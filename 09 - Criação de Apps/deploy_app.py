# Databricks notebook source
# MAGIC %md
# MAGIC # Exercício 9 — Central de Retenção (Databricks App)
# MAGIC
# MAGIC Este notebook **implanta o seu app** *Central de Retenção* — o painel que amarra todo o
# MAGIC treinamento: o **Cockpit** de churn (mapa + gráficos com leitura por IA), o **Assistente**
# MAGIC (o Supervisor do Ex. 6) e a **Retenção Personalizada** (as funções do Ex. 8).
# MAGIC
# MAGIC Você **não escreve código**: preencha os dois campos no topo e clique em **Run all**. O
# MAGIC notebook resolve o warehouse, cria o app, concede **automaticamente** tudo que o app precisa
# MAGIC (o app roda com um *service principal* próprio) e publica. No fim, ele imprime a **URL**.
# MAGIC
# MAGIC **Pré-requisitos** (no seu schema `dbacademy.<seu_db>`):
# MAGIC - **Ex. 6** — seu **Supervisor** publicado (endpoint `mas-...-endpoint`).
# MAGIC - **Ex. 7** — a tabela `churn_scores`.
# MAGIC - **Ex. 8** — as funções `gerar_email_retencao` (e `get_cliente_360`).
# MAGIC
# MAGIC > Rode em **Serverless** (ou qualquer cluster). O app em si roda em compute próprio do
# MAGIC > Databricks Apps — este notebook só o **provisiona e publica**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 1 — Preencha os campos e rode tudo
# MAGIC - **database**: o seu schema pessoal (o mesmo dos Ex. 7 e 8), ex.: `cbettanim`.
# MAGIC - **supervisor_endpoint**: o endpoint do seu Supervisor do Ex. 6, ex.: `mas-3d713414-endpoint`.
# MAGIC
# MAGIC (Os campos *catalog* e *warehouse* têm padrão e normalmente não precisam ser tocados.)

# COMMAND ----------

dbutils.widgets.text("database", "", "1. Seu database pessoal (ex.: cbettanim)")
dbutils.widgets.text("supervisor_endpoint", "", "2. Endpoint do Supervisor (Ex.06)")
dbutils.widgets.text("catalog", "dbacademy", "3. Catálogo (opcional)")
dbutils.widgets.text("warehouse", "", "4. Warehouse: nome ou id (opcional)")

DATABASE = dbutils.widgets.get("database").strip()
SUPERVISOR = dbutils.widgets.get("supervisor_endpoint").strip()
CATALOG = dbutils.widgets.get("catalog").strip() or "dbacademy"
WAREHOUSE_W = dbutils.widgets.get("warehouse").strip()

assert DATABASE, "Preencha o widget 'database' (seu schema pessoal, ex.: cbettanim)."
assert SUPERVISOR, "Preencha o widget 'supervisor_endpoint' (ex.: mas-...-endpoint do Ex. 6)."

import os, re, shutil, time, json
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Constantes do treino (não mudam entre alunos).
SCHEMA_CHURN = "churn"                              # base compartilhada (read-only)
EXPLAIN_MODEL = "databricks-claude-sonnet-4-5"      # leitura por IA dos gráficos (Cockpit)
EMAIL_LLM = "databricks-meta-llama-3-3-70b-instruct"  # usado DENTRO da UC function via ai_query
WAREHOUSE_NAME = "dbacademy_workshop_wh"            # criado no Setup (Ex. 00)

APP_NAME = "central-retencao-" + re.sub(r"[^a-z0-9-]", "-", DATABASE.lower()).strip("-")
ME = w.current_user.me().user_name

print("Aluno            :", ME)
print("App              :", APP_NAME)
print("Catálogo/schema  :", f"{CATALOG}.{DATABASE}  (+ {CATALOG}.{SCHEMA_CHURN} compartilhado)")
print("Supervisor       :", SUPERVISOR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 2 — Resolver o SQL Warehouse
# MAGIC O app lê os dados via warehouse. Resolvemos em cascata (o **ID não é portável**, então
# MAGIC resolvemos por **nome**): widget → `dbacademy_workshop_wh` → primeiro warehouse disponível.

# COMMAND ----------

def resolver_warehouse():
    whs = list(w.warehouses.list())
    if not whs:
        raise RuntimeError("Nenhum SQL Warehouse encontrado no workspace. Rode o Setup (Ex. 00).")
    # 1) override explícito pelo widget (id ou nome)
    if WAREHOUSE_W:
        m = next((x for x in whs if x.id == WAREHOUSE_W or x.name == WAREHOUSE_W), None)
        if m:
            return m.id, m.name, "widget"
        print(f"  aviso: warehouse '{WAREHOUSE_W}' do widget não encontrado; caindo para a cascata.")
    # 2) por nome, o do Setup
    m = next((x for x in whs if x.name == WAREHOUSE_NAME), None)
    if m:
        return m.id, m.name, f"nome '{WAREHOUSE_NAME}'"
    # 3) fallback: um em execução, senão o primeiro
    m = next((x for x in whs if str(getattr(x, "state", "")).upper().endswith("RUNNING")), whs[0])
    return m.id, m.name, "fallback (primeiro disponível)"

WH_ID, WH_NAME, WH_VIA = resolver_warehouse()
print(f"Warehouse: '{WH_NAME}' (id {WH_ID}) — resolvido por {WH_VIA}.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 3 — Preparar o código-fonte do app (com a SUA configuração)
# MAGIC Copiamos o `app/` (que veio junto deste notebook) para uma pasta sua no workspace e
# MAGIC gravamos os seus valores no `app.yaml`. O app é **inteiramente dirigido por config**
# MAGIC (`server/config.py` lê as variáveis `CR_*`) — nada é escrito no código.

# COMMAND ----------

# Caminho deste notebook -> pasta do módulo -> app/ ao lado.
nb_path = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
)
def fuse(p):  # /Workspace é o mount FUSE dos Workspace Files
    return p if p.startswith("/Workspace/") else "/Workspace" + p

mod_dir = fuse(os.path.dirname(nb_path))
SRC_APP = os.path.join(mod_dir, "app")
assert os.path.isdir(SRC_APP), (
    f"Não achei a pasta 'app/' ao lado do notebook ({SRC_APP}). "
    "Importe a PASTA inteira '09 - Criação de Apps' (via Git folder), não só o notebook."
)

# Pasta de publicação (por aluno; recriada a cada execução para permitir re-deploy limpo).
STAGE = f"/Workspace/Users/{ME}/.central-retencao/{APP_NAME}"
if os.path.exists(STAGE):
    shutil.rmtree(STAGE)
shutil.copytree(SRC_APP, STAGE)

# Reescreve o app.yaml com a config do aluno (determinístico).
APP_YAML = f"""command:
  - "uvicorn"
  - "app:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "8000"

env:
  - name: CR_WAREHOUSE_ID
    value: "{WH_ID}"
  - name: CR_SUPERVISOR_ENDPOINT
    value: "{SUPERVISOR}"
  - name: CR_EXPLAIN_MODEL
    value: "{EXPLAIN_MODEL}"
  - name: CR_CATALOG
    value: "{CATALOG}"
  - name: CR_SCHEMA_CHURN
    value: "{SCHEMA_CHURN}"
  - name: CR_SCHEMA_PESSOAL
    value: "{DATABASE}"
"""
with open(os.path.join(STAGE, "app.yaml"), "w") as f:
    f.write(APP_YAML)

print("Código preparado em:", STAGE)
print(APP_YAML)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 4 — Criar o app (compute próprio + service principal)
# MAGIC Se o app já existir (re-execução), seguimos em frente. Esperamos o compute ficar **ACTIVE**.

# COMMAND ----------

def api(method, path, body=None):
    return w.api_client.do(method, path, body=body)

# cria (ou reaproveita) o app
try:
    api("GET", f"/api/2.0/apps/{APP_NAME}")
    print(f"App '{APP_NAME}' já existe — reaproveitando.")
except Exception:
    api("POST", "/api/2.0/apps", body={
        "name": APP_NAME,
        "description": "Central de Retenção — Master Training (churn): Cockpit + Assistente + Retenção.",
    })
    print(f"App '{APP_NAME}' criado.")

# espera o compute ficar ACTIVE
for _ in range(60):
    app = api("GET", f"/api/2.0/apps/{APP_NAME}")
    st = (app.get("compute_status") or {}).get("state")
    if st == "ACTIVE":
        break
    if st in ("ERROR", "STOPPED"):
        # tenta iniciar
        try: api("POST", f"/api/2.0/apps/{APP_NAME}/start")
        except Exception: pass
    time.sleep(10)

SP = app.get("service_principal_client_id")
APP_URL = app.get("url")
print(f"compute: {(app.get('compute_status') or {}).get('state')}  |  SP: {SP}")
print("URL     :", APP_URL)
assert SP, "Service principal do app ainda não disponível; re-execute esta célula."

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 5 — Conceder ao app TUDO que ele precisa (automático)
# MAGIC O app roda como o *service principal* acima — não como você. Então concedemos a ELE:
# MAGIC recursos do app (warehouse + endpoints), permissões de Unity Catalog e **CAN_RUN nos Genies
# MAGIC que o Supervisor usa** — estes são **descobertos dinamicamente** do próprio Supervisor
# MAGIC (nunca fixos no código: um Genie errado no Supervisor foi exatamente o que já quebrou o app).

# COMMAND ----------

concedido = []

# 5a) Recursos do app: warehouse (CAN_USE) + 3 serving endpoints (CAN_QUERY).
#     O endpoint de e-mail (llama) é necessário porque a UC function gerar_email_retencao
#     chama ai_query(...) internamente com a identidade do app.
recursos = [
    {"name": "sql-warehouse", "description": "Leitura do Unity Catalog",
     "sql_warehouse": {"id": WH_ID, "permission": "CAN_USE"}},
    {"name": "supervisor-endpoint", "description": "Supervisor (Ex.06)",
     "serving_endpoint": {"name": SUPERVISOR, "permission": "CAN_QUERY"}},
    {"name": "explain-endpoint", "description": "Leitura por IA dos gráficos",
     "serving_endpoint": {"name": EXPLAIN_MODEL, "permission": "CAN_QUERY"}},
    {"name": "email-llm-endpoint", "description": "LLM usado pela UC function de e-mail",
     "serving_endpoint": {"name": EMAIL_LLM, "permission": "CAN_QUERY"}},
]
try:
    api("PATCH", f"/api/2.0/apps/{APP_NAME}",
        body={"name": APP_NAME, "resources": recursos})
    concedido.append(f"recursos do app: warehouse CAN_USE + {SUPERVISOR}/{EXPLAIN_MODEL}/{EMAIL_LLM} CAN_QUERY")
except Exception as e:
    print("  ERRO ao anexar recursos:", e)

# 5b) Unity Catalog: USE CATALOG, USE SCHEMA + SELECT (churn e schema pessoal), EXECUTE nas funções.
def grant(stmt, rotulo):
    try:
        r = w.statement_execution.execute_statement(
            warehouse_id=WH_ID, statement=stmt, wait_timeout="30s")
        estado = getattr(r.status, "state", None)
        estado = getattr(estado, "value", estado)
        if str(estado) == "SUCCEEDED":
            concedido.append(rotulo); print("  OK:", rotulo)
        else:
            msg = getattr(getattr(r.status, "error", None), "message", "")
            print(f"  FALHOU: {rotulo} -> {estado} {msg}")
    except Exception as e:
        print(f"  FALHOU: {rotulo} -> {e}")

grant(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{SP}`", f"USE CATALOG {CATALOG}")
grant(f"GRANT USE SCHEMA, SELECT ON SCHEMA {CATALOG}.{SCHEMA_CHURN} TO `{SP}`", f"USE+SELECT {CATALOG}.{SCHEMA_CHURN}")
grant(f"GRANT USE SCHEMA, SELECT ON SCHEMA {CATALOG}.{DATABASE} TO `{SP}`", f"USE+SELECT {CATALOG}.{DATABASE}")
grant(f"GRANT EXECUTE ON FUNCTION {CATALOG}.{DATABASE}.gerar_email_retencao TO `{SP}`", "EXECUTE gerar_email_retencao")
grant(f"GRANT EXECUTE ON FUNCTION {CATALOG}.{DATABASE}.get_cliente_360 TO `{SP}`", "EXECUTE get_cliente_360")

# 5c) Genies do Supervisor — descobertos DINAMICAMENTE (endpoint -> agente -> tools -> genie_space.id).
def genies_do_supervisor(endpoint_name):
    ags = (api("GET", "/api/2.1/supervisor-agents").get("supervisor_agents")) or []
    ag = next((a for a in ags if a.get("endpoint_name") == endpoint_name), None)
    if not ag:
        print(f"  aviso: nenhum supervisor-agent com endpoint '{endpoint_name}'. Genies não concedidos.")
        return []
    tools = (api("GET", f"/api/2.1/supervisor-agents/{ag['supervisor_agent_id']}/tools").get("tools")) or []
    ids = [t["genie_space"]["id"] for t in tools
           if t.get("tool_type") == "genie_space" and t.get("genie_space", {}).get("id")]
    return ids

for gid in genies_do_supervisor(SUPERVISOR):
    try:
        api("PATCH", f"/api/2.0/permissions/genie/{gid}",
            body={"access_control_list": [{"service_principal_name": SP, "permission_level": "CAN_RUN"}]})
        concedido.append(f"CAN_RUN no Genie {gid}"); print("  OK: CAN_RUN no Genie", gid)
    except Exception as e:
        print(f"  FALHOU: CAN_RUN no Genie {gid} -> {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 6 — Publicar (deploy)

# COMMAND ----------

dep = api("POST", f"/api/2.0/apps/{APP_NAME}/deployments",
          body={"source_code_path": STAGE, "mode": "SNAPSHOT"})
dep_id = dep.get("deployment_id")
print("deployment_id:", dep_id, "— aguardando...")
estado = None
for _ in range(60):
    d = api("GET", f"/api/2.0/apps/{APP_NAME}/deployments/{dep_id}")
    estado = (d.get("status") or {}).get("state")
    if estado in ("SUCCEEDED", "FAILED", "STOPPED"):
        break
    time.sleep(10)
print("deploy:", estado, "-", (d.get("status") or {}).get("message"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pronto! 🎉

# COMMAND ----------

print("=" * 66)
print("  CENTRAL DE RETENÇÃO — publicada")
print("=" * 66)
print("  App URL :", APP_URL)
print("  Deploy  :", estado)
print("  SP      :", SP)
print("  Concedido automaticamente:")
for c in concedido:
    print("    -", c)
print("=" * 66)
print("  Abra a URL acima. Cockpit (mapa + gráficos ✨), Assistente (Supervisor)")
print("  e Retenção Personalizada (e-mail via UC function) já devem responder.")
displayHTML(f'<h3>Central de Retenção</h3><a href="{APP_URL}" target="_blank">{APP_URL}</a>')
