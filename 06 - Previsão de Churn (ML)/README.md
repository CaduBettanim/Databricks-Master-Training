# 06 - Previsão de Churn (ML)

![Trilha do Master Training com destaque no que foi construído até o Exercício 06](../assets/06%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Agora vamos treinar um modelo que estima a probabilidade de cada cliente cancelar e transformar isso em uma **tabela de scores** pronta para usar. Este é o exercício-ponte: o score que você gera aqui alimenta as dashboards, os agentes e o app de retenção dos próximos módulos.

**Pré-requisitos:**
- [Ex. 1 - SQL com IA](../01%20-%20SQL%20com%20IA)
- [Ex. 5 - Dashboards com IA](../05%20-%20Dashboards%20com%20IA) (para o Desafio)

## Objetivo
A partir da tabela de features `dbacademy.churn.feature_churn` (comportamento de uso, atraso de pagamento, satisfação), treinar um modelo de classificação, registrá-lo no Unity Catalog e pontuar todos os clientes. Ao final você terá, no seu schema:
- **`modelo_churn`**: o modelo governado, registrado no Unity Catalog
- **`churn_scores`**: a tabela de scores com `prob_churn`, `faixa_risco` (Alto/Médio/Baixo) e o `fator_principal` por trás do risco

> Não escrevemos ML na mão célula a célula: o notebook já traz o fluxo pronto e explicado. O foco é gerar o ativo (modelo + scores), não programar o treino.

---

## Passo 1: Rodar o notebook
1. Importe o notebook: **Workspace → Três pontinhos no topo → Import → URL**, e cole o seguinte:
```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/06%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29/notebook_modelo_churn.py
```
2. Após clicar em **Import**, você será redirecionado para o notebook
3. No dropdown na barra superior, ao lado de **Run all**, selecione o cluster `dbacademy_workshop_cluster`
4. Rode as células em ordem até a primeira célula de código abaixo de **Passo 1 — Configure o seu schema**, que exibe o widget
5. No widget **Seu schema**, selecione o schema que você criou no Ex. 1
6. Clique em **Run all**

Em ~2 minutos o notebook instala as bibliotecas, treina, registra o modelo e grava a tabela de scores.

## Passo 2: Conferir o resultado
No fim do notebook, confira:
- **AUC (teste): ≈ 0,97**: o modelo separa bem quem cancela de quem fica
- Distribuição de risco (`churn_scores`):

  | Faixa | Clientes | Prob. média |
  |-------|----------|-------------|
  | Alto  | ~492     | ~0,82       |
  | Médio | ~133     | ~0,36       |
  | Baixo | ~1.375   | ~0,06       |

- Fator principal de cada cliente em risco: *Insatisfação (CSAT)*, *Baixo uso*, *Inadimplência* ou *Detrator (NPS)*, a "explicação de negócio" que vai aparecer no app

Depois, veja os objetos criados no seu schema:
1. No menu lateral à esquerda, vá em **Catalog → `dbacademy` → `<seu_schema>`**
2. Em **Models**, abra o `modelo_churn`
3. Em **Tables**, abra a tabela `churn_scores`

## 🎯 Desafio
Volte à sua dashboard `Análise de Churn <seu_schema>` e gere uma nova análise: usando as tabelas `dbacademy.<seu_schema>.churn_scores` e `dbacademy.churn.dim_cliente`, crie indicadores e visualizações relevantes sobre a previsão de churn.

Assim a mesma dashboard passa a ter uma aba de **retrospectiva** (o churn que aconteceu, do Ex. 5) e uma de **previsão** (quem está em risco agora).

## Explore
Você acabou de criar o coração da operação de retenção: um score de risco por cliente, com o motivo por trás. Nos próximos módulos, esse ativo ganha vida: os agentes respondem sobre risco, e as dashboards e o app priorizam quem atender primeiro. Registrado no Unity Catalog, o `modelo_churn` fica pronto para ser publicado como endpoint de serving (com guardrail de PII) quando você quiser consultá-lo em tempo real.
