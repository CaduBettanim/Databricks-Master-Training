# 07 - Genie (Perguntas em linguagem natural)

Até aqui **você** montou as análises. Agora abrimos isso para o time de negócio: um **Genie Space** onde qualquer pessoa **pergunta em português** — *"qual a taxa de churn por plano?"* — e o Genie escreve o SQL, executa e responde. Zero código.

Mas tem uma lição no meio do caminho: **o Genie é tão bom quanto o contexto que você dá a ele.** Nas regras de mercado ele acerta sozinho; nas regras **da sua empresa**, ele chuta — até você ensinar.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).

## Objetivo
Criar um Genie Space sobre a base de churn, ver o Genie acertando perguntas do dia a dia, **flagrar ele errando uma regra de negócio** que ele não tem como adivinhar e, então, **ensinar a regra** e vê-lo acertar.

---

## Passo 1 — Criar o Genie Space
1. No menu lateral, **Genie → New** (ou **New → Genie space**).
2. Em **Data**, adicione as tabelas da base compartilhada:
   - `dbacademy.churn.dim_cliente`
   - `dbacademy.churn.dim_plano`
   - `dbacademy.churn.fato_assinatura`
   - `dbacademy.churn.fato_faturamento`
   - `dbacademy.churn.fato_ticket_suporte`
   - `dbacademy.churn.fato_uso`

> O Genie já **infere os relacionamentos** entre os fatos e a `dim_cliente` — não precisa configurar joins na mão.

## Passo 2 — Perguntas que ele acerta de cara
Faça as perguntas abaixo (uma por vez). Repare que você **não diz de qual tabela** — o Genie descobre, e ainda mostra o SQL e um gráfico.

```text
Qual a taxa de churn por plano?
```
Esperado: Básico **31,65%** · Padrão **27,44%** · Premium **22,55%** · Empresarial **15,74%**.

```text
Quais os principais motivos de cancelamento?
```
Esperado: Insatisfação **196** · Preço **148** · Concorrência **104** · Atendimento **80** · Mudança de necessidade **12**.

## Passo 3 — A pergunta que ele erra
Agora uma pergunta que depende de uma regra **da sua empresa**: o **ano fiscal**. Pergunte:

```text
Qual a média de NPS do ano fiscal de 2024 no estado do Amazonas (AM)?
```
O Genie responde **≈ 7,3** — mas repare na explicação dele: *"não há definição de ano fiscal, então interpretei como o ano-calendário (jan–dez de 2024)"*. Ele **chutou** que ano fiscal = ano civil. Ninguém disse a ele quando começa o seu ano fiscal.

## Passo 4 — Ensine a regra e veja ele acertar
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

## 🎯 Desafio
O Genie também pode responder sobre o **futuro**. Adicione a sua tabela `dbacademy.<seu_db>.churn_scores` (do [Ex. 6](../06%20-%20Modelo%20de%20Churn)) ao Space e pergunte, em linguagem natural, **quantos clientes estão em risco alto e qual o principal fator de risco**.

## Explore
Você entregou autoatendimento de dados **com governança**: o time pergunta em português e recebe número, SQL e gráfico — e as regras do negócio ficam registradas no Space, não na cabeça de uma pessoa. Nos próximos módulos o Genie deixa de ser só um espaço de perguntas e vira **peça de um agente** maior (Knowledge Assistant e Supervisor), que combina dados, documentos e ações.
