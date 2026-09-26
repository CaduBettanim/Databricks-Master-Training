# 05 - Dashboards com IA

![Trilha do Master Training com destaque no que foi construído até o Exercício 05](../assets/05%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Vamos transformar os dados de churn em um **painel executivo**: você deixa o **Genie** montar os gráficos a partir de prompts e reaproveita a metric view que criou no Ex. 3. Você descreve as análises, ele monta; você só ajusta e publica.

**Pré-requisitos:**
- [Ex. 1 - SQL com IA](../01%20-%20SQL%20com%20IA)
- [Ex. 3 - Métricas de Negócio](../03%20-%20M%C3%A9tricas%20de%20Neg%C3%B3cio)

## Objetivo
Construir uma dashboard **AI/BI** de retenção com:
- Um KPI de taxa de churn
- Churn por plano e por segmento
- Cancelamentos ao longo do tempo
- Um mapa de churn por região
- 2 filtros (plano, segmento) que deixam o painel interativo
- O logo do treinamento no topo

> As 4 primeiras análises saem direto da sua `mvw_churn`: a mesma medida governada que você definiu no Ex. 3, agora virando gráfico

---

## Passo 1: Criar a dashboard
1. No menu lateral à esquerda, clique em **Dashboards**
2. Clique em **Create Dashboard**

## Passo 2: Gerar as análises com o Genie (sobre a sua metric view)
Logo após criar a dashboard, cole este prompt no espaço para texto abaixo de **Create a dashboard with Genie**, trocando `<seu_schema>` pelo nome do seu schema:
```text
Utilizando a metric view mvw_churn do dbacademy.<seu_schema>, crie análises de churn: um indicador (KPI) com a Taxa de Churn geral; um gráfico de barras com a Taxa de Churn por Plano, da maior para a menor; um gráfico de barras com a Taxa de Churn por Segmento; e um gráfico de linha com os Cancelamentos por Mês.
```

Resultados esperados:

**KPI Taxa de Churn:** ≈ **27%** (540 cancelamentos em 2.000 clientes)

**Por plano:**
- Básico **31,7%**
- Padrão **27,4%**
- Premium **22,5%**
- Empresarial **15,7%**

**Por segmento:**
- Consumidor **30,3%**
- PME **23,9%**
- Corporativo **16,6%**

**Cancelamentos por mês:** série mensal (2023–2025) com ~12 a 21 cancelamentos/mês

Quanto mais barato o plano, maior o churn.

> Repare: você montou 4 gráficos sem escrever uma linha de SQL, usando a medida governada que já tinha criado no Ex. 3. É a fonte única da verdade virando painel.

### Passo 2.1: Veja a metric view propagar na dashboard
Vamos transformar a `Taxa de Churn` de fração para percentual, sem tocar em nenhum gráfico:
1. No menu lateral à esquerda, vá em **Catalog → `dbacademy` → `<seu_schema>` → Tables → `mvw_churn`**
2. Logo acima, clique no botão **Edit**
3. Selecione a measure chamada **`Taxa de Churn`**
4. Altere a **Expressão** de `SUM(source.churn_flag) / COUNT(DISTINCT source.id_cliente)` para:
    ```
    100 * SUM(source.churn_flag) / COUNT(DISTINCT source.id_cliente)
    ```
5. Clique em **Save**
6. Volte à dashboard e clique no botão de **refresh**

O KPI e os gráficos de churn saltam de fração para percentual:

| | KPI | Básico | Padrão | Premium | Empresarial |
|---|---|---|---|---|---|
| **Antes** | 0,27 | 0,317 | 0,274 | 0,225 | 0,157 |
| **Depois** | 27 | 31,7 | 27,4 | 22,5 | 15,7 |

Essa é a grande vantagem de uma metric view: você muda a regra uma única vez e todos os gráficos que a usam mudam juntos.

### Passo 2.2: Adicionar 2 filtros
No mesmo assistente do Genie, cole o prompt abaixo
```text
Adicione 2 filtros à dashboard: um para Plano e outro para Segmento.
```

Ao escolher um valor em qualquer filtro, os gráficos se ajustam juntos.

## Passo 3: Incluir o logo
1. Através do menu embaixo no painel, adicione um widget de **Image**
2. Clique em **use a URL** e cole o seguinte:
```text
https://raw.githubusercontent.com/CaduBettanim/Databricks-Master-Training/main/assets/logo_master_training.png
```
3. Posicione o logo no topo da dashboard, ocupando a largura da página

## Passo 4: Mapa de churn por região (com o Genie)
1. Selecione o **Genie** novamente
2. Cole o prompt abaixo
```text
Inclua um mapa contendo a quantidade de assinaturas canceladas por UF (região). Crie o campo uf_iso concatenando "BR-" com o uf, usando as tabelas dbacademy.churn.fato_assinatura e dbacademy.churn.dim_cliente.
```

Resultado esperado: um mapa do Brasil com os cancelamentos distribuídos entre ~10 UFs (as maiores: **PR, RJ, BA, SP, CE**).

## Passo 5: Nomear e publicar
1. Clique no título da dashboard, no topo da página, e renomeie para **`Análise de Churn <seu_schema>`**, trocando `<seu_schema>` pelo nome do seu schema
2. Clique em **Publish** no canto superior direito

A dashboard publicada é a que você compartilha com o time de negócio: eles interagem com os filtros sem precisar do editor.

> Vamos voltar a esse painel no Ex. 6
