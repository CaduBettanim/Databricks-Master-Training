"""
Leitura do Unity Catalog via SQL Statement Execution API (warehouse serverless).

Toda a camada de dados do app (cockpit, lista de risco, e-mail de retenção via UC function)
passa por aqui. Degrade gracioso: erro -> lista vazia, e o front mostra estado vazio.
"""
from __future__ import annotations

import json

import aiohttp

from . import config


async def query(sql: str) -> list[dict]:
    """Roda um SELECT no warehouse e devolve lista de dicts (colunas nomeadas)."""
    host = config.get_workspace_host()
    token = config.get_workspace_token()
    url = f"{host}/api/2.0/sql/statements"
    payload = {
        "warehouse_id": config.WAREHOUSE_ID,
        "statement": sql,
        "wait_timeout": "50s",
        "format": "JSON_ARRAY",
        "disposition": "INLINE",
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as sess:
            async with sess.post(url, json=payload, headers=headers) as resp:
                data = json.loads(await resp.text())
                status = (data.get("status") or {}).get("state")
                if status != "SUCCEEDED":
                    msg = (data.get("status") or {}).get("error", {}).get("message", "")
                    print(f"[warehouse] statement {status}: {msg[:300]}")
                    return []
                result = data.get("result", {})
                schema_cols = (
                    data.get("manifest", {}).get("schema", {}).get("columns", [])
                )
                names = [c["name"] for c in schema_cols]
                rows = result.get("data_array") or []
                return [dict(zip(names, r)) for r in rows]
    except Exception as exc:
        print(f"[warehouse] erro: {exc}")
        return []


def num(v) -> float:
    """O SQL Statement API (JSON_ARRAY) devolve TODA coluna como string. Converte p/ float."""
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0
