# 00 - Setup — Base compartilhada de Churn

Prepara a base de dados que **toda a turma** vai usar. Roda **uma vez** (papel de instrutor/admin).

## Conteúdo

| Pasta | O quê |
|-------|-------|
| `data/` | CSVs de origem (dataset fixo, 1 por tabela) |
| `setup/` | Notebook `00_setup_base_churn.py` que carrega os CSVs e prepara tudo |

## O que o Setup cria (no schema `<catálogo>.churn`)

- Dimensões: `dim_cliente`, `dim_plano`, `dim_data`
- Fatos: `fato_assinatura`, `fato_uso`, `fato_faturamento`, `fato_ticket_suporte`
- `feature_churn` — tabela analítica por cliente (para o modelo de churn), derivada no notebook
- Comentários + chaves (PK/FK) em todas as tabelas
- Volume `kb_volume` com a base de conhecimento (FAQ, Política de Retenção, Playbook de CS)

## Passos

1. **Pré-requisito:** um catálogo Unity Catalog (padrão `dbacademy`). Se não existir e não puder ser criado automaticamente (contas com *Default Storage*), crie pela UI: **Catalog Explorer → Create catalog → Default Storage**.
2. Importe o notebook por URL: **Workspace → Import → URL** com
   `https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/00%20-%20Setup/setup/00_setup_base_churn.py`
3. (Opcional) ajuste `NOME_CATALOGO` / `NOME_SCHEMA` na primeira célula.
4. Anexe **Serverless** (ou um cluster) e clique em **Run all**.

## Resultado esperado (dataset fixo → valores exatos)

| Métrica | Valor |
|---------|-------|
| clientes | **2.000** |
| tickets | **1.253** |
| taxa de churn | **0,270** |
| corr. uso × churn | **-0,504** |
| corr. atraso × churn | **0,125** |

Se os números baterem exatamente, a carga está íntegra. A correlação negativa forte (uso ↓ → churn ↑) confirma o sinal necessário para o modelo dos próximos módulos.
