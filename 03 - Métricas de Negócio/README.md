# 03 - Métricas de Negócio

![Trilha do Master Training com destaque no que foi construído até o Exercício 03](../assets/03%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Agora vamos definir métricas de negócio uma única vez (governadas no Unity Catalog) e reutilizá-las em SQL, dashboards e na Genie. Este é o primeiro exercício em que você vai criar objetos no seu próprio schema.

> Você pode encontrar o SQL completo das views em [`metric_views.sql`](./metric_views.sql)

---

## Passo 1: Criar as suas metric views
1. Importe o notebook: **Workspace → Três pontinhos no topo → Import → URL**, e cole o seguinte:
```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/03%20-%20M%C3%A9tricas%20de%20Neg%C3%B3cio/notebook_metric_views.py
```
2. Após clicar em **Import**, você será redirecionado para o notebook
3. No dropdown na barra superior, ao lado de **Run all**, selecione o cluster `dbacademy_workshop_cluster`
4. Rode a primeira célula do notebook para exibir o widget
5. No widget **Seu schema**, selecione o schema que você criou no Ex. 1
6. Clique em **Run all**

O notebook cria três metric views no seu schema, lendo do schema compartilhado `dbacademy.churn`:
- `mvw_churn`: Cancelamentos, Clientes, Taxa de Churn (por Segmento, Plano, Mês)
- `mvw_receita`: Receita, Inadimplência, Ticket Médio (por Segmento, Mês)
- `mvw_suporte`: Tickets, CSAT Médio, NPS Médio (por Segmento, Canal, Categoria)

> Depois de criadas, as metric views ficam disponíveis para consultas SQL, dashboards (Ex. 5) e Genie (Ex. 7)

### O que é uma Metric View?
Uma view especial (`WITH METRICS`, em YAML) que separa **dimensões** (por onde cortar) de **medidas** (o que calcular). Você consulta as medidas com a função `MEASURE()`, e a definição fica governada e consistente para todos: dashboards e Genie passam a usar a mesma fonte da verdade.

## Passo 2: Por que Metric Views? (antes × depois)
Agora que suas metric views existem, vamos comparar as duas formas de calcular a mesma métrica, a inadimplência por segmento. Dão o mesmo número, com esforço e risco bem diferentes.

Navegue novamente para o **SQL Editor** através do menu à esquerda para rodar as duas queries a seguir.

**Sem metric view (SQL puro):** você precisa acertar o join, a lógica condicional e a forma de média:
```sql
SELECT
    c.segmento,
    ROUND(AVG(CASE WHEN NOT f.pago THEN 1.0 ELSE 0.0 END), 3) AS inadimplencia
FROM dbacademy.churn.fato_faturamento f
JOIN dbacademy.churn.dim_cliente c ON f.id_cliente = c.id_cliente
GROUP BY c.segmento
ORDER BY inadimplencia DESC;
```

**Com a metric view:** a fórmula já está governada, então você só pede pelo nome:
```sql
SELECT
    `Segmento`,
    ROUND(MEASURE(`Inadimplência`), 3) AS inadimplencia
FROM dbacademy.<seu_schema>.mvw_receita
GROUP BY `Segmento`
ORDER BY inadimplencia DESC;
```

Ambas retornam **Corporativo 0,069 · PME 0,068 · Consumidor 0,068**. A diferença: na metric view a fórmula complexa (join + `CASE` + média) foi escrita uma vez por quem entende, e todo mundo reusa sem risco de errar. Quanto mais complexa a métrica, maior o ganho.

## Explore no catálogo
Navegue no seu catálogo para entender como as metric views são armazenadas e disponíveis. Vamos também utilizar as Metric Views nos próximos exercícios.
