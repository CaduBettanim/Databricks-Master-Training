# Databricks notebook source
# MAGIC %md
# MAGIC # Exercício 9 — Central de Retenção (Databricks App)
# MAGIC
# MAGIC Este notebook **implanta o seu app** *Central de Retenção* — o painel que amarra todo o
# MAGIC treinamento: o **Cockpit** de churn (mapa + gráficos com leitura por IA), o **Assistente**
# MAGIC (um **Supervisor em código** que orquestra os seus Genies do Ex. 7) e a **Retenção
# MAGIC Personalizada** (a função `get_cliente_360` do Ex. 8).
# MAGIC
# MAGIC A IA do app (o Supervisor, a leitura dos gráficos e o e-mail de retenção) passa por um
# MAGIC **model service do Unity Gateway** que este notebook cria no **seu** schema: um modelo
# MAGIC governado pelo Unity Catalog, com limite de uso e registro de cada chamada.
# MAGIC
# MAGIC Você **não escreve código** e **não concede nenhuma permissão manual**: preencha o campo no
# MAGIC topo e clique em **Run all**.
# MAGIC
# MAGIC **Como o app acessa os dados (on-behalf-of):** o app roda cada consulta e cada chamada de
# MAGIC IA **com a identidade do usuário logado** (autenticação *on-behalf-of-user*, via o header
# MAGIC `X-Forwarded-Access-Token`). Como VOCÊ já tem acesso — `SELECT` em `dbacademy.churn` (pelo
# MAGIC grupo do treino), é dono do seu schema, das suas funções e dos seus Genies — **nada precisa
# MAGIC ser concedido** ao *service principal* do app. Esse é o pulo do gato deste deploy: zero
# MAGIC concessões, funciona para qualquer aluno.
# MAGIC
# MAGIC **Pré-requisitos** (no seu schema `dbacademy.<seu_schema>`):
# MAGIC - **Ex. 7** — os seus Genie Agents `Faturamento - <seu_schema>` e `Suporte - <seu_schema>`
# MAGIC   (o notebook os encontra **pelo nome**).
# MAGIC - **Ex. 6** — a tabela `churn_scores`.
# MAGIC - **Ex. 8** — a função `get_cliente_360` (com as ofertas calculadas em SQL).
# MAGIC
# MAGIC > Rode no cluster `dbacademy_workshop_cluster`. O app roda em compute próprio do Databricks Apps.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 1 — Preencha os campos e rode tudo
# MAGIC 1. **Rode só a célula abaixo** (Shift+Enter) para os campos aparecerem no topo do notebook.
# MAGIC 2. Preencha **1. Seu schema** (ex.: `cbettanim`).
# MAGIC 3. Confira **2. Genie de Faturamento** e **3. Genie de Suporte**: os dropdowns listam os Genie
# MAGIC    Agents que **você** criou e já vêm com os seus do Ex. 7 selecionados (o mais recente cujo
# MAGIC    nome começa com "Faturamento" / "Suporte"). São os especialistas do Supervisor do app. Criou ou
# MAGIC    renomeou um Genie depois? Rode esta célula de novo para a lista atualizar.
# MAGIC 4. **4. Warehouse** já vem com `dbacademy_workshop_wh` e **5. Model service** com
# MAGIC    `retencao-gateway` (o modelo que o notebook vai criar no Unity Gateway, no seu schema).
# MAGIC    Pode deixar como estão.
# MAGIC 5. Só então clique em **Run all**.

# COMMAND ----------

# Cria os campos no topo do notebook. Rode ESTA célula primeiro, preencha os campos e depois Run all.
# O warehouse vira um dropdown com os warehouses reais do workspace, já com o do Setup selecionado.
# Os dois Genies viram dropdowns com os Genie Agents que VOCÊ criou (os que ficam na sua pasta).
import re as _re
from concurrent.futures import ThreadPoolExecutor as _TPE
from databricks.sdk import WorkspaceClient as _WC
_w0 = _WC()
_wh_names = [x.name for x in _w0.warehouses.list()]
_WH_DEFAULT = "dbacademy_workshop_wh"
_wh_choices = _wh_names or [""]
_wh_sel = _WH_DEFAULT if _WH_DEFAULT in _wh_names else (_wh_names[0] if _wh_names else "")

def _meus_genies():
    """Genie Agents criados por você: a API de lista não diz o criador, mas o detalhe de cada
    space traz `parent_path` (a pasta onde ele foi criado, ex.: /Users/<você>)."""
    _home = f"/Users/{_w0.current_user.me().user_name}"
    spaces, page = [], None
    while True:
        r = _w0.api_client.do("GET", "/api/2.0/genie/spaces",
                              query={"page_size": 100, **({"page_token": page} if page else {})})
        spaces += r.get("spaces") or []
        page = r.get("next_page_token")
        if not page or len(spaces) >= 500:
            break
    def _det(sp):
        try:
            return _w0.api_client.do("GET", f"/api/2.0/genie/spaces/{sp['space_id']}")
        except Exception:
            return {}
    with _TPE(16) as _ex:
        detalhes = list(_ex.map(_det, spaces))
    def _meu(d):
        pp = (d.get("parent_path") or "").removeprefix("/Workspace")
        return pp == _home or pp.startswith(_home + "/")
    meus = [d for d in detalhes if d.get("space_id") and _meu(d)]
    return sorted(meus, key=lambda d: d.get("create_time") or "", reverse=True)  # mais recente 1º

_genies = _meus_genies()
_SEM_GENIE = "(nenhum Genie seu encontrado: crie-o no Ex. 7 e rode esta célula de novo)"
_g_choices = [f"{g['title']} · {g['space_id']}" for g in _genies] or [_SEM_GENIE]
def _pre(prefixo):  # pré-seleção: o mais recente cujo nome começa com o prefixo
    return next((c for c in _g_choices if c.lower().startswith(prefixo)), _g_choices[0])

dbutils.widgets.text("schema", "", "1. Seu schema")
dbutils.widgets.dropdown("genie_faturamento", _pre("faturamento"), _g_choices, "2. Genie de Faturamento (Ex.07)")
dbutils.widgets.dropdown("genie_suporte", _pre("suporte"), _g_choices, "3. Genie de Suporte (Ex.07)")
dbutils.widgets.dropdown("warehouse", _wh_sel, _wh_choices, "4. Warehouse")
dbutils.widgets.text("model_service", "retencao-gateway", "5. Model service")
print(f"{len(_genies)} Genie Agent(s) seu(s) encontrado(s):")
for _c in _g_choices:
    print("  -", _c)

# COMMAND ----------

SCHEMA = dbutils.widgets.get("schema").strip()
CATALOG = "dbacademy"
WAREHOUSE_W = dbutils.widgets.get("warehouse").strip()
MODEL_SERVICE_NAME = dbutils.widgets.get("model_service").strip() or "retencao-gateway"

assert SCHEMA, "Preencha o widget 'Seu schema' (ex.: cbettanim)."

import os, re, shutil, time, unicodedata
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# (Mantenedores do curso) Origem alternativa do código do app, para validar um branch/fork antes
# do merge: URL de um .zip do GitHub ou um caminho /Workspace/... com a pasta app/. NÃO é um
# widget (o aluno não vê): só é lido quando passado como parâmetro de job (`app_source`).
try:
    APP_SOURCE = dbutils.widgets.get("app_source").strip()
except Exception:
    APP_SOURCE = ""

# Escopos OBO: `sql` (SQL Warehouse) + `dashboards.genie` (os seus Genies, consultados pelo
# Supervisor) + `ai-gateway` (model service do Unity Gateway; sem ele, o Gateway responde 403) +
# `model-serving` (serving endpoints).
USER_API_SCOPES = ["sql", "dashboards.genie", "ai-gateway", "model-serving"]
EXPLAIN_MODEL = "databricks-claude-sonnet-4-5"   # leitura por IA dos gráficos (Cockpit)
WAREHOUSE_NAME = "dbacademy_workshop_wh"          # criado no Setup (Ex. 00)
GATEWAY_DEST_MODEL = "models/system.ai.gpt-oss-20b"  # modelo por trás do model service

# Nome do app: prefixo + database normalizado, LIMITADO a 30 caracteres
# (Databricks Apps exige nome entre 2 e 30 chars). Trunca e remove hífen sobrando no fim.
APP_NAME = ("central-retencao-" + re.sub(r"[^a-z0-9-]", "-", SCHEMA.lower()).strip("-"))[:30].rstrip("-")
ME = w.current_user.me().user_name

print("Aluno            :", ME)
print("App              :", APP_NAME, f"({len(APP_NAME)} chars)")
print("Catálogo/schema  :", f"{CATALOG}.{SCHEMA}  (+ {CATALOG}.churn compartilhado)")
GATEWAY_MODEL = f"{CATALOG}.{SCHEMA}.{MODEL_SERVICE_NAME}"
print("Model service    :", GATEWAY_MODEL, "(Unity Gateway)")
print("Auth             : on-behalf-of-user (roda como VOCÊ; sem grants ao service principal)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 2 — Resolver o SQL Warehouse
# MAGIC O app lê os dados via warehouse (com o SEU token). Resolvemos por **nome** (o ID não é
# MAGIC portável): widget → `dbacademy_workshop_wh` → primeiro warehouse disponível.

# COMMAND ----------

def resolver_warehouse():
    whs = list(w.warehouses.list())
    if not whs:
        raise RuntimeError("Nenhum SQL Warehouse encontrado no workspace. Rode o Setup (Ex. 00).")
    if WAREHOUSE_W:
        m = next((x for x in whs if x.id == WAREHOUSE_W or x.name == WAREHOUSE_W), None)
        if m:
            return m.id, m.name, "widget"
        print(f"  aviso: warehouse '{WAREHOUSE_W}' do widget não encontrado; caindo para a cascata.")
    m = next((x for x in whs if x.name == WAREHOUSE_NAME), None)
    if m:
        return m.id, m.name, f"nome '{WAREHOUSE_NAME}'"
    m = next((x for x in whs if str(getattr(x, "state", "")).upper().endswith("RUNNING")), whs[0])
    return m.id, m.name, "fallback (primeiro disponível)"

WH_ID, WH_NAME, WH_VIA = resolver_warehouse()
print(f"Warehouse: '{WH_NAME}' (id {WH_ID}) — resolvido por {WH_VIA}.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 3 — Confirmar os seus Genies (Ex. 7)
# MAGIC O **Assistente** do app tem um **Supervisor em código** (`app/server/supervisor.py`): um
# MAGIC agente que lê a pergunta, escolhe o especialista certo e sintetiza a resposta. Os
# MAGIC especialistas são os dois Genie Agents que você selecionou nos campos **2** e **3**: o app
# MAGIC recebe os IDs deles. Se um campo ficar sem Genie (ex.: rodando como job), procuramos pelo
# MAGIC **nome** do Ex. 7 (`Faturamento - <seu_schema>` / `Suporte - <seu_schema>`).

# COMMAND ----------

def _norm(txt):
    txt = unicodedata.normalize("NFKD", txt or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[\s_\-\u2013\u2014]+", " ", txt).strip()

def listar_genies():
    spaces, page = [], None
    while True:
        q = {"page_size": 100, **({"page_token": page} if page else {})}
        r = w.api_client.do("GET", "/api/2.0/genie/spaces", query=q)
        spaces += r.get("spaces") or []
        page = r.get("next_page_token")
        if not page:
            return spaces

def achar_genie(spaces, dominio):
    nome = f"{dominio} - {SCHEMA}"
    achados = [s for s in spaces if _norm(s.get("title")) == _norm(nome)]
    if not achados:
        parecidos = [s.get("title") for s in spaces if _norm(dominio) in _norm(s.get("title"))][:10]
        raise AssertionError(
            f"Não encontrei o Genie '{nome}' (Ex. 7). Confira o nome em Genie Agents"
            + (f"; Genies parecidos que você acessa: {parecidos}" if parecidos else "")
            + f". Renomeie-o para '{nome}' ou crie-o como no Ex. 7 e rode de novo.")
    if len(achados) > 1:
        print(f"  aviso: {len(achados)} Genies chamados '{nome}'; usando o primeiro "
              f"({[s.get('space_id') for s in achados]}).")
    return achados[0]["space_id"], achados[0].get("title")

def genie_do_widget(widget, dominio):
    """ID do Genie selecionado no dropdown (o texto termina com o id); sem seleção, pelo nome."""
    m = re.search(r"([0-9a-f]{32})\s*$", dbutils.widgets.get(widget).strip())
    if m:
        sp = w.api_client.do("GET", f"/api/2.0/genie/spaces/{m.group(1)}")
        return sp["space_id"], sp.get("title"), f"do campo {'2' if dominio == 'Faturamento' else '3'}"
    sid, title = achar_genie(listar_genies(), dominio)
    return sid, title, "encontrado pelo nome"

GENIE_FAT_ID, _fat_title, _fat_via = genie_do_widget("genie_faturamento", "Faturamento")
GENIE_SUP_ID, _sup_title, _sup_via = genie_do_widget("genie_suporte", "Suporte")
assert GENIE_FAT_ID != GENIE_SUP_ID, (
    "Os campos 2 e 3 apontam para o MESMO Genie. Selecione o de Faturamento no campo 2 e o de "
    "Suporte no campo 3 e rode de novo.")
print(f"Genie Faturamento: '{_fat_title}' (id {GENIE_FAT_ID}) — {_fat_via}")
print(f"Genie Suporte    : '{_sup_title}' (id {GENIE_SUP_ID}) — {_sup_via}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 4 — Criar o seu model service no Unity Gateway
# MAGIC Um **model service** é um modelo de IA governado pelo Unity Catalog: ele fica no **seu**
# MAGIC schema (você é o dono), tem **limite de uso** (60 chamadas por minuto) e uma **tabela de
# MAGIC inferência** que registra cada chamada (pergunta e resposta). O app vai usá-lo para ler os
# MAGIC gráficos e para escrever o e-mail de retenção. Se ele já existir, só reaproveitamos.

# COMMAND ----------

def api(method, path, body=None):
    return w.api_client.do(method, path, body=body)

_ms_path = f"/api/2.1/unity-catalog/model-services/{GATEWAY_MODEL}"
try:
    api("GET", _ms_path)
    print(f"Model service '{GATEWAY_MODEL}' já existe — reaproveitando.")
except Exception:
    api("POST", f"/api/2.1/unity-catalog/model-services?model_service_id={MODEL_SERVICE_NAME}"
                f"&parent=schemas/{CATALOG}.{SCHEMA}", body={
        "comment": "Master Training — modelo da Central de Retenção (Unity Gateway)",
        "config": {
            "routing": {"destinations": [{
                "destination_type": "DESTINATION_TYPE_PAY_PER_TOKEN_FOUNDATION_MODEL",
                "name": "primary", "traffic_percentage": 100,
                "pay_per_token_config": {"model": GATEWAY_DEST_MODEL}}]},
            "rate_limits": [{"key": "RATE_LIMIT_KEY_SERVICE",
                             "renewal_period": "RATE_LIMIT_RENEWAL_PERIOD_MINUTE", "requests": 60}],
            "inference_table": {"parent": f"schemas/{CATALOG}.{SCHEMA}",
                                "table_name_prefix": MODEL_SERVICE_NAME.replace("-", "_")},
        },
    })
    print(f"Model service '{GATEWAY_MODEL}' criado.")
_ms = api("GET", _ms_path)
_dest = (_ms.get("config") or {}).get("routing", {}).get("destinations", [{}])[0]
print("  destino        :", (_dest.get("pay_per_token_config") or {}).get("model"))
print("  inference table:", ((_ms.get("config") or {}).get("inference_table") or {}).get("table"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 5 — Preparar o código-fonte do app (com a SUA configuração)
# MAGIC Este notebook é **autocontido**: ele **baixa o código do app** do repositório público no
# MAGIC GitHub (a pasta `09 - Criação de Apps/app/`), copia para uma pasta sua no workspace e grava
# MAGIC os seus valores no `app.yaml` (warehouse, Genies, model service). O app é **inteiramente
# MAGIC dirigido por config** (`server/config.py` lê as variáveis `CR_*`) — nada é escrito no código.

# COMMAND ----------

import urllib.request, zipfile, tempfile, glob

# Baixa o repositório do GitHub (a compute do Databricks alcança github.com) e usa o app/ de lá.
# TEMPORÁRIO (validação do branch feat/supervisor-em-codigo): antes do merge, voltar para
# "https://github.com/CaduBettanim/Databricks-Master-Training/archive/refs/heads/main.zip".
ZIP_URL = "https://github.com/vitor-bricks/Databricks-Master-Training/archive/refs/heads/feat/supervisor-em-codigo.zip"
if APP_SOURCE.startswith("/Workspace/"):
    SRC_APP = APP_SOURCE
    assert os.path.isdir(os.path.join(SRC_APP, "server")), f"app_source sem a pasta app/: {SRC_APP}"
    print("app copiado de (app_source):", SRC_APP)
else:
    ZIP_URL = APP_SOURCE or ZIP_URL
    _tmp = tempfile.mkdtemp()
    _zip = os.path.join(_tmp, "repo.zip")
    urllib.request.urlretrieve(ZIP_URL, _zip)
    with zipfile.ZipFile(_zip) as _zf:
        _zf.extractall(_tmp)
    _matches = glob.glob(os.path.join(_tmp, "*", "09 - Criação de Apps", "app"))
    assert _matches, (
        "Não consegui baixar o app/ do GitHub. Confirme que a compute alcança github.com "
        "(ou adicione o repositório como Git folder e use a pasta app/ local)."
    )
    SRC_APP = _matches[0]
    print("app baixado do GitHub:", ZIP_URL)

STAGE = f"/Workspace/Users/{ME}/.central-retencao/{APP_NAME}"
if os.path.exists(STAGE):
    shutil.rmtree(STAGE)
shutil.copytree(SRC_APP, STAGE)

# app.yaml com a config do aluno. Obs.: os escopos OBO NÃO vão no app.yaml (chave ignorada e
# pode falhar o build); são configurados no APP (campo user_api_scopes) no Passo 7.
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
  - name: CR_GENIE_FATURAMENTO_ID
    value: "{GENIE_FAT_ID}"
  - name: CR_GENIE_SUPORTE_ID
    value: "{GENIE_SUP_ID}"
  - name: CR_EXPLAIN_MODEL
    value: "{EXPLAIN_MODEL}"
  - name: CR_GATEWAY_MODEL
    value: "{GATEWAY_MODEL}"
  - name: CR_CATALOG
    value: "{CATALOG}"
  - name: CR_SCHEMA_CHURN
    value: "churn"
  - name: CR_SCHEMA_PESSOAL
    value: "{SCHEMA}"
"""
with open(os.path.join(STAGE, "app.yaml"), "w") as f:
    f.write(APP_YAML)

print("Código preparado em:", STAGE)
print(APP_YAML)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 6 — Criar o app (compute próprio + service principal)
# MAGIC Se já existir (re-execução), seguimos em frente. Esperamos o compute ficar **ACTIVE**.

# COMMAND ----------

try:
    api("GET", f"/api/2.0/apps/{APP_NAME}")
    print(f"App '{APP_NAME}' já existe — reaproveitando.")
except Exception:
    api("POST", "/api/2.0/apps", body={
        "name": APP_NAME,
        "description": "Central de Retenção — Master Training (churn): Cockpit + Assistente + Retenção.",
    })
    print(f"App '{APP_NAME}' criado.")

for _ in range(60):
    app = api("GET", f"/api/2.0/apps/{APP_NAME}")
    if (app.get("compute_status") or {}).get("state") == "ACTIVE":
        break
    time.sleep(10)

SP = app.get("service_principal_client_id")
APP_URL = app.get("url")
print(f"compute: {(app.get('compute_status') or {}).get('state')}  |  SP: {SP}")
print("URL     :", APP_URL)
assert SP, "Service principal do app ainda não disponível; re-execute esta célula."

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 7 — Configurar OBO (escopos) + o warehouse
# MAGIC O ÚNICO preparo necessário — e nenhum é uma concessão ao usuário/SP:
# MAGIC - **user_api_scopes** = `sql`, `dashboards.genie`, `ai-gateway`, `model-serving` → habilita o
# MAGIC   app a usar o token do usuário nas chamadas de SQL, dos seus Genies (Supervisor) e do seu
# MAGIC   model service do Unity Gateway;
# MAGIC - **recurso warehouse** (CAN_USE) → o app precisa declarar o warehouse que vai usar.
# MAGIC
# MAGIC **Não há** GRANT de UC, EXECUTE, CAN_QUERY em endpoints, nem CAN_RUN em Genies: tudo isso é
# MAGIC dispensado pelo OBO (as chamadas rodam como o usuário, que já tem acesso).

# COMMAND ----------

api("PATCH", f"/api/2.0/apps/{APP_NAME}", body={
    "name": APP_NAME,
    "user_api_scopes": USER_API_SCOPES,
    "resources": [
        {"name": "sql-warehouse", "description": "Warehouse p/ ler o Unity Catalog (como o usuário)",
         "sql_warehouse": {"id": WH_ID, "permission": "CAN_USE"}},
    ],
})
_app = api("GET", f"/api/2.0/apps/{APP_NAME}")
print("escopos OBO :", _app.get("effective_user_api_scopes"))
print("recursos    :", [r["name"] for r in _app.get("resources", [])])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Passo 8 — Publicar (deploy)

# COMMAND ----------

api("POST", f"/api/2.0/apps/{APP_NAME}/deployments",
    body={"source_code_path": STAGE, "mode": "SNAPSHOT"})
estado = None
for _ in range(60):
    app = api("GET", f"/api/2.0/apps/{APP_NAME}")
    ad = app.get("active_deployment") or {}
    estado = (ad.get("status") or {}).get("state")
    if estado in ("SUCCEEDED", "FAILED", "STOPPED"):
        break
    time.sleep(10)
print("deploy:", estado)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pronto! 🎉

# COMMAND ----------

print("=" * 66)
print("  CENTRAL DE RETENÇÃO — publicada (autenticação on-behalf-of usuário)")
print("=" * 66)
print("  App URL :", APP_URL)
print("  Deploy  :", estado)
print("  Modelo  :", GATEWAY_MODEL, "(Unity Gateway)")
print("  Genies  :", f"Faturamento {GENIE_FAT_ID} · Suporte {GENIE_SUP_ID} (Supervisor em código)")
print("  Escopos :", USER_API_SCOPES, "(o app usa o SEU token nas chamadas)")
print("  Grants  : NENHUM concedido ao service principal — desnecessário sob OBO.")
print("  Manual  : só o campo 'Seu schema' (e conferir os 2 Genies) deste notebook.")
print("=" * 66)
print("  Abra a URL acima e explore as 3 abas. Tudo roda com a SUA identidade:")
print("  o Cockpit lê os dados, o Supervisor do Assistente consulta os seus Genies e")
print("  a Retenção chama as suas UC functions — sem precisar conceder nada.")
displayHTML(f'<h3>Central de Retenção</h3><a href="{APP_URL}" target="_blank">{APP_URL}</a>')
