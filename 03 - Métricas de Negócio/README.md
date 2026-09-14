# 03 - Métricas de Negócio

Definir **métricas de negócio uma única vez** — governadas no Unity Catalog — e reutilizá-las em SQL, dashboards e na Genie. É o primeiro exercício em que **você cria objetos no seu schema**.

**Pré-requisitos:** [Setup](../00%20-%20Setup) concluído e o seu **database pessoal** criado (Passo 0 do [Ex. 1](../01%20-%20SQL%20com%20IA)).

## O que é uma Metric View
Uma view especial (`WITH METRICS`, em YAML) que separa **dimensões** (por onde cortar) de **medidas** (o que calcular). Você consulta as medidas com a função **`MEASURE()`**, e a definição fica **governada e consistente** para todos — dashboards e Genie passam a usar a mesma fonte da verdade.

## Passo 1 — Criar as suas metric views
1. Importe o notebook por URL (**Workspace → Import → URL**):
   ```
   https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/03%20-%20M%C3%A9tricas%20de%20Neg%C3%B3cio/notebook_metric_views.py
   ```
2. Na 1ª célula, troque `NOME_SCHEMA` pelo **seu** database pessoal.
3. Anexe **Serverless** e clique em **Run all**.

O notebook cria três metric views no **seu** schema, lendo de `dbacademy.churn`:
- **`mvw_churn`** — Cancelamentos, Clientes, Taxa de Churn (por Segmento, Plano, Mês)
- **`mvw_receita`** — Receita, Inadimplência, Ticket Médio (por Segmento, Mês)
- **`mvw_suporte`** — Tickets, CSAT Médio, NPS Médio (por Segmento, Canal, Categoria)

> O SQL completo das views está em [`metric_views.sql`](./metric_views.sql).
> As metric views são criadas via **notebook (Spark)**; depois de criadas, ficam disponíveis para consultas SQL, **dashboards (Ex. 5)** e **Genie (Ex. 7)**.

## Passo 2 — Por que Metric Views? (antes × depois)
Agora que suas metric views existem, compare as duas formas de calcular a **mesma** métrica — **inadimplência por segmento**. Dão o mesmo número, com esforço e risco bem diferentes.

**Sem metric view (SQL puro):** você precisa acertar o join, a lógica condicional e a forma de média:
```sql
SELECT c.segmento,
       ROUND(AVG(CASE WHEN NOT f.pago THEN 1.0 ELSE 0.0 END), 3) AS inadimplencia
FROM dbacademy.churn.fato_faturamento f
JOIN dbacademy.churn.dim_cliente c ON f.id_cliente = c.id_cliente
GROUP BY c.segmento
ORDER BY inadimplencia DESC;
```

**Com a metric view:** a fórmula já está governada — você só pede pelo nome:
```sql
SELECT `Segmento`, ROUND(MEASURE(`Inadimplência`), 3) AS inadimplencia
FROM dbacademy.<seu_db>.mvw_receita
GROUP BY `Segmento`
ORDER BY inadimplencia DESC;
```

Ambas retornam **Corporativo 0,069 · PME 0,068 · Consumidor 0,068**. A diferença: na metric view a fórmula complexa (join + `CASE` + média) foi escrita **uma vez** por quem entende, e todo mundo reusa sem risco de errar. **Quanto mais complexa a métrica, maior o ganho.**

## Explore no catálogo
Navegue no seu catálogo para entender como as metric views são armazenadas e disponíveis. Vamos também utilizar Metric Views nos próximos exercícios.
