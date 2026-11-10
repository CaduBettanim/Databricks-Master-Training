"""
Camada de IA do app. Tudo é chamado com o TOKEN DO USUÁRIO logado (OBO), passado pelas rotas.

  chat_completion(): uma chamada de chat (formato OpenAI) ao model service do aluno no Unity
     Gateway (CR_GATEWAY_MODEL, via /ai-gateway/mlflow/v1/chat/completions). Aceita `tools`
     (tool calling), que é o que o Supervisor em código (server/supervisor.py) usa para escolher
     entre os Genies de Faturamento e Suporte. Sem CR_GATEWAY_MODEL, cai para o foundation model
     CR_EXPLAIN_MODEL via /serving-endpoints/<modelo>/invocations.

  explicar_grafico() e redigir_email_retencao(): leitura curta de um gráfico do Cockpit e o
     e-mail de retenção, ambos por cima de chat_completion().

Degrade gracioso: qualquer falha devolve None / texto de fallback.
"""
from __future__ import annotations

import json
import os
import ssl
from functools import lru_cache
from typing import Optional

import aiohttp

from . import config


@lru_cache(maxsize=1)
def _ssl_context() -> Optional[ssl.SSLContext]:
    for caminho in (os.environ.get("SSL_CERT_FILE"), "/etc/ssl/cert.pem"):
        if caminho and os.path.exists(caminho):
            try:
                return ssl.create_default_context(cafile=caminho)
            except Exception:
                pass
    return None


def _connector():
    ctx = _ssl_context()
    return aiohttp.TCPConnector(ssl=ctx) if ctx else None


def texto_do_content(content) -> str:
    """Extrai texto de um content que pode ser string ou lista de blocos. Blocos de raciocínio
    (modelos como o gpt-oss devolvem {"type": "reasoning", ...}) ficam de fora."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for bloco in content:
            if isinstance(bloco, dict) and bloco.get("type") != "reasoning":
                partes.append(bloco.get("text") or bloco.get("content") or "")
        return "".join(partes)
    return str(content or "")


# -----------------------------------------------------------------------------
# Chat completions (Unity Gateway ou foundation model)
# -----------------------------------------------------------------------------
async def chat_completion(messages: list[dict], token: Optional[str], *,
                          tools: Optional[list] = None, tool_choice: Optional[str] = None,
                          max_tokens: int = 600, temperature: float = 0.3,
                          timeout_s: int = 45) -> Optional[dict]:
    """Uma chamada de chat. Devolve o JSON da resposta (com `choices`) ou None se falhar."""
    if not token:
        return None
    host = config.get_workspace_host()
    payload: dict = {"messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if tools:
        payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
    if config.GATEWAY_MODEL:
        # Unity Gateway: API unificada (OpenAI-compatível); o model service vai no campo `model`.
        url = f"{host}/ai-gateway/mlflow/v1/chat/completions"
        payload["model"] = config.GATEWAY_MODEL
    else:
        url = f"{host}/serving-endpoints/{config.EXPLAIN_MODEL}/invocations"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s)
        async with aiohttp.ClientSession(timeout=timeout, connector=_connector()) as sess:
            async with sess.post(url, json=payload, headers=headers) as rr:
                txt = await rr.text()
                if rr.status != 200:
                    print(f"[chat] HTTP {rr.status}: {txt[:300]}")
                    return None
                return json.loads(txt)
    except Exception as exc:
        print(f"[chat] indisponível: {exc}")
        return None


async def _chat(system: str, user: str, token: Optional[str], max_tokens: int = 220,
                timeout_s: int = 45) -> Optional[str]:
    """Atalho: system + user -> texto da resposta."""
    d = await chat_completion(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        token, max_tokens=max_tokens, timeout_s=timeout_s,
    )
    try:
        return texto_do_content(d["choices"][0]["message"]["content"]).strip() if d else None
    except (KeyError, IndexError, TypeError):
        return None


async def explicar_grafico(chart: str, regiao: str, dados: dict, token: Optional[str]) -> str:
    """Leitura em 1-2 frases PT-BR de um gráfico do cockpit, a partir dos dados atuais."""
    onde = "no Brasil (todas as regiões)" if regiao == "Brasil" else f"na região {regiao}"
    contexto = {
        "plano": "Churn (%) por plano de assinatura",
        "faixa": "Distribuição de clientes por faixa de risco de churn (Alto/Médio/Baixo)",
        "meses": "Cancelamentos de assinatura por mês (set/24 a ago/25)",
        "seg": "Churn (%) por segmento de cliente (Consumidor/PME/Corporativo)",
    }.get(chart, chart)
    system = (
        "Você é um analista de retenção (Customer Success) de uma empresa de telecom. "
        "Explique gráficos de churn para um gerente, em português do Brasil, de forma direta "
        "e acionável. Responda em NO MÁXIMO 2 frases curtas. Não use markdown nem listas. "
        "Cite os números mais relevantes e uma recomendação prática."
    )
    user = (
        f"Gráfico: {contexto}, {onde}.\n"
        f"Dados (JSON): {json.dumps(dados, ensure_ascii=False)}\n"
        "Escreva a leitura do gráfico."
    )
    # Folga de tokens: modelos de raciocínio (ex.: gpt-oss) gastam parte do limite pensando.
    resp = await _chat(system, user, token, max_tokens=600)
    return resp or "Não foi possível gerar a leitura da IA agora. Tente novamente."


async def redigir_email_retencao(perfil: dict, token: Optional[str]) -> Optional[str]:
    """Redige o e-mail de retenção. As OFERTAS já vêm calculadas pela UC function
    get_cliente_360 (regra de negócio em SQL); a IA só escreve o texto."""
    system = (
        "Você é um especialista em retenção de clientes de uma empresa de assinatura. "
        "Redija um e-mail profissional e empático em português do Brasil para convencer o "
        "cliente a permanecer. Ofereça EXATAMENTE as ofertas informadas, sem inventar outras "
        "e sem mudar valores. Não cite o setor da empresa. Comece pela saudação (não inclua "
        "linha de assunto) e escreva em texto simples, sem markdown: sem asteriscos, sem listas."
    )
    user = (
        f"Dados: Nome: {perfil.get('nome_cliente')}, Cidade: {perfil.get('cidade')}, "
        f"Anos de casa: {perfil.get('anos_de_casa')}. "
        f"Ofertas: (a) desconto de {perfil.get('desconto')} na mensalidade; "
        f"(b) {perfil.get('oferta_internet')}; (c) {perfil.get('oferta_fator')}. "
        "Cite o nome, a cidade e os anos de casa e mencione as três ofertas de forma natural."
    )
    return await _chat(system, user, token, max_tokens=1500, timeout_s=120)


async def ping() -> dict:
    return {
        "supervisor": "em código (server/supervisor.py)",
        "genie_faturamento": config.GENIE_FATURAMENTO_ID or None,
        "genie_suporte": config.GENIE_SUPORTE_ID or None,
        "explain_model": config.EXPLAIN_MODEL,
        "gateway_model": config.GATEWAY_MODEL or None,
    }
