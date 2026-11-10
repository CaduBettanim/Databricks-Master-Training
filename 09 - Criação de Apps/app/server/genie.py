"""
Cliente da Genie Conversation API: as "ferramentas" do Supervisor (server/supervisor.py).

Cada especialista é um Genie Agent que o aluno criou no Ex. 7 (Faturamento e Suporte). Perguntar
a um Genie são 3 chamadas REST, sempre com o TOKEN DO USUÁRIO logado (OBO, escopo
`dashboards.genie`), então o Genie roda o SQL com a identidade de quem perguntou:

  1. POST /api/2.0/genie/spaces/{space}/start-conversation   {"content": pergunta}
  2. GET  .../conversations/{c}/messages/{m}                 até o status ficar COMPLETED
     (nesse meio tempo o Genie escreve o SQL e o executa no warehouse do space)
  3. GET  .../messages/{m}/attachments/{a}/query-result      as linhas do resultado

Cada pergunta abre uma conversa nova (sem memória entre perguntas), como no Ex. 7.
Degrade gracioso: qualquer falha volta como {"ok": False, "erro": ...}, nunca exceção.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

import aiohttp

from . import config
from .llm import _connector

# Status em que o Genie terminou (com ou sem sucesso).
TERMINAIS = {"COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"}
# Quantas linhas do resultado repassamos ao Supervisor (o suficiente para ele sintetizar).
MAX_LINHAS = 20


async def _get(sess: aiohttp.ClientSession, url: str, headers: dict) -> dict:
    async with sess.get(url, headers=headers) as rr:
        txt = await rr.text()
        if rr.status != 200:
            raise RuntimeError(f"HTTP {rr.status}: {txt[:300]}")
        return json.loads(txt)


async def perguntar(space_id: str, pergunta: str, token: Optional[str],
                    timeout_s: int = 150) -> dict:
    """Faz UMA pergunta a um Genie Agent (como o usuário) e devolve:
    {ok, status, texto, sql, descricao, colunas, linhas, total_linhas, erro}."""
    if not token:
        return {"ok": False, "erro": "sem token de usuário (OBO)"}
    if not space_id:
        return {"ok": False, "erro": "Genie não configurado no app"}

    host = config.get_workspace_host()
    base = f"{host}/api/2.0/genie/spaces/{space_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    t0 = time.monotonic()
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s + 30)
        async with aiohttp.ClientSession(timeout=timeout, connector=_connector()) as sess:
            # 1. Abre a conversa com a pergunta.
            async with sess.post(f"{base}/start-conversation", json={"content": pergunta},
                                 headers=headers) as rr:
                txt = await rr.text()
                if rr.status != 200:
                    return {"ok": False, "erro": f"HTTP {rr.status}: {txt[:300]}"}
                ini = json.loads(txt)
            conv = ini.get("conversation_id") or (ini.get("conversation") or {}).get("id")
            msg_id = ini.get("message_id") or (ini.get("message") or {}).get("id")
            url_msg = f"{base}/conversations/{conv}/messages/{msg_id}"

            # 2. Espera o Genie terminar (escrever e executar o SQL).
            msg: dict = {}
            espera = 1.5
            while time.monotonic() - t0 < timeout_s:
                msg = await _get(sess, url_msg, headers)
                if msg.get("status") in TERMINAIS:
                    break
                await asyncio.sleep(espera)
                espera = min(espera + 0.5, 3.0)
            status = msg.get("status") or "TIMEOUT"
            if status != "COMPLETED":
                erro = (msg.get("error") or {}).get("error") if isinstance(msg.get("error"), dict) \
                    else msg.get("error")
                return {"ok": False, "status": status, "erro": str(erro or status)[:300]}

            # 3. Texto do Genie + SQL + linhas do resultado.
            out = {"ok": True, "status": status, "texto": None, "sql": None, "descricao": None,
                   "colunas": [], "linhas": [], "total_linhas": 0}
            for att in msg.get("attachments") or []:
                if att.get("text"):
                    out["texto"] = (att["text"] or {}).get("content")
                q = att.get("query")
                if q and not out["sql"]:
                    out["sql"] = q.get("query")
                    out["descricao"] = q.get("description")
                    att_id = att.get("attachment_id") or att.get("id")
                    try:
                        res = await _get(sess, f"{url_msg}/attachments/{att_id}/query-result",
                                         headers)
                        sr = res.get("statement_response") or {}
                        manifest = sr.get("manifest") or {}
                        out["colunas"] = [c.get("name") for c in
                                          (manifest.get("schema") or {}).get("columns") or []]
                        dados = (sr.get("result") or {}).get("data_array") or []
                        out["linhas"] = dados[:MAX_LINHAS]
                        out["total_linhas"] = manifest.get("total_row_count", len(dados))
                    except Exception as exc:  # resultado é opcional: o texto do Genie já ajuda
                        print(f"[genie] sem query-result ({space_id}): {exc}")
            return out
    except Exception as exc:
        print(f"[genie] indisponível ({space_id}): {exc}")
        return {"ok": False, "erro": str(exc)[:300]}
