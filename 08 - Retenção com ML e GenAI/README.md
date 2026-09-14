# 08 - Retenção com ML e GenAI

Até aqui você **detectou** quem está em risco (dashboards + modelo do Ex. 7) e **diagnosticou** o porquê (IA + agentes). Agora vamos **agir**: criar as funções que, a partir de um `id_cliente`, montam a oferta de retenção certa e geram um **e-mail marketing personalizado** — e vamos criá-las **conversando com o Genie Code**, sem escrever SQL na mão.

O pulo do gato deste módulo: as **regras de negócio ficam governadas no Unity Catalog** — reutilizáveis pelo app (Ex. 9), pelo Genie e por qualquer agente — e a **IA só escreve o texto**, sem decidir a oferta.

**Pré-requisitos:**
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- Seu **database pessoal** criado (Passo 0 do [Ex. 1](../01%20-%20SQL%20com%20IA)).
- **[Ex. 7 - Previsão de Churn (ML)](../07%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29)** concluído — precisamos da tabela `churn_scores` no seu schema.

## Objetivo
Criar **duas UC Functions no seu schema** `dbacademy.<seu_db>`, usando o **Genie Code** (o assistente ✨ do SQL Editor):
- **`get_cliente_360(id)`** — passa o id do cliente, recebe o **perfil dele** (cadastro + risco);
- **`gerar_email_retencao(id)`** — passa o id, recebe o **e-mail de retenção pronto**, com a oferta certa aplicada.

> **Por que funções, e não SQL solto no app?** Uma função vira um **ativo governado** do Unity Catalog: o app fica fino (só chama a função), o acesso é controlado (EXECUTE) e a mesma lógica é reutilizada por outras ferramentas. É a diferença entre "cada um faz do seu jeito" e "uma regra única, governada".

---

## Passo 0 — Seu database
As funções são criadas **no SEU schema** `dbacademy.<seu_db>`. Use o mesmo database dos Ex. 1 e Ex. 7. Nos prompts abaixo, troque **`<seu_db>`** pelo seu database.

## Passo 1 — As regras de retenção
A oferta é montada por **três regras de negócio**. Elas usam só dados que já temos — inclusive o `fator_principal` que o **modelo do Ex. 7** calculou:

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

## Passo 2 — Peça ao Genie Code para criar as funções
Abra o **SQL Editor**, ative o **Genie Code** (✨) e cole o prompt abaixo (troque `<seu_db>`). O Genie vai explorar as tabelas, gerar o `CREATE FUNCTION` das **duas** funções — **revise** o SQL e clique em **Run**:

```text
Crie duas UC Functions (funções SQL) no schema dbacademy.<seu_db>, usando as tabelas dbacademy.churn.dim_cliente e dbacademy.<seu_db>.churn_scores unidas por id_cliente.

1) get_cliente_360(p_id STRING): função de tabela que retorna o perfil do cliente cujo id_cliente = p_id — nome_cliente, cidade, uf, segmento, canal_aquisicao, data_cadastro (de dim_cliente) e nome_plano, preco_mensal, prob_churn, faixa_risco, fator_principal (de churn_scores).

2) gerar_email_retencao(p_id STRING): função de tabela que retorna uma coluna email com um e-mail de retenção personalizado em português. Calcule em SQL com CASE três ofertas e depois use ai_query('databricks-meta-llama-3-3-70b-instruct', ...) para redigir o e-mail citando nome, cidade e anos de casa, oferecendo exatamente: (a) desconto de 15% se o cliente tem 5 anos ou mais de casa (calcule por data_cadastro com datediff), senão 10%; (b) se nome_plano = 'Básico' então 10GB de internet grátis, senão o dobro da internet + WhatsApp ilimitado; (c) conforme fator_principal: 'Insatisfação (CSAT)' -> gerente de conta dedicado, 'Inadimplência' -> renegociação da fatura sem juros, 'Baixo uso' -> sessão gratuita de treinamento, caso contrário -> ligação com um especialista.
```

> **Repare no que o Genie faz sozinho:** ele consulta `dim_cliente` e `churn_scores`, descobre os valores de `fator_principal` e `nome_plano`, e monta os `CASE` certos — você só descreveu as regras. Se ele assumir um setor específico (ex.: "telecom"), acrescente ao prompt *"empresa de assinatura genérica, não cite o setor"*.

## Passo 3 — Testar `get_cliente_360`
```sql
SELECT * FROM dbacademy.<seu_db>.get_cliente_360('C01575');
```
Resultado (a cliente **Marina Ribeiro**):

| nome | cidade/uf | cliente desde | plano | risco | fator principal |
|------|-----------|---------------|-------|-------|-----------------|
| Marina Ribeiro | Fortaleza/CE | 2021 | Básico (R$ 49,90) | **Alto** | Insatisfação (CSAT) |

## Passo 4 — Testar `gerar_email_retencao` e conferir as regras
```sql
SELECT email FROM dbacademy.<seu_db>.gerar_email_retencao('C01575');
```
E-mail gerado para a **Marina** (5 anos · Básico · Insatisfação):
> *"Olá Marina Ribeiro… é um prazer ter você conosco **há 5 anos**… em **Fortaleza**… um **desconto de 15%** na sua fatura… **10GB de internet grátis**… **gerente de conta dedicado**…"*

Agora teste um cliente do **outro lado** das regras:
```sql
SELECT email FROM dbacademy.<seu_db>.gerar_email_retencao('C00018');
```
É a **Gabriela Cardoso** (4 anos · Empresarial · Inadimplência) — e o e-mail muda sozinho:

| Cliente | Tempo | Plano | Motivo | E-mail oferece |
|---------|-------|-------|--------|----------------|
| Marina (C01575) | 5 anos | Básico | Insatisfação | 15% · 10GB grátis · gerente dedicado |
| Gabriela (C00018) | 4 anos | Empresarial | Inadimplência | **10%** · **dobro + WhatsApp** · **renegociação sem juros** |

Leia os dois e-mails lado a lado: a mesma função, ofertas diferentes, cada uma correta para o cliente.

> **A lição:** a **regra de negócio é governada** (SQL, verificável, igual para todos), a **IA cuida só da linguagem**. Você nunca fica refém de a IA "inventar" um desconto — e criou tudo isso **só descrevendo o que queria** ao Genie Code.

## 🎯 Desafio
Peça ao Genie Code para adicionar uma **quarta regra**. Ideias:
- clientes do segmento **Corporativo** ganham um **canal de suporte exclusivo**;
- risco **Alto** ganha um **bônus extra** (ex.: 1 mês grátis) que o risco Médio não recebe.

Descreva a nova regra no prompt, deixe o Genie recriar a função (`CREATE OR REPLACE`) e confira o resultado em dois clientes.

## Explore
Você acabou de construir o **motor de ação** da retenção: dado um cliente em risco, sai a oferta certa e o e-mail pronto — com a regra de negócio governada e a IA só na escrita. No **próximo módulo (Ex. 9 - Criação de Apps)**, o app **Central de Retenção** vai chamar exatamente essas duas funções: o atendente digita o id, vê o perfil e o risco, e clica para gerar o e-mail.
