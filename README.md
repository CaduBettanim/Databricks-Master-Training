# Databricks Master Training — Análise de Clientes & Churn

Treinamento hands-on na plataforma Databricks que leva o participante **do SQL self-service aos agentes de IA**, sempre sobre um mesmo desafio de negócio: **entender e reduzir o churn** (cancelamento) de clientes.

## Objetivo

Capacitar times de **negócio e dados** a usar a plataforma Databricks de ponta a ponta — em modo **low-code** — para responder a uma pergunta real: *por que os clientes cancelam e como retê-los?*

Ao longo da trilha, o participante:
- consulta e modela dados de churn (SQL, Metric Views);
- aplica **IA Generativa** sobre texto (tickets de suporte);
- cria dashboards e **agentes conversacionais (Genie)**;
- treina um **modelo de churn** e o serve com governança;
- orquestra tudo em um **agente supervisor** e entrega um **app** de retenção.

O domínio é uma **empresa de assinatura genérica**, então a trilha se adapta a qualquer cliente/indústria. Todo o conteúdo é **reproduzível em qualquer workspace** — os dados vêm de CSVs versionados neste repositório.

## Arquitetura de dados

- **Base compartilhada** (schema `churn`, somente leitura): criada uma vez no Setup e usada por toda a turma.
- **Schema pessoal por participante** (`<catálogo>.<seu_database>`): recebe o que cada um cria nos exercícios (metric views, modelo, funções, etc.).
- Objetos de workspace (Genie, Knowledge Assistant, Supervisor, App) são criados por participante.

## Trilha

| Módulo | Conteúdo |
|--------|----------|
| **00 - Setup** | Preparação da base compartilhada de churn (dados + documentação + base de conhecimento). Começe por aqui. |
| **01 - Consultas SQL com Genie Code** | Explorar a base no SQL Editor e gerar SQL com o assistente (Genie Code). |
| **02 - Geração de Alertas** | Criar alertas que disparam quando um indicador de churn cruza um limite. |
| **03 - Metric Views** | Definir métricas governadas (churn, receita, suporte) e consultá-las com MEASURE(). |
| **04 - AI Functions** | IA Generativa no SQL sobre os tickets: sentimento, classificação, PII e resumo. |
| *(próximos)* | Dashboards · Modelo de churn · Genie · Discovery · Knowledge Assistant · Supervisor · App |

## Como começar

Abra a pasta **[`00 - Setup`](./00%20-%20Setup)** e siga o `README.md` de lá.
