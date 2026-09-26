# 00 - Setup: Base compartilhada + Habilitação da turma

![Trilha do Master Training com destaque no que foi construído até o Exercício 00](../assets/00%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Um único notebook, rodado uma vez pelo **administrador de conta**, que faz tudo: prepara a turma (grupo, permissões, compute), carrega a base compartilhada de churn e verifica que cada participante (e o workspace) está pronto. É **idempotente** (seguro re-executar).

## Conteúdo

| Pasta | O quê |
|-------|-------|
| `data/` | CSVs de origem (dataset fixo, 1 por tabela) |
| `setup/` | Notebook `00_setup_base_churn.py`: prepara a turma, carrega os dados e verifica tudo |

## O que o Setup faz
> O setup é idempotente, então pode ser rodado várias vezes

1. Cria o grupo `dbacademy_workshop` e adiciona os participantes
2. Cria o catálogo `dbacademy`
3. Cria os recursos de computação:
    - SQL Warehouse `dbacademy_workshop_wh`
    - Cluster multiuso `dbacademy_workshop_cluster`
4. Concede as permissões ao grupo:
    - `USE CATALOG` + `CREATE SCHEMA` no catálogo
    - `CAN_MANAGE` na warehouse
    - `CAN_ATTACH_TO` no cluster
5. Carrega a base compartilhada em `dbacademy.churn` como read-only para os participantes:
    - Dimensões `dim_cliente`, `dim_plano`, `dim_data` e fatos `fato_assinatura`, `fato_uso`, `fato_faturamento`, `fato_ticket_suporte`
    - `feature_churn`: tabela analítica por cliente 
    - Comentários + chaves em todas as tabelas
    - Volume `kb_volume` com a base de conhecimento (FAQ, Política de Retenção, Playbook de CS)
    - Concede à turma `USE SCHEMA` + `SELECT` no schema `churn` e `READ VOLUME` no `kb_volume`
6. Verifica:
    - Permissões por participante
    - Features de IA usadas nos Ex. 4/6/7
7. Produz um relatório final de preparo do workspace


## Passos
> É necessário ser um administrador de conta para rodar o setup

1. Importe o notebook por URL: **Workspace → Três pontinhos no topo → Import → URL**, e cole o seguinte:
```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/00%20-%20Setup/setup/00_setup_base_churn.py
```
2. Rode as duas primeiras células para exibir os widgets
3. Selecione os participantes que participarão do treinamento. Não é necessário alterar os outros parâmetros
4. Clique em **Run all**.
    - Caso obtenha o erro `RuntimeError: Catálogo 'dbacademy' não pode ser criado automaticamente` na célula 11, crie o catálogo `dbacademy` manualmente através de **Catalog → Create a catalog** e rode novamente as células a partir da 11
5. Todas as células devem terminar com sucesso

> Caso vá participar de um treinamento com a equipe Databricks, envie a evidência de conclusão do Setup para seu time de conta

