"""
Aba 3 — Retenção Personalizada.

  - /retencao/lista: os 12 clientes mais propensos a churn (faixa Alto).
  - /retencao/email: chama a UC function gerar_email_retencao(id) — a regra de negócio da oferta
    é decidida em SQL (CASE) dentro da função; a IA só REDIGE o texto. 100% verificável.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from .. import config, warehouse
from ..warehouse import num

router = APIRouter()

CH = f"{config.CATALOG}.{config.SCHEMA_CHURN}"
PE = f"{config.CATALOG}.{config.SCHEMA_PESSOAL}"


def _user_token(request: Request):
    return config.token_for_request(request.headers.get(config.USER_TOKEN_HEADER))


@router.get("/retencao/lista")
async def lista(request: Request):
    rows = await warehouse.query(f"""
        SELECT s.id_cliente, c.nome_cliente, c.cidade, c.uf,
               floor(datediff(current_date(), c.data_cadastro)/365) anos,
               s.nome_plano, round(s.prob_churn,3) prob, s.fator_principal
        FROM {PE}.churn_scores s JOIN {CH}.dim_cliente c USING(id_cliente)
        WHERE s.faixa_risco='Alto'
        ORDER BY s.prob_churn DESC
        LIMIT 12
    """, _user_token(request))
    clientes = [
        {
            "id": r.get("id_cliente"),
            "nome": r.get("nome_cliente"),
            "cidade": r.get("cidade"),
            "uf": r.get("uf"),
            "anos": int(num(r.get("anos"))),
            "plano": r.get("nome_plano"),
            "prob": round(num(r.get("prob")) * 100),
            "fator": r.get("fator_principal"),
        }
        for r in rows
    ]
    return {"clientes": clientes}


class EmailReq(BaseModel):
    id_cliente: str


def _sanitiza_id(raw: str) -> str:
    """Só letras/dígitos maiúsculos — evita injeção na string literal da UC function."""
    return "".join(ch for ch in (raw or "").strip().upper() if ch.isalnum())[:16]


@router.post("/retencao/email")
async def email(req: EmailReq, request: Request):
    cid = _sanitiza_id(req.id_cliente)
    if not cid:
        return {"ok": False, "erro": "ID inválido."}
    rows = await warehouse.query(
        f"SELECT email FROM {PE}.gerar_email_retencao('{cid}')", _user_token(request)
    )
    if not rows or not rows[0].get("email"):
        return {"ok": False, "erro": "ID não encontrado na base de risco."}
    return {"ok": True, "id_cliente": cid, "email": rows[0]["email"]}
