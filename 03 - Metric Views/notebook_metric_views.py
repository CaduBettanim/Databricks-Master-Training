# Databricks notebook source
# MAGIC %md
# MAGIC # Exercício 3 — Metric Views (métricas governadas)
# MAGIC Cria `mvw_churn`, `mvw_receita` e `mvw_suporte` no **seu schema pessoal**, lendo da base
# MAGIC compartilhada `dbacademy.churn`. Depois consulte com `MEASURE()`.

# COMMAND ----------

NOME_CATALOGO = "dbacademy"
NOME_SCHEMA   = "<seu_db>"   # <<< troque pelo seu database pessoal (ex.: jsilva)
SQL_URL = "https://raw.githubusercontent.com/CaduBettanim/Databricks-Master-Training/main/03%20-%20Metric%20Views/metric_views.sql"

fq = f"{NOME_CATALOGO}.{NOME_SCHEMA}"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {fq}")

# COMMAND ----------
# ## 1. Criar as metric views (lê o SQL do repositório e cria no seu schema)
import urllib.request
sql = urllib.request.urlopen(SQL_URL).read().decode("utf-8").replace("<seu_db>", NOME_SCHEMA)
for stmt in sql.split(";"):
    if "CREATE OR REPLACE VIEW" in stmt:
        nome = stmt.split("VIEW",1)[1].split("(",1)[0].strip()
        spark.sql(stmt)
        print("criada:", nome)

# COMMAND ----------
# ## 2. Consultar com MEASURE()

# Taxa de churn por segmento
display(spark.sql(f"""
SELECT `Segmento`, ROUND(MEASURE(`Taxa de Churn`), 3) AS taxa_churn
FROM {fq}.mvw_churn GROUP BY `Segmento` ORDER BY taxa_churn DESC
"""))

# COMMAND ----------
# Receita e inadimplência por segmento
display(spark.sql(f"""
SELECT `Segmento`,
       ROUND(MEASURE(`Receita`), 2)       AS receita,
       ROUND(MEASURE(`Inadimplência`), 3) AS inadimplencia
FROM {fq}.mvw_receita GROUP BY `Segmento` ORDER BY receita DESC
"""))

# COMMAND ----------
# CSAT e NPS por categoria de ticket
display(spark.sql(f"""
SELECT `Categoria`,
       MEASURE(`Tickets`)              AS tickets,
       ROUND(MEASURE(`CSAT Médio`), 2) AS csat,
       ROUND(MEASURE(`NPS Médio`), 2)  AS nps
FROM {fq}.mvw_suporte GROUP BY `Categoria` ORDER BY tickets DESC
"""))

# COMMAND ----------
print("✅ Metric views criadas em", fq)
