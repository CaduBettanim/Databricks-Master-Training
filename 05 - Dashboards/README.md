# 05 - Dashboards (AI/BI)

Transformar os dados de churn em um **painel executivo** — deixando o **Genie montar o dashboard inteiro a partir de um único prompt**. Você descreve as análises que quer, ele cria os datasets e os gráficos; você só ajusta e publica.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).

## Objetivo
Construir um dashboard **AI/BI** de retenção com:
- um **KPI** de taxa de churn;
- **churn por plano** e **por segmento**;
- **cancelamentos ao longo do tempo** e **motivos de cancelamento**;
- um **mapa** de churn por região;
- **3 filtros** (plano, segmento, motivo) que deixam o painel interativo;
- o **logo** do treinamento no topo.

---

## Passo 1 — Criar o dashboard
No menu lateral, **New → Dashboard** e clique em **Create Dashboard**.

## Passo 2 — Gerar as análises com o Genie
Logo após criar, escolha a opção **"Create a Dashboard with Genie"** e cole **este prompt** (é um só — o Genie monta os datasets e todos os gráficos de uma vez):

```text
Utilizando o dataset dbacademy.churn crie análises de churn. Inclua um indicador (KPI) com o percentual de assinaturas com status Cancelada sobre o total, Gráfico de barras com o percentual de assinaturas Canceladas por nome_plano, da maior para a menor, Gráfico de barras com o percentual de assinaturas Canceladas por segmento, Gráfico de linha com a quantidade de assinaturas Canceladas por mês, usando a data_fim, Gráfico de barras com a contagem de assinaturas Canceladas por motivo_cancelamento, da maior para a menor.
```

Resultados esperados (confira se batem):
- **KPI de churn:** ≈ **27%** (540 de 2.000 assinaturas).
- **Churn por plano:** Básico **31,7%** · Padrão **27,4%** · Premium **22,5%** · Empresarial **15,7%** — quanto mais barato o plano, maior o churn.
- **Churn por segmento:** Consumidor **30,3%** · PME **23,9%** · Corporativo **16,6%**.
- **Cancelamentos por mês:** série mensal (2023–2025) com ~12 a 21 cancelamentos/mês.
- **Motivos:** Insatisfação **196** · Preço **148** · Concorrência **104** · Atendimento **80** · Mudança de necessidade **12**.

> Você montou um dashboard inteiro **sem escrever uma linha de SQL** — só descrevendo as análises. É o mesmo espírito do Genie Code, agora para o painel.

### Passo 2.1 — Adicionar 3 filtros (também com o Genie)
Peça os filtros ao Genie, no mesmo assistente. Cole **este prompt**:

```text
Adicione 3 filtros ao dashboard: um para nome_plano, outro para segmento e outro para motivo_cancelamento.
```

Ao escolher um valor em qualquer filtro, **todos os gráficos** se ajustam juntos.

## Passo 3 — Incluir o logo
Dê a cara do treinamento ao painel. No Canvas, adicione um widget de **Image** e, no campo de URL, cole:

```text
https://raw.githubusercontent.com/CaduBettanim/Databricks-Master-Training/main/05%20-%20Dashboards/logo_master_training.png
```

Posicione o logo no topo do dashboard, ocupando a largura da página. Com a imagem selecionada, no painel direito, na opção **Size** selecione **Fill**.

> Prefere subir o arquivo em vez de usar a URL? Baixe o [`logo_master_training.png`](./logo_master_training.png) deste repositório e use **Upload** no widget de imagem.

## Passo 4 — Mapa de churn por região (com o Genie)
Selecione o **Genie** de novo e peça um mapa. Cole **este prompt**:

```text
Inclua um mapa contendo a quantidade de assinaturas Canceladas por UF (região).
```

Esperado: um mapa do Brasil com os cancelamentos distribuídos entre ~10 UFs (as maiores: **PR, RJ, BA, SP, CE**).

## Passo 5 — Publicar
Clique em **Publish** (canto superior direito). O dashboard publicado é o que você compartilha com o time de negócio — eles interagem com os filtros sem precisar do editor.

---

## Explore
Um dashboard AI/BI não é só um relatório: ele nasceu de uma frase, e os filtros deixam qualquer pessoa de negócio explorar sozinha. No Ex. 07 vamos dar um passo além — deixar o time **perguntar em linguagem natural** com o Genie, sem nem abrir o painel.
