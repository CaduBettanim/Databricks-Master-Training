"""Aba 2 — Assistente. Encaminha a pergunta ao Supervisor (Ex.06) e devolve o texto."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .. import llm

router = APIRouter()


class PerguntaReq(BaseModel):
    pergunta: str


@router.post("/assistente/perguntar")
async def perguntar(req: PerguntaReq):
    pergunta = (req.pergunta or "").strip()
    if not pergunta:
        return {"resposta": "Digite uma pergunta.", "ok": False}
    resposta = await llm.supervisor_ask(pergunta)
    if not resposta:
        return {
            "resposta": "O Supervisor não respondeu agora (pode estar em cold start). Tente de novo.",
            "ok": False,
        }
    return {"resposta": resposta, "ok": True}
