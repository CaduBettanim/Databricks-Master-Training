# 05 - Dashboards (AI/BI)

Transformar os dados de churn em um **painel executivo** — e deixar o **Assistente de IA** (✨) do dashboard **montar os gráficos a partir de prompts**. Você descreve o gráfico em linguagem natural, ele desenha; você só ajusta.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).

## Objetivo
Construir, do zero, um dashboard **AI/BI** de retenção com:
- um **KPI** de taxa de churn e de receita ativa (MRR);
- **churn por plano, segmento e canal**;
- **cancelamentos ao longo do tempo** e **motivos**;
- **inadimplência mensal**;
- um **filtro** que deixa o painel inteiro interativo.

> Os dois **datasets** (consultas SQL que alimentam o painel) estão em [`dashboard_datasets.sql`](./dashboard_datasets.sql). Os **gráficos** você cria com o Assistente, no Canvas.

---

## Passo 1 — Criar o dashboard e o 1º dataset
1. No menu lateral, **New → Dashboard** (ou **Dashboards → Create dashboard**).
2. Abra a aba **Data** (Dados) e clique em **Add SQL Dataset**.
3. Cole a consulta do **Dataset 1 — assinaturas** (está no `.sql`) e **Run**. Renomeie o dataset para **`assinaturas`**.

```text
Dataset 1 — cole na aba Dados (é 1 linha por assinatura, com status Ativa/Cancelada,
plano, segmento, canal, UF, faixa etária e motivo de cancelamento).
```
Este único dataset já alimenta a maioria dos gráficos abaixo.

## Passo 2 — Montar os gráficos com o Assistente (✨)
Vá para a aba **Canvas**. Clique em **Add a visualization** e, no painel do **Assistente**, use o dataset **`assinaturas`**. Cole **um prompt por vez** — o Assistente monta o gráfico; confira e clique em **Accept**.

**2.1 — KPI de taxa de churn**
```text
Crie um indicador (KPI) com o percentual de assinaturas com status Cancelada sobre o total.
```
Esperado: **≈ 27%** (540 de 2.000).

**2.2 — Churn por plano**
```text
Gráfico de barras com o percentual de assinaturas Canceladas por nome_plano, da maior para a menor.
```
Esperado: **Básico 31,7% · Padrão 27,4% · Premium 22,5% · Empresarial 15,7%** — quanto mais barato o plano, maior o churn.

**2.3 — Churn por segmento**
```text
Gráfico de barras com o percentual de assinaturas Canceladas por segmento.
```
Esperado: **Consumidor 30,3% · PME 23,9% · Corporativo 16,6%**.

**2.4 — Cancelamentos ao longo do tempo**
```text
Gráfico de linha com a quantidade de assinaturas Canceladas por mês, usando a data_fim.
```
Esperado: uma série mensal (2023–2025) com ~12 a 21 cancelamentos/mês — dá para enxergar picos.

**2.5 — Motivos de cancelamento**
```text
Gráfico de barras com a contagem de assinaturas Canceladas por motivo_cancelamento, da maior para a menor.
```
Esperado: **Insatisfação 196 · Preço 148 · Concorrência 104 · Atendimento 80 · Mudança de necessidade 12**.

> Repare: você montou 5 visualizações **sem escrever uma linha de SQL de gráfico** — só descrevendo o que queria. É o mesmo espírito do Genie Code, agora para o painel.

## Passo 3 — Receita e inadimplência (2º dataset)
1. Volte à aba **Data → Add SQL Dataset** e cole o **Dataset 2 — faturamento**. Renomeie para **`faturamento`**.
2. No Canvas, adicione um gráfico com o Assistente usando o dataset **`faturamento`**:
```text
Gráfico de linha com a receita por competencia (mês) e uma segunda linha com o pct_nao_pago.
```
Esperado: receita mensal (total acumulado ~R$ 6,1 mi) com a **inadimplência oscilando perto de 6,8%**. Gancho para o Ex. 11 (governança/qualidade).

## Passo 4 — Deixar o painel interativo (filtro)
No Canvas, adicione um **Filter** (widget de filtro) sobre o dataset `assinaturas`, no campo **`segmento`** (ou `nome_plano`). Agora, ao escolher um segmento, **todos os gráficos** se ajustam juntos.

## Passo 5 — Publicar
Clique em **Publish** (canto superior direito). O dashboard publicado é o que você compartilha com o time de negócio — eles interagem com os filtros sem precisar do editor.

---

## 🎯 Desafio
A diretoria quer saber **onde o churn dói mais no bolso**: não basta a taxa, importa o quanto de receita está saindo. **Monte um gráfico que mostre, por plano, a receita mensal perdida com os cancelamentos** (dica: `preco_mensal` das assinaturas Canceladas) e descubra qual plano lidera a perda — nem sempre é o de maior taxa de churn.

**Dica:** Assistente (✨) + o dataset `assinaturas` 😉

## Explore
Um dashboard AI/BI não é só um relatório: cada gráfico nasceu de uma frase, e o filtro deixa qualquer pessoa de negócio explorar sozinha. No Ex. 07 vamos dar um passo além — deixar o time **perguntar em linguagem natural** com o Genie, sem nem abrir o painel.
