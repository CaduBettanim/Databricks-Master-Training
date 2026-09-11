# Databricks notebook source
# MAGIC %md
# MAGIC # Setup — Base COMPARTILHADA de Churn
# MAGIC Rode **1x** (instrutor). Lê os CSVs deste repositório (via URL) → tabelas Delta,
# MAGIC deriva `feature_churn`, documenta (comentários + PK/FK) e monta a base de conhecimento.
# MAGIC
# MAGIC Metric views (Ex.3), modelo (Ex.6) e funções (Ex.11) são criados por cada aluno no schema pessoal.

# COMMAND ----------

# Parâmetros — ajuste se necessário
NOME_CATALOGO = "dbacademy"     # catálogo Unity Catalog de destino
NOME_SCHEMA   = "churn"         # schema COMPARTILHADO (somente leitura para alunos)
CSV_BASE      = "https://raw.githubusercontent.com/CaduBettanim/Databricks-Master-Training/main/data"
fq = f"{NOME_CATALOGO}.{NOME_SCHEMA}"

# Garante o catálogo. Só tenta criar se faltar; se não conseguir (contas com Default Storage
# não permitem CREATE CATALOG via SQL sem MANAGED LOCATION), avisa para criar na mão pela UI.
existentes = [row[0] for row in spark.sql("SHOW CATALOGS").collect()]
if NOME_CATALOGO not in existentes:
    try:
        spark.sql(f"CREATE CATALOG {NOME_CATALOGO}")
    except Exception as e:
        raise RuntimeError(
            f"⚠️ O catálogo '{NOME_CATALOGO}' não existe e não pôde ser criado automaticamente. "
            f"Crie-o pela UI (Catalog Explorer → Create catalog → Default Storage) e rode de novo. "
            f"Detalhe: {str(e)[:160]}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {fq} COMMENT 'Base compartilhada de churn do Master Training'")

# COMMAND ----------
# ## 1. Carrega os CSVs (do repositório) → tabelas Delta
import pandas as pd
from pyspark.sql.functions import to_date, col, lower, when, trim

def carrega(nome, dates=(), bools=()):
    pdf = pd.read_csv(f"{CSV_BASE}/{nome}.csv", keep_default_na=False)  # "" em vez de NaN
    df = spark.createDataFrame(pdf)   # numéricos inferidos; datas/bools vêm como string
    for d in dates:  # trata vazio como NULL antes do cast (ANSI: to_date('') estoura)
        df = df.withColumn(d, to_date(when(trim(col(d)) == "", None).otherwise(col(d))))
    for b in bools:
        df = df.withColumn(b, lower(col(b).cast("string")) == "true")
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{fq}.{nome}")
    print(f"  {nome:22} {df.count():>6} linhas")

carrega("dim_plano")
carrega("dim_cliente", dates=["data_cadastro"])
carrega("dim_data", dates=["data"], bools=["fim_de_semana"])
carrega("fato_assinatura", dates=["data_inicio", "data_fim"])
carrega("fato_uso", dates=["competencia"])
carrega("fato_faturamento", dates=["competencia"], bools=["pago"])
carrega("fato_ticket_suporte", dates=["data_abertura"])

# COMMAND ----------
# ## 2. feature_churn (features comportamentais, sem leakage)
spark.sql(f"""CREATE OR REPLACE TABLE {fq}.feature_churn AS
WITH u AS (SELECT id_cliente, AVG(logins_mes) uso_medio, AVG(horas_uso) horas_medio FROM {fq}.fato_uso GROUP BY id_cliente),
f AS (SELECT id_cliente, AVG(dias_atraso) dias_atraso_medio, AVG(CASE WHEN NOT pago THEN 1.0 ELSE 0.0 END) pct_faturas_atraso FROM {fq}.fato_faturamento GROUP BY id_cliente),
t AS (SELECT id_cliente, AVG(csat) csat_medio, AVG(nps) nps_medio FROM {fq}.fato_ticket_suporte GROUP BY id_cliente)
SELECT c.id_cliente, c.segmento, p.nome_plano, CAST(p.preco_mensal AS DOUBLE) preco_mensal,
 CAST(COALESCE(u.uso_medio,0) AS DOUBLE) uso_medio, CAST(COALESCE(u.horas_medio,0) AS DOUBLE) horas_medio,
 CAST(COALESCE(f.dias_atraso_medio,0) AS DOUBLE) dias_atraso_medio, CAST(COALESCE(f.pct_faturas_atraso,0) AS DOUBLE) pct_faturas_atraso,
 CAST(COALESCE(t.csat_medio,3) AS DOUBLE) csat_medio, CAST(COALESCE(t.nps_medio,7) AS DOUBLE) nps_medio, a.churn_flag
FROM {fq}.dim_cliente c JOIN {fq}.fato_assinatura a ON a.id_cliente=c.id_cliente
JOIN {fq}.dim_plano p ON p.id_plano=a.id_plano
LEFT JOIN u ON u.id_cliente=c.id_cliente LEFT JOIN f ON f.id_cliente=c.id_cliente LEFT JOIN t ON t.id_cliente=c.id_cliente""")

# COMMAND ----------
# ## 3. Comentários + constraints (documentação p/ Genie e Discovery)
tabc={"dim_cliente":"Dimensão de clientes.","dim_plano":"Dimensão de planos.","dim_data":"Dimensão calendário.",
 "fato_assinatura":"Assinaturas: uma por cliente, com status e churn.","fato_uso":"Uso mensal por cliente.",
 "fato_faturamento":"Faturamento mensal por cliente.","fato_ticket_suporte":"Tickets de suporte com texto, CSAT e NPS.",
 "feature_churn":"Tabela analítica por cliente (features comportamentais) para o modelo de churn."}
colc={"dim_cliente":{"id_cliente":"Identificador único do cliente","nome_cliente":"Nome do cliente","segmento":"Segmento: Consumidor, PME ou Corporativo","cidade":"Cidade","uf":"Estado (UF)","data_cadastro":"Data de cadastro","canal_aquisicao":"Canal de aquisição","faixa_etaria":"Faixa etária"},
 "dim_plano":{"id_plano":"Identificador do plano","nome_plano":"Nome do plano: Básico, Padrão, Premium ou Empresarial","periodicidade":"Mensal ou Anual","preco_mensal":"Preço mensal em reais"},
 "dim_data":{"data":"Data","ano":"Ano","mes":"Mês","nome_mes":"Nome do mês","trimestre":"Trimestre","dia_semana":"Dia da semana","fim_de_semana":"Fim de semana?"},
 "fato_assinatura":{"id_assinatura":"ID da assinatura","id_cliente":"FK dim_cliente","id_plano":"FK dim_plano","data_inicio":"Início","data_fim":"Cancelamento (nulo se ativa)","status":"Ativa ou Cancelada","motivo_cancelamento":"Motivo do cancelamento","churn_flag":"1 se cancelou (churn), 0 se ativo"},
 "fato_uso":{"id_uso":"ID","id_cliente":"FK dim_cliente","competencia":"Mês de referência","logins_mes":"Logins no mês","horas_uso":"Horas de uso","funcionalidades_usadas":"Funcionalidades usadas"},
 "fato_faturamento":{"id_fatura":"ID","id_cliente":"FK dim_cliente","id_assinatura":"FK assinatura","competencia":"Mês","valor":"Valor em R$","pago":"Pago?","dias_atraso":"Dias de atraso"},
 "fato_ticket_suporte":{"id_ticket":"ID","id_cliente":"FK dim_cliente","data_abertura":"Abertura","canal":"Chat, Email ou Telefone","categoria":"Cobrança, Técnico, Cancelamento ou Dúvida","texto_reclamacao":"Texto do contato (pode conter PII)","csat":"Satisfação 1-5","nps":"NPS 0-10"}}
for t,c in tabc.items(): spark.sql(f"COMMENT ON TABLE {fq}.{t} IS '{c}'")
for t,cols in colc.items():
    for cc,cm in cols.items(): spark.sql(f"ALTER TABLE {fq}.{t} ALTER COLUMN {cc} COMMENT '{cm}'")
def _run(s):
    try: spark.sql(s)
    except Exception as e: print("skip:", str(e)[:70])
_run(f"ALTER TABLE {fq}.dim_cliente ALTER COLUMN id_cliente SET NOT NULL")
_run(f"ALTER TABLE {fq}.dim_plano ALTER COLUMN id_plano SET NOT NULL")
_run(f"ALTER TABLE {fq}.dim_cliente ADD CONSTRAINT pk_cliente PRIMARY KEY (id_cliente)")
_run(f"ALTER TABLE {fq}.dim_plano ADD CONSTRAINT pk_plano PRIMARY KEY (id_plano)")
for t in ["fato_assinatura","fato_uso","fato_faturamento","fato_ticket_suporte"]:
    _run(f"ALTER TABLE {fq}.{t} ADD CONSTRAINT fk_{t}_cli FOREIGN KEY (id_cliente) REFERENCES {fq}.dim_cliente(id_cliente) NOT ENFORCED RELY")

# COMMAND ----------
# ## 4. Base de conhecimento (volume + documentos)
spark.sql(f"CREATE VOLUME IF NOT EXISTS {fq}.kb_volume COMMENT 'Base de conhecimento de retenção'")
docs={
"FAQ_Atendimento.md":"# FAQ de Atendimento\n\n## Cancelamento\n- Como cancelar? Em Conta > Assinatura > Cancelar, ou com o Customer Success.\n- Multa? Planos mensais não têm; anuais têm multa proporcional aos meses restantes.\n\n## Reembolso\n- Até 7 dias após a cobrança (arrependimento) ou falha comprovada. Anual: reembolso proporcional.\n\n## Cobrança\n- Vencimento dia 10. Atraso acima de 20 dias suspende o serviço.\n\n## Suporte\n- Chat 24/7, Email e Telefone (seg-sex 8h-20h).\n",
"Politica_Retencao.md":"# Política de Retenção e Cancelamento\n\n## Ofertas autorizadas\n- Preço: até 20% de desconto por 3 meses OU upgrade grátis por 1 mês.\n- Atendimento/Insatisfação: atendimento prioritário 60 dias + gerente de contas.\n- Concorrência: match de preço por até 6 meses.\n- Corporativo: revisão contratual, desconto por volume e SLA dedicado.\n\n## Regras\n- Descontos acima de 20% exigem aprovação do gestor de CS.\n- Cliente de alto risco (score do modelo) deve ser contatado em até 48h.\n",
"Playbook_Customer_Success.md":"# Playbook de Customer Success\n\n## Priorização\n1. Alto valor (Premium/Empresarial) com risco alto.\n2. Queda de uso > 40% no trimestre.\n3. Faturas em atraso e CSAT < 3.\n\n## Fluxo\n1. Detectar risco. 2. Diagnosticar causa. 3. Selecionar oferta (Política). 4. Contatar e registrar. 5. Acompanhar 90 dias.\n"}
import os
base=f"/Volumes/{NOME_CATALOGO}/{NOME_SCHEMA}/kb_volume"
for nome,conteudo in docs.items():
    with open(f"{base}/{nome}","w") as fp: fp.write(conteudo)
print("KB:", os.listdir(base))

# COMMAND ----------
# ## 5. Relatório de validação  (valores exatos esperados: 2000 / 1253 / 0.27 / -0.504 / 0.125)
rep=spark.sql(f"""SELECT
 (SELECT COUNT(*) FROM {fq}.dim_cliente) clientes,
 (SELECT COUNT(*) FROM {fq}.fato_ticket_suporte) tickets,
 (SELECT ROUND(AVG(churn_flag),3) FROM {fq}.fato_assinatura) taxa_churn,
 (SELECT ROUND(corr(uso_medio, churn_flag),3) FROM {fq}.feature_churn) corr_uso_churn,
 (SELECT ROUND(corr(dias_atraso_medio, churn_flag),3) FROM {fq}.feature_churn) corr_atraso_churn""")
display(rep)
print("✅ Setup da base compartilhada concluído")
