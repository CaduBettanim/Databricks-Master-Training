# 07 - Genie (Perguntas em linguagem natural)

Até aqui **você** montou as análises. Agora vamos abrir isso para o time de negócio: um **Genie Space** onde qualquer pessoa **pergunta em português** — *"qual a taxa de churn por plano?"* — e o Genie escreve o SQL, executa e responde, com tabela e gráfico. Zero código.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).

## Objetivo
Criar um Genie Space sobre a base de churn, dar a ele um **contexto de negócio** e validar que ele responde bem a perguntas do dia a dia da retenção.

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

## Passo 2 — Dar contexto ao Genie
Em **Instructions** (Instruções gerais), cole o texto abaixo. É o que faz o Genie "falar a língua do negócio" e não errar as regras:

```text
Este espaço analisa o churn (cancelamento) de clientes de uma empresa de assinatura. Em fato_assinatura, churn_flag = 1 indica cliente que cancelou e a coluna status vale 'Ativa' ou 'Cancelada'. Taxa de churn = número de cancelamentos dividido pelo total. A receita vem de fato_faturamento.valor e a inadimplência ocorre quando pago = false. A satisfação está em fato_ticket_suporte (csat de 1 a 5, nps de 0 a 10). Trate 'cancelamento' e 'churn' como sinônimos.
```

## Passo 3 — Perguntar
Faça as perguntas abaixo (uma por vez) e confira as respostas. Repare que você **não diz de qual tabela** — o Genie descobre.

```text
Qual a taxa de churn por plano?
```
Esperado: Básico **31,65%** · Padrão **27,44%** · Premium **22,55%** · Empresarial **15,74%**.

```text
Quais os principais motivos de cancelamento?
```
Esperado: Insatisfação **196** (36,3%) · Preço **148** (27,4%) · Concorrência **104** · Atendimento **80** · Mudança de necessidade **12**.

```text
Qual o CSAT médio por categoria de ticket?
```
Esperado: Dúvida **4,08** · Cobrança **2,99** · Técnico **2,28** · Cancelamento **2,27**.

```text
Qual a receita total e o percentual de inadimplência por segmento?
```
Esperado: Consumidor **R$ 3,62 mi** / **6,79%** · PME **R$ 1,80 mi** / **6,84%** · Corporativo **R$ 680 mil** / **6,91%**.

> Cada resposta traz o **SQL usado** e um **gráfico** — clique para ver como o Genie chegou ao número. Se algo vier estranho, ajuste as **Instructions**: é lá que você ensina o Genie.

## 🎯 Desafio
O Genie também pode responder sobre o **futuro**. Adicione a sua tabela `dbacademy.<seu_db>.churn_scores` (do [Ex. 6](../06%20-%20Modelo%20de%20Churn)) ao Space e pergunte, em linguagem natural, **quantos clientes estão em risco alto e qual o principal fator de risco**.

## Explore
Você acabou de entregar autoatendimento de dados: o time pergunta e recebe resposta com número, SQL e gráfico — sem depender de ninguém escrever query. Nos próximos módulos o Genie deixa de ser só um espaço de perguntas e vira uma **peça de um agente** maior (Knowledge Assistant e Supervisor), que combina dados, documentos e ações.
