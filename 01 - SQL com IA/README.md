# 01 - SQL com IA

![Trilha do Master Training com destaque no que foi construído até o Exercício 01](../assets/01%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Seu primeiro contato com os dados de churn: você vai explorar no **SQL Editor** e usar o **Genie Code** para gerar consultas através de linguagem natural.

## Objetivo
- Navegar no SQL Editor e consultar a base compartilhada `dbacademy.churn`
- Usar o Genie Code para escrever SQL a partir de perguntas em português
- Conhecer recursos do formato Delta (histórico, time travel)

> Você pode encontrar todas as consultas usadas aqui em [`consultas.sql`](./consultas.sql)

---

## Passo 0: Abrir o SQL Editor
No menu lateral à esquerda, selecione **SQL Editor**. Abaixo de **Create new**, clique em **SQL Query**.
No seletor de contexto ao lado de **Run all**, escolha o catálogo `dbacademy` e o schema `churn`, como a seguir:
![Imagem do catálogo+schema no SQL Editor](../assets/01%20-%20catálogo+schema%20no%20SQL%20Editor.png)

## Passo 1: Crie o seu database pessoal
Agora você deve criar o seu próprio _schema_, onde ficarão todas as bases que você criar a partir do Ex. 3.
Para o nome do schema, vamos seguir o padrão "1ª letra do nome + sobrenome" (ex.: João Silva → jsilva).
```sql
CREATE SCHEMA IF NOT EXISTS dbacademy.<seu_schema>;
```


## Passo 2: Consultas guiadas
Para cada uma das consultas a seguir:
1. Copie a consulta clicando no ícone de dois quadrados no canto de cada bloco
2. Cole a consulta no SQL Editor
3. Rode a consulta
4. Observe os resultados

**2.1 Clientes por segmento**
```sql
SELECT
    segmento,
    COUNT(*) AS clientes
FROM dbacademy.churn.dim_cliente
GROUP BY segmento
ORDER BY clientes DESC;
```

**2.2 Assinaturas ativas x canceladas**
```sql
SELECT
    status,
    COUNT(*) AS qtd
FROM dbacademy.churn.fato_assinatura
GROUP BY status
ORDER BY qtd DESC;
```

**2.3 Top motivos de cancelamento**
```sql
SELECT
    motivo_cancelamento,
    COUNT(*) AS qtd
FROM dbacademy.churn.fato_assinatura
WHERE churn_flag = 1
GROUP BY motivo_cancelamento
ORDER BY qtd DESC;
```

## Passo 3: Usando o Genie Code
O **Genie Code** é o assistente de desenvolvimento da Databricks, nós podemos utilizá-lo no SQL Editor para escrever consultas SQL através de linguagem natural. É diferente dos _Genie Agents_ que vamos tratar no Ex. 7, cujo objetivo é _responder perguntas e gerar insights_. Aqui o foco é montar a consulta.

Abra o Genie Code clicando na lâmpada no canto superior direito e cole um prompt de cada vez , revise o SQL gerado e execute:

**1. Taxa de churn por segmento**
```text
Escreva o SQL da taxa de churn por segmento usando a tabela dbacademy.churn.feature_churn.
```

<details>
<summary>👉 Resultado:</summary>

```sql
SELECT
    segmento,
    ROUND(AVG(churn_flag), 3) AS taxa_churn
FROM dbacademy.churn.feature_churn
GROUP BY segmento
ORDER BY taxa_churn DESC;
```

</details>

**2. Top 5 motivos de cancelamento**
```text
Escreva uma query com os 5 principais motivos de cancelamento das assinaturas canceladas (churn_flag = 1) usando a dbacademy.churn.fato_assinatura.
```

<details>
<summary>👉 Resultado:</summary>

```sql
SELECT
    motivo_cancelamento,
    COUNT(*) AS qtd
FROM dbacademy.churn.fato_assinatura
WHERE churn_flag = 1
GROUP BY motivo_cancelamento
ORDER BY qtd DESC
LIMIT 5;
```

</details>

**3. Taxa de churn por plano**
```text
Escreva a taxa de churn por plano usando dbacademy.churn.fato_assinatura e dbacademy.churn.dim_plano.
```

<details>
<summary>👉 Resultado:</summary>

```sql
SELECT
    p.nome_plano,
    ROUND(AVG(a.churn_flag), 3) AS taxa_churn
FROM dbacademy.churn.fato_assinatura a
JOIN dbacademy.churn.dim_plano p ON a.id_plano = p.id_plano
GROUP BY p.nome_plano
ORDER BY taxa_churn DESC;
```

</details>

**4. Cancelamentos por mês**
```text
Conte quantas assinaturas foram canceladas por mês usando dbacademy.churn.fato_assinatura, considerando apenas as canceladas (churn_flag = 1) pela data de cancelamento (data_fim).
```

<details>
<summary>👉 Resultado:</summary>

```sql
SELECT
    date_trunc('month', data_fim) AS mes,
    COUNT(*) AS cancelamentos
FROM dbacademy.churn.fato_assinatura
WHERE churn_flag = 1
GROUP BY 1
ORDER BY 1;
```

</details>

## 🎯 Desafio
Qual plano tem a maior taxa de churn e quantos clientes perdeu?

---

## Resultados esperados (dataset fixo → valores exatos)

**Clientes por segmento:**
- Consumidor **1.200**
- PME **595**
- Corporativo **205**

**Assinaturas:**
- Ativa **1.460**
- Cancelada **540**

**Top motivos:**
- Insatisfação **196**
- Preço **148**
- Concorrência **104**
- Atendimento **80** 
- Mudança de necessidade **12**

**Taxa de churn por segmento:**
- Consumidor **0,303**
- PME **0,239**
- Corporativo **0,166**

**🎯 Desafio (churn por plano):**
| Plano | Taxa de churn | Clientes perdidos |
|-------|:---:|:---:|
| **Básico** | **0,317** | **257** |
| Padrão | 0,274 | 160 |
| Premium | 0,225 | 92 |
| Empresarial | 0,157 | 31 |

➡️ O plano **Básico** concentra o maior churn, coerente com o negócio (menor barreira de saída, menor valor percebido).
