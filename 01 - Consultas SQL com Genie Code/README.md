# 01 - Consultas SQL com Genie Code

Primeiro contato com os dados de churn: explorar no **SQL Editor** e usar o **Genie Code** (assistente de IA ✨) para gerar consultas em linguagem natural.

**Pré-requisito:** [Setup](../00%20-%20Setup) concluído — a base `dbacademy.churn` deve existir.

## Objetivo
- Navegar no SQL Editor e consultar a base compartilhada `dbacademy.churn`.
- Deixar o **Genie Code** escrever SQL a partir de perguntas em português.
- Conhecer recursos Delta (histórico, time travel).

> As consultas prontas estão em [`consultas.sql`](./consultas.sql). Ajuste o catálogo se você não usou `dbacademy`.

---

## Passo 0 — Crie o seu database pessoal
Você lê a base compartilhada `dbacademy.churn`, mas o que **você criar** (a partir do Ex. 3) vai no **seu** schema. Convenção: 1ª letra do nome + sobrenome (ex.: *João Silva* → `jsilva`).
```sql
CREATE SCHEMA IF NOT EXISTS dbacademy.<seu_db>;
```

## Passo 1 — Abrir o SQL Editor
No menu lateral, **SQL Editor**. No seletor de contexto, escolha o catálogo `dbacademy` e o schema `churn`.

## Passo 2 — Consultas guiadas
Rode uma a uma e observe os resultados:

**2.1 Clientes por segmento**
```sql
SELECT segmento, COUNT(*) AS clientes
FROM dbacademy.churn.dim_cliente
GROUP BY segmento ORDER BY clientes DESC;
```
**2.2 Assinaturas ativas x canceladas** · **2.3 Top motivos de cancelamento** · **2.4 Taxa de churn por segmento** — ver [`consultas.sql`](./consultas.sql).

## Passo 3 — Genie Code: gerar SQL em linguagem natural

O **Genie Code** é o assistente do SQL Editor que **escreve o código SQL** para você — diferente da **Genie** (espaço conversacional, Ex. 7), que *responde perguntas*. Aqui o foco é **montar consulta**.

> **Regra de ouro (para todos gerarem o mesmo resultado):** **nomeie sempre a tabela**. Não precisa listar as colunas — os comentários que documentamos no Setup fazem a IA acertar. Só acrescente um detalhe quando houver ambiguidade real: **qual data** (há mais de uma), o **limiar** de um termo vago, ou a **definição** de uma métrica aberta.

Abra o assistente (✨) no SQL Editor e peça, **um de cada vez** (revise o SQL gerado e execute):

1. `Escreva o SQL da taxa de churn por segmento usando a tabela dbacademy.churn.feature_churn.`
2. `Escreva uma query com os 5 principais motivos de cancelamento usando a dbacademy.churn.fato_assinatura.`
3. `Escreva a taxa de churn por plano usando dbacademy.churn.fato_assinatura e dbacademy.churn.dim_plano.`
4. `Conte quantas assinaturas foram canceladas por mês usando dbacademy.churn.fato_assinatura, considerando a data de cancelamento (data_fim).`
5. `Liste os 10 clientes com mais tickets de csat <= 2 na dbacademy.churn.fato_ticket_suporte, usando window function para o ranking.`

**Editar e entender o código gerado** (isto é o diferencial do Genie Code — não é Q&A):
- `explique esta consulta`
- `otimize esta consulta`
- `adicione um filtro para o segmento Corporativo`

> **⚠️ Contra-exemplo — por que ser objetivo:** peça `Liste os clientes em risco.` Sem uma definição, a IA **inventa os critérios** (limiares diferentes a cada execução) e o resultado **varia por aluno**. Lição: seja específico. A definição de "risco" virá depois — das **instruções da Genie** (Ex. 7) e do **modelo de churn** (Ex. 6).

## Passo 4 (bônus) — Recursos Delta (somente leitura)
```sql
DESCRIBE HISTORY dbacademy.churn.fato_assinatura;
DESCRIBE DETAIL  dbacademy.churn.dim_cliente;
SELECT COUNT(*) FROM dbacademy.churn.fato_assinatura VERSION AS OF 0;  -- time travel
```
> A base compartilhada é **somente leitura** — não use `ALTER`/`UPDATE` aqui. Você vai criar e alterar objetos no **seu** schema a partir do próximo módulo.

## 🎯 Desafio
**Qual plano tem a maior taxa de churn e quantos clientes perdeu?** Monte a consulta (dica: junte `fato_assinatura` com `dim_plano`), depois confira pedindo ao Genie Code.

---

## Resultados esperados (dataset fixo → valores exatos)

**Clientes por segmento:** Consumidor **1.200** · PME **595** · Corporativo **205**
**Assinaturas:** Ativa **1.460** · Cancelada **540**
**Top motivos:** Insatisfação **196** · Preço **148** · Concorrência **104** · Atendimento **80** · Mudança de necessidade **12**
**Taxa de churn por segmento:** Consumidor **0,303** · PME **0,239** · Corporativo **0,166**

**🎯 Desafio — churn por plano:**
| Plano | Taxa de churn | Clientes perdidos |
|-------|:---:|:---:|
| **Básico** | **0,317** | **257** |
| Padrão | 0,274 | 160 |
| Premium | 0,225 | 92 |
| Empresarial | 0,157 | 31 |

➡️ O plano **Básico** concentra o maior churn — coerente com o negócio (menor barreira de saída, menor valor percebido).
