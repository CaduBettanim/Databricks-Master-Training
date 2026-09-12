# 07 - Genie (Perguntas em linguagem natural)

Até aqui **você** montou as análises. Agora abrimos isso para o time de negócio: **Genie Spaces** onde qualquer pessoa **pergunta em português** — *"qual a receita por segmento?"* — e o Genie escreve o SQL, executa e responde. Zero código.

Vamos criar **dois Genies especializados** — um de **Faturamento** e um de **Suporte**. No próximo módulo, um **agente Supervisor** vai orquestrar os dois (mais um Knowledge Assistant), roteando cada pergunta para o especialista certo.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).

---

# Parte 1 — Genie de Faturamento

## Passo 1 — Criar o Space
1. No menu lateral, **Genie → New** (ou **New → Genie space**).
2. Em **Data**, adicione:
   - `dbacademy.churn.dim_cliente`
   - `dbacademy.churn.dim_plano`
   - `dbacademy.churn.fato_assinatura`
   - `dbacademy.churn.fato_faturamento`
3. Dê o nome **`Faturamento - <seu_db>`** (troque `<seu_db>`) — vamos usá-lo no próximo lab.

> O Genie **infere os relacionamentos** entre as tabelas — não precisa configurar joins na mão.

## Passo 2 — Perguntar
Faça as perguntas abaixo (uma por vez). Você **não diz de qual tabela** — o Genie descobre, e ainda mostra o SQL e um gráfico.

```text
Qual a receita total por segmento?
```
Esperado: Consumidor **R$ 3,62 mi** · PME **R$ 1,80 mi** · Corporativo **R$ 680 mil**.

```text
Qual o percentual de faturas não pagas por plano?
```
Esperado: Básico **7,90%** · Padrão **6,49%** · Premium **5,90%** · Empresarial **5,45%** — a inadimplência acompanha o churn: pior no Básico.

---

# Parte 2 — Genie de Suporte

## Passo 3 — Criar o Space
1. **Genie → New** de novo.
2. Em **Data**, adicione:
   - `dbacademy.churn.dim_cliente`
   - `dbacademy.churn.fato_ticket_suporte`
3. Dê o nome **`Suporte - <seu_db>`**.

## Passo 4 — Perguntar
```text
Qual o CSAT médio por categoria de ticket?
```
Esperado: Dúvida **4,08** · Cobrança **2,99** · Técnico **2,28** · Cancelamento **2,27**.

```text
Quantos tickets de suporte temos por canal?
```
Esperado: Chat **447** · Email **407** · Telefone **399**.

## Passo 5 — Faça a seguinte pergunta
```text
Qual a média de NPS do ano fiscal de 2024 no estado do Amazonas (AM)?
```
O Genie responde **≈ 7,3** — mas leia a explicação dele: *"não há definição de ano fiscal, então interpretei como o ano-calendário (jan–dez de 2024)"*. Ele **chutou** que ano fiscal = ano civil. Ninguém disse a ele quando começa o seu ano fiscal.

## Passo 6 — Ensine a regra e pergunte de novo
Em **Instructions** (Instruções gerais), cole a regra do seu ano fiscal:

```text
O ano fiscal (AF) da empresa vai de 1º de outubro a 30 de setembro do ano seguinte, identificado pelo ano em que começa. Exemplo: o AF2024 vai de 01/10/2024 a 30/09/2025. Sempre que a pergunta mencionar "ano fiscal", use esse período (com base em data_abertura), nunca o ano-calendário.
```

Faça **exatamente a mesma pergunta** de novo:

```text
Qual a média de NPS do ano fiscal de 2024 no estado do Amazonas (AM)?
```
Agora o Genie filtra **01/10/2024 a 30/09/2025** e responde **≈ 6,5** — número diferente, porque o período mudou. A mesma pergunta, duas respostas: a diferença foi **a regra que você deu**.

> É a mesma ideia da métrica governada do Ex. 3: **sem a regra explícita, a IA chuta**. As *Instructions* são onde você transforma o conhecimento do negócio em respostas confiáveis — e valem para todo mundo que usa o Space.
