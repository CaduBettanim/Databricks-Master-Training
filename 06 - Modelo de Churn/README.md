# 06 - Modelo de Churn

Treinar um modelo que estima a **probabilidade de cada cliente cancelar** e transformar isso em uma **tabela de scores** pronta para usar. Este é o exercício-**ponte**: o score que você gera aqui alimenta os dashboards, os agentes e o app de retenção dos próximos módulos.

**Pré-requisitos:**
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- Seu **database pessoal** criado (Passo 0 do [Ex. 1](../01%20-%20Consultas%20SQL%20com%20Genie%20Code)).

## Objetivo
A partir da tabela de features `dbacademy.churn.feature_churn` (comportamento de uso, atraso de pagamento, satisfação), treinar um modelo de classificação, **registrá-lo no Unity Catalog** e **pontuar todos os clientes**. Ao final você terá, no seu schema:
- **`modelo_churn`** — o modelo governado (que o Ex. 11 vai *servir* com governança);
- **`churn_scores`** — a tabela de scores: `prob_churn`, `faixa_risco` (Alto/Médio/Baixo) e o `fator_principal` por trás do risco.

> Não escrevemos ML na mão célula a célula: o notebook já traz o fluxo pronto e explicado. O foco é **gerar o ativo** (modelo + scores), não programar o treino.

---

## Passo 1 — Rodar o notebook
1. Importe o notebook por URL (**Workspace → Import → URL**):
   ```
   https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/06%20-%20Modelo%20de%20Churn/notebook_modelo_churn.py
   ```
2. Na célula do **Passo 1**, troque `<seu_db>` pelo **seu** database pessoal.
3. Anexe **Serverless** e clique em **Run all**.

Em ~2 minutos o notebook instala as bibliotecas, treina, registra o modelo e grava a tabela de scores.

## Passo 2 — Conferir o resultado
No fim do notebook, confira:
- **AUC (teste): ≈ 0,97** — o modelo separa bem quem cancela de quem fica.
- **Distribuição de risco** (`churn_scores`):

  | Faixa | Clientes | Prob. média |
  |-------|----------|-------------|
  | Alto  | ~492     | ~0,82       |
  | Médio | ~133     | ~0,36       |
  | Baixo | ~1.375   | ~0,06       |

- **Fator principal** de cada cliente em risco: *Insatisfação (CSAT)*, *Baixo uso*, *Inadimplência* ou *Detrator (NPS)* — a "explicação de negócio" que vai aparecer no app.

Navegue no seu catálogo e veja o **`modelo_churn`** (em *Models*) e a tabela **`churn_scores`** (em *Tables*) criados no seu schema.

## Passo 3 — Levar a previsão para o dashboard
Agora que o score existe, leve-o para o painel que você criou no Ex. 5.
1. Abra o dashboard **`Análise de Churn <seu_db>`**.
2. No rodapé, crie uma **nova aba** (nova página).
3. Selecione o **Genie** e cole **este prompt** (troque `<seu_db>`):

```text
Usando as tabelas dbacademy.<seu_db>.churn_scores e dbacademy.churn.dim_cliente, crie indicadores e visualizações sobre a previsão de churn: um KPI com a quantidade de clientes em risco Alto (faixa_risco igual a 'Alto'); um KPI com o MRR em risco (soma de preco_mensal dos clientes com faixa_risco 'Alto'); um gráfico de barras com a quantidade de clientes por faixa_risco; um gráfico de barras com a quantidade de clientes por fator_principal, da maior para a menor; um gráfico de barras com a probabilidade média de churn (prob_churn) por segmento; e uma tabela com os 10 clientes de maior prob_churn, mostrando nome_cliente, segmento, nome_plano, preco_mensal, prob_churn e fator_principal.
```

Resultados esperados:
- **Clientes em risco Alto:** ~**492**; **MRR em risco:** ~**R$ 45.971**.
- **Por faixa:** Baixo ~1.375 · Alto ~492 · Médio ~133.
- **Fator principal:** Insatisfação (CSAT) ~658 · Baixo uso ~557 · Inadimplência ~520 · Detrator (NPS) ~265.
- **Prob. média por segmento:** Consumidor ~0,30 · PME ~0,23 · Corporativo ~0,17.

Pronto: o mesmo dashboard agora tem uma aba de **retrospectiva** (o churn que aconteceu, do Ex. 5) e uma de **previsão** (quem está em risco agora).

## Explore
Você acabou de criar o coração da operação de retenção: um score de risco por cliente, com o motivo por trás. Nos próximos módulos, esse ativo ganha vida — os **agentes** respondem sobre risco e os dashboards e o **app** priorizam quem atender primeiro. No **Ex. 11** o `modelo_churn` é publicado como **endpoint** (com guardrail de PII) para ser consultado em tempo real.
