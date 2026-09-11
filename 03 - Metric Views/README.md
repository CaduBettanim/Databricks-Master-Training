# 03 - Metric Views

Definir **métricas de negócio uma única vez** — governadas no Unity Catalog — e reutilizá-las em SQL, dashboards e na Genie. É o primeiro exercício em que **você cria objetos no seu schema**.

**Pré-requisitos:** [Setup](../00%20-%20Setup) concluído e o seu **database pessoal** criado (Passo 0 do [Ex. 1](../01%20-%20Consultas%20SQL%20com%20Genie%20Code)).

## O que é uma Metric View
Uma view especial (`WITH METRICS`, em YAML) que separa **dimensões** (por onde cortar) de **medidas** (o que calcular). Você consulta as medidas com a função **`MEASURE()`**, e a definição fica **governada e consistente** para todos — dashboards e Genie passam a usar a mesma fonte da verdade.

## Passo 1 — Criar as suas metric views
1. Importe o notebook por URL (**Workspace → Import → URL**):
   ```
   https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/03%20-%20Metric%20Views/notebook_metric_views.py
   ```
2. Na 1ª célula, troque `NOME_SCHEMA` pelo **seu** database pessoal.
3. Anexe **Serverless** e clique em **Run all**.

O notebook cria três metric views no **seu** schema, lendo de `dbacademy.churn`:
- **`mvw_churn`** — Cancelamentos, Clientes, Taxa de Churn (por Segmento, Plano, Mês)
- **`mvw_receita`** — Receita, Inadimplência, Ticket Médio (por Segmento, Mês)
- **`mvw_suporte`** — Tickets, CSAT Médio, NPS Médio (por Segmento, Canal, Categoria)

> O SQL completo das views está em [`metric_views.sql`](./metric_views.sql).
> As metric views são criadas via **notebook (Spark)**; depois de criadas, ficam disponíveis para consultas SQL, **dashboards (Ex. 5)** e **Genie (Ex. 7)**.

## Passo 2 — Consultar com `MEASURE()`
As últimas células do notebook já mostram exemplos. Troque `<seu_db>` pelo seu schema:
```sql
SELECT `Segmento`, ROUND(MEASURE(`Taxa de Churn`), 3) AS taxa_churn
FROM dbacademy.<seu_db>.mvw_churn
GROUP BY `Segmento` ORDER BY taxa_churn DESC;
```

## Resultados esperados (dataset fixo → valores exatos)

**Taxa de churn por segmento (`mvw_churn`):** Consumidor **0,303** · PME **0,239** · Corporativo **0,166**

**Receita por segmento (`mvw_receita`):** _(preenchido na validação)_

**Suporte por categoria (`mvw_suporte`):** _(preenchido na validação)_
