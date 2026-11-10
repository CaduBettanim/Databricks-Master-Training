"""
Supervisor em código: o agente multi-agent do Assistente (aba 💬).

Ele recebe a pergunta do usuário, decide qual especialista deve responder, consulta esse
especialista e sintetiza a resposta. Os especialistas são os dois Genie Agents que o aluno criou
no Ex. 7 (Faturamento e Suporte). O "cérebro" é o model service do aluno no Unity Gateway
(CR_GATEWAY_MODEL), chamado com TOOL CALLING: cada especialista é uma ferramenta.

O laço do agente (padrão "tool calling"):
  1. Manda ao modelo as INSTRUÇÕES (abaixo), a pergunta e as duas ferramentas com a descrição
     de cada especialista. O modelo devolve qual ferramenta chamar e com qual pergunta.
  2. O app executa a ferramenta: pergunta ao Genie (server/genie.py) e devolve ao modelo o texto,
     o SQL e as linhas que o Genie produziu. Se o modelo pedir os dois especialistas, eles rodam
     em paralelo.
  3. Repete até o modelo responder sem pedir ferramenta (no máximo MAX_PASSOS rodadas). Essa
     última mensagem é a resposta final ao usuário.

Tudo roda com o TOKEN DO USUÁRIO (OBO): o modelo pelo escopo `ai-gateway` e os Genies pelo
escopo `dashboards.genie`. Nenhuma permissão é concedida ao service principal do app.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Optional

from . import config, genie, llm

# Instruções de coordenação: a "personalidade" do Supervisor.
INSTRUCOES = (
    "Você coordena dois especialistas: um de Faturamento (receita, inadimplência, faturas, "
    "planos) e um de Suporte (tickets, CSAT, NPS, canais). Encaminhe cada pergunta ao "
    "especialista adequado, combine as respostas quando a pergunta envolver os dois temas e "
    "responda sempre em português.\n"
    "Regras: use SEMPRE uma ferramenta para obter dados e nunca invente números. Passe a cada "
    "especialista só a parte da pergunta que é do domínio dele, completa e em português (numa "
    "pergunta sobre os dois temas, cada um recebe a sua parte). Na resposta final, diga em uma frase qual "
    "especialista respondeu e traga os números principais, com valores em reais no formato "
    "brasileiro (ex.: R$ 383.335,40). Escreva em texto simples, sem markdown (sem asteriscos, "
    "sem tabelas); listas curtas com hífen são permitidas."
)

# Os especialistas: cada um vira uma ferramenta. A descrição é o que o modelo lê para decidir.
ESPECIALISTAS = {
    "consultar_faturamento": {
        "nome": "Faturamento",
        "space_id": config.GENIE_FATURAMENTO_ID,
        "descricao": (
            "Especialista em faturamento e cobrança. Responde sobre receita, inadimplência, "
            "faturas pagas e não pagas, e valores por plano e por segmento."
        ),
    },
    "consultar_suporte": {
        "nome": "Suporte",
        "space_id": config.GENIE_SUPORTE_ID,
        "descricao": (
            "Especialista em atendimento e satisfação do cliente. Responde sobre tickets de "
            "suporte, CSAT, NPS, canais e categorias, inclusive por ano fiscal."
        ),
    },
}

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": nome,
            "description": esp["descricao"],
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {
                        "type": "string",
                        "description": "A parte da pergunta que cabe a este especialista, completa e em português.",
                    }
                },
                "required": ["pergunta"],
            },
        },
    }
    for nome, esp in ESPECIALISTAS.items()
]

MAX_PASSOS = 4


def _nome_ferramenta(bruto) -> str:
    """Nome da ferramenta sem lixo: o gpt-oss às vezes vaza tokens do formato dele no nome
    (ex.: 'consultar_suporte<|channel|>commentary')."""
    return re.split(r"<\|", str(bruto or ""))[0].strip()


def _rota(consultas: list[dict]) -> list[str]:
    """Especialistas válidos acionados, na ordem, sem repetição."""
    validos = {e["nome"] for e in ESPECIALISTAS.values()}
    return list(dict.fromkeys(c["especialista"] for c in consultas if c["especialista"] in validos))


async def _executar(chamada: dict, token: Optional[str]) -> tuple[str, dict]:
    """Executa UMA chamada de ferramenta. Devolve (conteúdo para o modelo, registro para a UI)."""
    fn = chamada.get("function") or {}
    esp = ESPECIALISTAS.get(_nome_ferramenta(fn.get("name")))
    args = fn.get("arguments") or {}
    if isinstance(args, str):  # o padrão OpenAI manda os argumentos como texto JSON
        try:
            args = json.loads(args or "{}")
        except json.JSONDecodeError:
            args = {}
    pergunta = str((args if isinstance(args, dict) else {}).get("pergunta") or "").strip()
    if not esp:
        return json.dumps({"erro": f"ferramenta desconhecida: {fn.get('name')}"}), {
            "especialista": str(fn.get("name")), "pergunta": pergunta, "ok": False}
    if not pergunta:
        return json.dumps({"erro": "informe a pergunta"}), {
            "especialista": esp["nome"], "pergunta": "", "ok": False}

    r = await genie.perguntar(esp["space_id"], pergunta, token)
    registro = {
        "especialista": esp["nome"], "pergunta": pergunta, "ok": r.get("ok", False),
        "sql": r.get("sql"), "texto": r.get("texto"), "linhas": r.get("total_linhas", 0),
    }
    if not r.get("ok"):
        return json.dumps({"especialista": esp["nome"], "erro": r.get("erro")},
                          ensure_ascii=False), registro
    para_modelo = {
        "especialista": esp["nome"],
        "resposta_do_genie": r.get("texto"),
        "descricao_da_consulta": r.get("descricao"),
        "sql": r.get("sql"),
        "colunas": r.get("colunas"),
        "linhas": r.get("linhas"),
        "total_linhas": r.get("total_linhas"),
    }
    return json.dumps(para_modelo, ensure_ascii=False, default=str), registro


async def responder(pergunta: str, token: Optional[str]) -> dict:
    """Roda o laço do agente. Devolve {ok, resposta, rota, consultas}."""
    t0 = time.monotonic()
    mensagens: list[dict] = [
        {"role": "system", "content": INSTRUCOES},
        {"role": "user", "content": pergunta},
    ]
    consultas: list[dict] = []

    for passo in range(MAX_PASSOS):
        ultimo = passo == MAX_PASSOS - 1
        # 1ª rodada: o modelo é obrigado a escolher um especialista (nunca responde "de cabeça").
        # Última rodada: sem ferramentas, para garantir que ele feche a resposta.
        escolha = "required" if passo == 0 else ("none" if ultimo else "auto")
        resp = await llm.chat_completion(mensagens, token, tools=FERRAMENTAS,
                                         tool_choice=escolha, max_tokens=2000, temperature=0.1,
                                         timeout_s=90)
        if not resp:  # o modelo não respondeu (o motivo já foi logado por llm.chat_completion)
            print(f"[supervisor] modelo indisponível no passo {passo + 1} "
                  f"(t={time.monotonic() - t0:.1f}s) pergunta={pergunta[:80]!r}")
            return {"ok": False, "resposta": None,
                    "rota": _rota(consultas),
                    "consultas": consultas}
        msg = (resp.get("choices") or [{}])[0].get("message") or {}
        chamadas = msg.get("tool_calls") or []
        if not chamadas:
            texto = llm.texto_do_content(msg.get("content")).strip()
            rota = _rota(consultas)
            print(f"[supervisor] rota={rota} passos={passo + 1} "
                  f"t={time.monotonic() - t0:.1f}s pergunta={pergunta[:80]!r}")
            return {"ok": bool(texto), "resposta": texto, "rota": rota, "consultas": consultas}

        mensagens.append({"role": "assistant",
                          "content": llm.texto_do_content(msg.get("content")),
                          "tool_calls": chamadas})
        resultados = await asyncio.gather(*(_executar(c, token) for c in chamadas))
        for chamada, (conteudo, registro) in zip(chamadas, resultados):
            consultas.append(registro)
            mensagens.append({"role": "tool", "tool_call_id": chamada.get("id"),
                              "content": conteudo})

    print(f"[supervisor] sem resposta final após {MAX_PASSOS} passos "
          f"(t={time.monotonic() - t0:.1f}s) pergunta={pergunta[:80]!r}")
    return {"ok": False, "resposta": None,
            "rota": _rota(consultas),
            "consultas": consultas}
