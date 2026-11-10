"""Aba 2 — Assistente. Encaminha a pergunta ao Supervisor em código (server/supervisor.py), que
escolhe entre os Genies de Faturamento e Suporte do Ex.07, e devolve a resposta + a rota."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from .. import config, supervisor

router = APIRouter()


class PerguntaReq(BaseModel):
    pergunta: str


@router.post("/assistente/perguntar")
async def perguntar(req: PerguntaReq, request: Request):
    pergunta = (req.pergunta or "").strip()
    if not pergunta:
        return {"resposta": "Digite uma pergunta.", "ok": False, "rota": [], "consultas": []}
    if not (config.GENIE_FATURAMENTO_ID and config.GENIE_SUPORTE_ID):
        return {"resposta": "Os Genies do Ex. 7 não estão configurados neste app. "
                            "Rode de novo o notebook deploy_app.py.",
                "ok": False, "rota": [], "consultas": []}
    token = config.token_for_request(request.headers.get(config.USER_TOKEN_HEADER))
    r = await supervisor.responder(pergunta, token)
    if not r.get("ok"):
        r["resposta"] = ("O Supervisor não conseguiu responder agora. Se é o seu primeiro acesso, "
                         "confira se você autorizou o app (Authorize); se já autorizou, tente de "
                         "novo em instantes (o warehouse do Genie pode estar iniciando).")
    return r
