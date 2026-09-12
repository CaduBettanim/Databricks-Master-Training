# 05 - Dashboards (AI/BI)

Transformar os dados de churn em um **painel executivo** — deixando o **Genie montar os gráficos a partir de prompts** e **reaproveitando a metric view que você criou no Ex. 3**. Você descreve as análises, ele monta; você só ajusta e publica.

**Pré-requisitos:**
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- [Ex. 3 - Metric Views](../03%20-%20Metric%20Views) concluído — a sua metric view **`mvw_churn`** precisa existir no seu database pessoal (`dbacademy.<seu_db>`).

## Objetivo
Construir um dashboard **AI/BI** de retenção com:
- um **KPI** de taxa de churn;
- **churn por plano** e **por segmento**;
- **cancelamentos ao longo do tempo**;
- um **mapa** de churn por região;
- **2 filtros** (plano, segmento) que deixam o painel interativo;
- o **logo** do treinamento no topo.

> As 4 primeiras análises saem direto da sua **`mvw_churn`** — a mesma medida governada que você definiu no Ex. 3, agora virando gráfico.

---

## Passo 1 — Criar o dashboard
No menu lateral, **New → Dashboard** e clique em **Create Dashboard**.

## Passo 2 — Gerar as análises com o Genie (sobre a sua metric view)
Logo após criar, escolha a opção **"Create a Dashboard with Genie"** e cole **este prompt** (troque `<seu_db>` pelo seu database pessoal):

```text
Utilizando a metric view mvw_churn do dbacademy.<seu_db>, crie análises de churn: um indicador (KPI) com a Taxa de Churn geral; um gráfico de barras com a Taxa de Churn por Plano, da maior para a menor; um gráfico de barras com a Taxa de Churn por Segmento; e um gráfico de linha com os Cancelamentos por Mês.
```

Resultados esperados (confira se batem):
- **KPI Taxa de Churn:** ≈ **27%** (540 cancelamentos em 2.000 clientes).
- **Por plano:** Básico **31,7%** · Padrão **27,4%** · Premium **22,5%** · Empresarial **15,7%** — quanto mais barato o plano, maior o churn.
- **Por segmento:** Consumidor **30,3%** · PME **23,9%** · Corporativo **16,6%**.
- **Cancelamentos por mês:** série mensal (2023–2025) com ~12 a 21 cancelamentos/mês.

> Repare: você montou 4 gráficos **sem escrever uma linha de SQL** — e usando a **medida que já tinha governado** no Ex. 3. É a fonte única da verdade virando painel.

### Passo 2.1 — Veja a metric view propagar no dashboard
Aqui está a grande vantagem de uma metric view: **mude a regra uma única vez e todos os gráficos que a usam mudam juntos.** Vamos transformar a `Taxa de Churn` de fração para percentual e ver o impacto — sem tocar em nenhum gráfico.

1. No menu lateral, vá em **Catalog → `dbacademy` → `<seu_db>` → Tables → `mvw_churn`**.
2. Logo acima, clique no botão **Edit**.
3. Selecione a measure chamada **`Taxa de Churn`**.
4. Altere a **Expressão** de `SUM(source.churn_flag) / COUNT(DISTINCT source.id_cliente)` para:
   ```
   100 * SUM(source.churn_flag) / COUNT(DISTINCT source.id_cliente)
   ```
5. Clique em **Save**.
6. Volte ao **Dashboard** e clique no botão de **refresh**.

O KPI e os gráficos de churn saltam de fração para percentual:

| | KPI | Básico | Padrão | Premium | Empresarial |
|---|---|---|---|---|---|
| **Antes** | 0,27 | 0,317 | 0,274 | 0,225 | 0,157 |
| **Depois** | 27 | 31,7 | 27,4 | 22,5 | 15,7 |

### Passo 2.2 — Adicionar 2 filtros
Peça os filtros ao Genie, no mesmo assistente. Cole **este prompt**:

```text
Adicione 2 filtros ao dashboard: um para Plano e outro para Segmento.
```

Ao escolher um valor em qualquer filtro, os gráficos se ajustam juntos.

## Passo 3 — Incluir o logo
Dê a cara do treinamento ao painel. No Canvas, adicione um widget de **Image** e, no campo de URL, cole:

```text
https://raw.githubusercontent.com/CaduBettanim/Databricks-Master-Training/main/05%20-%20Dashboards/logo_master_training.png
```

Posicione o logo no topo do dashboard, ocupando a largura da página. Com a imagem selecionada, no painel direito, na opção **Size** selecione **Fill**.

## Passo 4 — Mapa de churn por região (com o Genie)
Selecione o **Genie** de novo e peça um mapa. Cole **este prompt**:

```text
Inclua um mapa contendo a quantidade de assinaturas Canceladas por UF (região), usando as tabelas dbacademy.churn.fato_assinatura e dbacademy.churn.dim_cliente.
```

Esperado: um mapa do Brasil com os cancelamentos distribuídos entre ~10 UFs (as maiores: **PR, RJ, BA, SP, CE**).
