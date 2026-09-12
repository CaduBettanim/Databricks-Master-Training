# 05 - Dashboards (AI/BI)

Transformar os dados de churn em um **painel executivo** — deixando o **Genie montar os gráficos a partir de prompts** e **reaproveitando a metric view que você criou no Ex. 3**. Você descreve as análises, ele monta; você só ajusta e publica.

**Pré-requisitos:**
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- [Ex. 3 - Metric Views](../03%20-%20Metric%20Views) concluído — a sua metric view **`mvw_churn`** precisa existir no seu database pessoal (`dbacademy.<seu_db>`).

## Objetivo
Construir um dashboard **AI/BI** de retenção com:
- um **KPI** de taxa de churn;
- **churn por plano** e **por segmento**;
- **cancelamentos ao longo do tempo** e **motivos de cancelamento**;
- um **mapa** de churn por região;
- **3 filtros** (plano, segmento, motivo) que deixam o painel interativo;
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

### Passo 2.1 — Adicionar o gráfico de motivos
Esse corte não está na metric view (ela não tem a dimensão de motivo), então peça ao Genie a partir da tabela. Cole **este prompt**:

```text
Adicione um gráfico de barras com a contagem de assinaturas Canceladas por motivo_cancelamento, da maior para a menor, usando a tabela dbacademy.churn.fato_assinatura.
```
Esperado: Insatisfação **196** · Preço **148** · Concorrência **104** · Atendimento **80** · Mudança de necessidade **12**.

### Passo 2.2 — Adicionar 3 filtros
Peça os filtros ao Genie, no mesmo assistente. Cole **este prompt**:

```text
Adicione 3 filtros ao dashboard: um para Plano, outro para Segmento e outro para motivo_cancelamento.
```

Ao escolher um valor em qualquer filtro, os gráficos se ajustam juntos.

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
Um dashboard AI/BI não é só um relatório: ele nasceu de uma frase, reusou a métrica governada do Ex. 3, e os filtros deixam qualquer pessoa de negócio explorar sozinha. No Ex. 07 vamos dar um passo além — deixar o time **perguntar em linguagem natural** com o Genie, sem nem abrir o painel.
