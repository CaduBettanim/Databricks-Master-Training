# 08 - Retenção com ML e GenAI

Até aqui você **detectou** quem está em risco (dashboards + modelo do Ex. 7) e **diagnosticou** o porquê (IA + agentes). Agora vamos **agir**: criar as funções que, a partir de um `id_cliente`, montam a oferta de retenção certa e geram um **e-mail marketing personalizado**.

O pulo do gato deste módulo: as **regras de negócio ficam governadas no Unity Catalog** — reutilizáveis pelo app (Ex. 9), pelo Genie e por qualquer agente — e a **IA só escreve o texto**, sem decidir a oferta.

**Pré-requisitos:**
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- Seu **database pessoal** criado (Passo 0 do [Ex. 1](../01%20-%20SQL%20com%20IA)).
- **[Ex. 7 - Previsão de Churn (ML)](../07%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29)** concluído — precisamos da tabela `churn_scores` no seu schema.

## Objetivo
Criar **duas UC Functions no seu schema** `dbacademy.<seu_db>`:
- **`get_cliente_360(id)`** — passa o id do cliente, recebe o **perfil dele** (cadastro + risco);
- **`gerar_email_retencao(id)`** — passa o id, recebe o **e-mail de retenção pronto**, com a oferta certa aplicada.

Todas as consultas estão em [`funcoes_retencao.sql`](./funcoes_retencao.sql).

> **Por que funções, e não SQL solto no app?** Uma função vira um **ativo governado** do Unity Catalog: o app fica fino (só chama a função), o acesso é controlado (EXECUTE) e a mesma lógica é reutilizada por outras ferramentas. É a diferença entre "cada um faz do seu jeito" e "uma regra única, governada".

---

## Passo 0 — Seu database
Todas as funções são criadas **no SEU schema**. No arquivo `.sql`, troque **`<seu_db>`** pelo seu database pessoal (o mesmo do Ex. 1 e Ex. 7) em **todas** as ocorrências.

## Passo 1 — `get_cliente_360`: do id ao perfil
Abra o **SQL Editor** e rode o `CREATE FUNCTION` da função 1 (está no `.sql`). Depois teste:
```sql
SELECT * FROM dbacademy.<seu_db>.get_cliente_360('C01575');
```
Resultado (a cliente **Marina Ribeiro**):

| nome | cidade/uf | cliente desde | plano | risco | fator principal |
|------|-----------|---------------|-------|-------|-----------------|
| Marina Ribeiro | Fortaleza/CE | 2021 | Básico (R$ 49,90) | **Alto** | Insatisfação (CSAT) |

> A função **junta** o cadastro (`dbacademy.churn.dim_cliente`) com o **seu** score (`dbacademy.<seu_db>.churn_scores`). Um único ponto de entrada para "tudo sobre o cliente".

## Passo 2 — As regras de retenção
A oferta é montada por **três regras de negócio**. Repare que elas usam só dados que já temos — inclusive o `fator_principal` que o **modelo do Ex. 7** calculou:

| Regra | Condição | Oferta |
|-------|----------|--------|
| **Tempo de casa** | 5 anos ou mais | desconto de **15%** na fatura |
| | menos de 5 anos | desconto de **10%** |
| **Plano** | Básico | **10GB** de internet grátis |
| | acima do Básico | **dobro** da internet + WhatsApp ilimitado |
| **Motivo do risco** | Insatisfação (CSAT) | gerente de conta dedicado |
| | Inadimplência | renegociação da fatura sem juros |
| | Baixo uso | sessão gratuita de treinamento |
| | Detrator (NPS) | ligação com um especialista |

## Passo 3 — `gerar_email_retencao`: do perfil ao e-mail
Rode o `CREATE FUNCTION` da função 2. Dentro dela, as regras acima viram `CASE` em SQL: o **desconto e os benefícios são decididos pela regra**, e só a oferta pronta é entregue à IA. A IA (`ai_query`) apenas **redige** o e-mail.

```sql
SELECT email FROM dbacademy.<seu_db>.gerar_email_retencao('C01575');
```
E-mail gerado para a **Marina** (5 anos · Básico · Insatisfação):
> *"Olá Marina Ribeiro, é um prazer enorme ter você conosco **há 5 anos**… em **Fortaleza**… oferecendo: um **desconto de 15%** na sua fatura… **10GB de internet grátis** no seu celular… **atendimento prioritário com um gerente de conta dedicado**…"*

As três ofertas aparecem **exatamente** como a regra mandou. ✅

> **A lição:** a **regra de negócio é governada** (SQL, verificável, igual para todos), a **IA cuida só da linguagem**. Você nunca fica refém de a IA "inventar" um desconto.

## Passo 4 — Conferir que as regras funcionam de verdade
Teste um cliente do **outro lado** das regras:
```sql
SELECT email FROM dbacademy.<seu_db>.gerar_email_retencao('C00018');
```
Agora é a **Gabriela Cardoso** (4 anos · Empresarial · Inadimplência) — e o e-mail muda sozinho:

| Cliente | Tempo | Plano | Motivo | E-mail oferece |
|---------|-------|-------|--------|----------------|
| Marina (C01575) | 5 anos | Básico | Insatisfação | 15% · 10GB grátis · gerente dedicado |
| Gabriela (C00018) | 4 anos | Empresarial | Inadimplência | **10%** · **dobro + WhatsApp** · **renegociação sem juros** |

Leia os dois e-mails lado a lado: a mesma função, ofertas diferentes, cada uma correta para o cliente.

## 🎯 Desafio
Adicione uma **quarta regra**. Ideias:
- clientes do segmento **Corporativo** ganham um **canal de suporte exclusivo**;
- risco **Alto** ganha um **bônus extra** (ex.: 1 mês grátis) que o risco Médio não recebe.

Edite o `CASE` na função, recrie (`CREATE OR REPLACE`) e confira o resultado em dois clientes.

## Explore
Você acabou de construir o **motor de ação** da retenção: dado um cliente em risco, sai a oferta certa e o e-mail pronto — com a regra de negócio governada e a IA só na escrita. No **próximo módulo (Ex. 9 - Criação de Apps)**, o app **Central de Retenção** vai chamar exatamente essas duas funções: o atendente digita o id, vê o perfil e o risco, e clica para gerar o e-mail.
