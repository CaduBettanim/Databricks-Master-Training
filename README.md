# Databricks Master Training — Análise de Clientes & Churn

Treinamento hands-on na plataforma Databricks, do **SQL self-service** aos **agentes de IA**, tudo sobre um mesmo domínio: **retenção / churn** de uma empresa de assinatura (setor genérico, aplicável a qualquer cliente).

O treinamento é para o **time de negócio** (low-code) e é **reproduzível em qualquer workspace** — os dados vêm de CSVs deste repositório.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `data/` | CSVs de origem (dataset fixo, 1 por tabela) — carregados no Setup |
| `setup/` | Notebook de preparação da base compartilhada |

## Modelo de dados

Base compartilhada (schema `churn` dentro do catálogo escolhido, ex.: `dbacademy`):

| Tabela | Descrição |
|--------|-----------|
| `dim_cliente` | Clientes (segmento, cidade, canal, faixa etária) |
| `dim_plano` | Planos (Básico, Padrão, Premium, Empresarial) |
| `dim_data` | Calendário |
| `fato_assinatura` | Assinaturas com status e `churn_flag` |
| `fato_uso` | Uso mensal (logins, horas, funcionalidades) |
| `fato_faturamento` | Faturamento mensal (valor, atraso, inadimplência) |
| `fato_ticket_suporte` | Tickets de suporte em PT-BR com texto, CSAT e NPS |
| `feature_churn` | Tabela analítica por cliente (features comportamentais) para o modelo de churn — derivada no Setup |

Os dados têm **sinal de churn verificado**: uso baixo, atraso de pagamento e baixa satisfação elevam o cancelamento (corr. uso × churn ≈ -0,50). Isso garante que o modelo de ML aprenda de verdade.

## Setup (instrutor — roda 1x)

1. **Pré-requisito:** um catálogo Unity Catalog (por padrão `dbacademy`). Se ele não existir e não puder ser criado automaticamente (contas com *Default Storage*), crie-o pela UI: **Catalog Explorer → Create catalog → Default Storage**.
2. Importe o notebook `setup/00_setup_base_churn.py` no seu workspace (**Workspace → Import → URL**) usando a URL raw deste arquivo.
3. Ajuste, se quiser, as variáveis `NOME_CATALOGO` / `NOME_SCHEMA` na primeira célula.
4. Anexe **Serverless** (ou um cluster) e clique em **Run all**.
5. Confira o relatório final. Valores esperados (dataset fixo): **2.000 clientes**, **1.253 tickets**, **taxa de churn 0,270**, **corr. uso × churn -0,504**.

O notebook lê os CSVs deste repositório (via URL raw), cria as tabelas Delta, deriva `feature_churn`, documenta tudo (comentários + PK/FK) e monta a base de conhecimento (volume `kb_volume`).

## Parametrização

Nada é fixo a um ambiente específico:
- **Catálogo/schema**: variáveis no topo do notebook.
- **Origem dos dados**: URL raw deste repositório (`CSV_BASE`).
- **Objetos por aluno** (metric views, modelo, funções, Genie, app): criados nos exercícios, em um schema pessoal `<catálogo>.<seu_database>`.
