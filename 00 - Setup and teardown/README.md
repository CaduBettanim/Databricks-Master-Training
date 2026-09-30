# 00 - Setup and teardown: Base compartilhada + Habilitação da turma

![Trilha do Master Training com destaque no que foi construído até o Exercício 00](../assets/00%20-%20arquitetura.gif?v=20260928)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Um único notebook, rodado uma vez pelo **administrador de conta**, que faz tudo: prepara a turma (grupo, permissões, compute), carrega a base compartilhada de churn e verifica que cada participante (e o workspace) está pronto. É **idempotente** (seguro re-executar).

!!! tip "Líderes de dados: veja o Setup Guiado"
    Vídeos curtos sobre a dinâmica do treinamento, a preparação do ambiente e o envio das evidências: **[Setup Guiado](<Setup guiado/README.md>)**.

## Conteúdo

| Pasta | O quê |
|-------|-------|
| `data/` | CSVs de origem (dataset fixo, 1 por tabela) |
| `notebooks/` | `00_setup.py` (prepara a turma, carrega os dados e verifica tudo) e `00_teardown.py` (remove os recursos ao fim do workshop) |

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
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/00%20-%20Setup%20and%20teardown/notebooks/00_setup.py
```
2. Rode as duas primeiras células para exibir os widgets
3. Selecione os participantes que participarão do treinamento. Não é necessário alterar os outros parâmetros
4. Clique em **Run all**.
    - Caso obtenha o erro `RuntimeError: Catálogo 'dbacademy' não pode ser criado automaticamente` na célula 11, crie o catálogo `dbacademy` manualmente através de **Catalog → Create a catalog** e rode novamente as células a partir da 11
5. Todas as células devem terminar com sucesso

> Caso vá participar de um treinamento com a equipe Databricks, envie a evidência de conclusão do Setup para seu time de conta

## Desmontagem (após o workshop)
> É necessário ser um administrador de conta para rodar a desmontagem

O notebook `00_teardown.py` reverte o que o Setup criou. É **idempotente** (recursos já ausentes são ignorados, seguro re-executar).

### O que a Desmontagem faz
Cada alternador é `true`/`false`. Os padrões removem os recursos **específicos do workshop**:

1. Exclui o grupo `dbacademy_workshop` (o que também revoga todas as concessões feitas a ele)
2. Exclui a SQL Warehouse `dbacademy_workshop_wh`
3. Exclui o cluster multiuso `dbacademy_workshop_cluster`
4. **REMOVER CATÁLOGO** vem **desativado** (`false`): o catálogo `dbacademy` pertence ao administrador e contém tanto a base compartilhada `dbacademy.churn` (tabelas + volume `kb_volume`) quanto o schema pessoal `dbacademy.<username>` de cada participante. Ative (`true`) apenas se o Setup criou o catálogo e o workshop foi completamente encerrado, pois o `DROP CATALOG ... CASCADE` apaga tudo isso.

### Passos
1. Importe o notebook por URL: **Workspace → Três pontinhos no topo → Import → URL**, e cole o seguinte:
```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/00%20-%20Setup%20and%20teardown/notebooks/00_teardown.py
```
2. Rode as duas primeiras células para exibir os widgets
3. Ajuste os alternadores conforme o que deseja remover
4. Clique em **Run all**
5. Confira o resultado na seção **3. Relatório final** (`✅ Desmontagem concluída`)

