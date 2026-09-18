# Databricks notebook source
# MAGIC %md
# MAGIC # Exercício 3 — Metric Views (métricas governadas)
# MAGIC Cria `mvw_churn`, `mvw_receita` e `mvw_suporte` no **seu schema pessoal**, lendo da base
# MAGIC compartilhada `dbacademy.churn`. Depois consulte com `MEASURE()`.

# COMMAND ----------

NOME_CATALOGO = "dbacademy"
_schemas = [r[0] for r in spark.sql(f"SHOW SCHEMAS IN {NOME_CATALOGO}").collect() if r[0] != "churn"]
dbutils.widgets.dropdown("database", _schemas[0] if _schemas else "", _schemas or [""], "Seu schema (dbacademy.<schema>)")
NOME_SCHEMA = dbutils.widgets.get("database")

fq = f"{NOME_CATALOGO}.{NOME_SCHEMA}"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {fq}")

# COMMAND ----------
# ## 1. Criar as metric views
for view, ddl in [
    ("mvw_churn", f"""CREATE OR REPLACE VIEW {fq}.mvw_churn (
  `Segmento`      COMMENT 'Segmento do cliente',
  `Plano`         COMMENT 'Nome do plano',
  `Mês`           COMMENT 'Mês do cancelamento',
  `Cancelamentos` COMMENT 'Assinaturas canceladas',
  `Clientes`      COMMENT 'Total de clientes',
  `Taxa de Churn` COMMENT 'Cancelamentos / Clientes'
) WITH METRICS LANGUAGE YAML
COMMENT 'Métricas de churn/retenção' AS $$
version: 0.1
source: dbacademy.churn.fato_assinatura
joins:
  - name: cliente
    source: dbacademy.churn.dim_cliente
    'on': source.id_cliente = cliente.id_cliente
  - name: plano
    source: dbacademy.churn.dim_plano
    'on': source.id_plano = plano.id_plano
dimensions:
  - name: Segmento
    expr: cliente.segmento
  - name: Plano
    expr: plano.nome_plano
  - name: Mês
    expr: date_trunc('MONTH', source.data_fim)
measures:
  - name: Cancelamentos
    expr: SUM(source.churn_flag)
  - name: Clientes
    expr: COUNT(DISTINCT source.id_cliente)
  - name: Taxa de Churn
    expr: SUM(source.churn_flag) / COUNT(DISTINCT source.id_cliente)
$$"""),
    ("mvw_receita", f"""CREATE OR REPLACE VIEW {fq}.mvw_receita (
  `Segmento`      COMMENT 'Segmento do cliente',
  `Mês`           COMMENT 'Competência (mês)',
  `Receita`       COMMENT 'Soma faturada',
  `Inadimplência` COMMENT 'Percentual de faturas não pagas',
  `Ticket Médio`  COMMENT 'Valor médio por fatura'
) WITH METRICS LANGUAGE YAML
COMMENT 'Métricas de receita' AS $$
version: 0.1
source: dbacademy.churn.fato_faturamento
joins:
  - name: cliente
    source: dbacademy.churn.dim_cliente
    'on': source.id_cliente = cliente.id_cliente
dimensions:
  - name: Segmento
    expr: cliente.segmento
  - name: Mês
    expr: date_trunc('MONTH', source.competencia)
measures:
  - name: Receita
    expr: SUM(source.valor)
  - name: Inadimplência
    expr: AVG(CASE WHEN NOT source.pago THEN 1.0 ELSE 0.0 END)
  - name: Ticket Médio
    expr: AVG(source.valor)
$$"""),
    ("mvw_suporte", f"""CREATE OR REPLACE VIEW {fq}.mvw_suporte (
  `Segmento`   COMMENT 'Segmento do cliente',
  `Canal`      COMMENT 'Canal do ticket',
  `Categoria`  COMMENT 'Categoria do ticket',
  `Tickets`    COMMENT 'Quantidade de tickets',
  `CSAT Médio` COMMENT 'CSAT médio (1-5)',
  `NPS Médio`  COMMENT 'NPS médio (0-10)'
) WITH METRICS LANGUAGE YAML
COMMENT 'Métricas de atendimento' AS $$
version: 0.1
source: dbacademy.churn.fato_ticket_suporte
joins:
  - name: cliente
    source: dbacademy.churn.dim_cliente
    'on': source.id_cliente = cliente.id_cliente
dimensions:
  - name: Segmento
    expr: cliente.segmento
  - name: Canal
    expr: source.canal
  - name: Categoria
    expr: source.categoria
measures:
  - name: Tickets
    expr: COUNT(1)
  - name: CSAT Médio
    expr: AVG(source.csat)
  - name: NPS Médio
    expr: AVG(source.nps)
$$"""),
]:
    spark.sql(ddl)
    print("criada:", f"{fq}.{view}")

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
