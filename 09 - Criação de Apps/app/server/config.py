"""
Configuração central e autenticação dual-mode da Central de Retenção.

Padrão da skill databricks-apps: o MESMO código roda localmente (via profile do CLI) e dentro
do Databricks App (via service principal auto-injetado). A detecção é feita pela variável
DATABRICKS_APP_NAME, que só existe no ambiente do App.

Diferente da demo Cargill, este app NÃO usa Lakebase. Todo o dado vem do Unity Catalog, lido
por um SQL Warehouse via Statement Execution API (server/warehouse.py). A IA vem de dois
serving endpoints: o Supervisor (Ex.06) e um foundation model (leitura dos gráficos).

Gotchas resolvidos aqui:
  1. Token OAuth: `w.config.token` é None em auth U2M/OAuth. Use `w.config.authenticate()`
     que devolve o header 'Authorization: Bearer <token>' e extraia o token de lá.
  2. DATABRICKS_HOST dentro do App vem SEM esquema (só o hostname). Prefixe com https://.
"""
from __future__ import annotations

import json
import os
import subprocess
from functools import lru_cache
from typing import Optional

# -----------------------------------------------------------------------------
# Ambiente
# -----------------------------------------------------------------------------
IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))

DATABRICKS_PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE") or os.environ.get(
    "DATABRICKS_PROFILE", "mastertraining"
)

WORKSPACE_HOST_DEFAULT = "https://SEU_WORKSPACE_HOST"

# -----------------------------------------------------------------------------
# Recursos (parametrizáveis por env var; defaults = valores do workspace do treino).
# O SQL Warehouse e os dois serving endpoints são anexados como App resources — isso dá ao
# service principal do app CAN_USE / CAN_QUERY. Os GRANTs do Unity Catalog (SELECT/EXECUTE)
# são concedidos ao SP à parte.
# -----------------------------------------------------------------------------
WAREHOUSE_ID = os.environ.get("CR_WAREHOUSE_ID", "d788121d0edfbb7a")

# Schemas do Unity Catalog. Dados compartilhados (read-only) em churn; dados pessoais + as duas
# UC functions em cbettanim.
CATALOG = os.environ.get("CR_CATALOG", "dbacademy")
SCHEMA_CHURN = os.environ.get("CR_SCHEMA_CHURN", "churn")
SCHEMA_PESSOAL = os.environ.get("CR_SCHEMA_PESSOAL", "cbettanim")

# Supervisor (Ex.06) — roteia entre os Genies de Faturamento e Suporte.
SUPERVISOR_ENDPOINT = os.environ.get("CR_SUPERVISOR_ENDPOINT", "mas-3d713414-endpoint")
# Foundation model p/ a "leitura da IA" dos gráficos (✨ Explicar).
EXPLAIN_MODEL = os.environ.get("CR_EXPLAIN_MODEL", "databricks-claude-sonnet-4-5")


@lru_cache(maxsize=1)
def _workspace_client():
    """WorkspaceClient autenticado. Import preguiçoso do SDK."""
    from databricks.sdk import WorkspaceClient

    if IS_DATABRICKS_APP:
        return WorkspaceClient()
    return WorkspaceClient(profile=DATABRICKS_PROFILE)


def get_workspace_host() -> str:
    """Host do workspace COM esquema https://."""
    if IS_DATABRICKS_APP:
        host = os.environ.get("DATABRICKS_HOST", "")
        if host and not host.startswith("http"):
            host = f"https://{host}"
        return host or WORKSPACE_HOST_DEFAULT
    try:
        return _workspace_client().config.host or WORKSPACE_HOST_DEFAULT
    except Exception:
        return os.environ.get("CR_HOST", WORKSPACE_HOST_DEFAULT)


def get_workspace_token() -> Optional[str]:
    """Token de portador para as APIs REST (SQL Statements + serving endpoints).

    Gotcha: em auth OAuth/U2M o `config.token` é None. Recorre a `authenticate()`.
    """
    try:
        w = _workspace_client()
        if getattr(w.config, "token", None):
            return w.config.token
        headers = w.config.authenticate()
        if headers and "Authorization" in headers:
            return headers["Authorization"].replace("Bearer ", "")
    except Exception as exc:  # pragma: no cover
        print(f"[config] SDK token indisponível ({exc}); tentando CLI")
    if not IS_DATABRICKS_APP:
        try:
            out = subprocess.run(
                ["databricks", "auth", "token", "-p", DATABRICKS_PROFILE],
                capture_output=True, text=True, check=True,
            ).stdout
            return json.loads(out)["access_token"]
        except Exception as exc:
            print(f"[config] falha ao obter token via CLI: {exc}")
    return None


def summary() -> dict:
    """Diagnóstico legível do ambiente, exposto em /api/health."""
    return {
        "modo": "databricks_app" if IS_DATABRICKS_APP else "local",
        "profile": None if IS_DATABRICKS_APP else DATABRICKS_PROFILE,
        "host": get_workspace_host(),
        "warehouse_id": WAREHOUSE_ID,
        "catalog": CATALOG,
        "schema_churn": SCHEMA_CHURN,
        "schema_pessoal": SCHEMA_PESSOAL,
        "supervisor_endpoint": SUPERVISOR_ENDPOINT,
        "explain_model": EXPLAIN_MODEL,
    }
