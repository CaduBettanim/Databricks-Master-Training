# 09 - Criação de Apps

![Trilha do Master Training com destaque no que foi construído até o Exercício 09](arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Você detectou o risco (dashboards + modelo do Ex. 6), diagnosticou o porquê (agentes do Ex. 7) e criou as funções que agem (Ex. 8). Agora vamos **entregar tudo num produto**: a **Central de Retenção**, um app que qualquer atendente abre no navegador — sem SQL, sem notebook.

O app **amarra o treinamento inteiro** em três abas, e você o publica **rodando um único notebook**: preenche dois campos e clica em **Run all**. O notebook cria o app, concede automaticamente tudo que ele precisa e devolve a **URL**.

**Pré-requisitos** (no seu schema `dbacademy.<seu_db>`):
- [Setup](../00%20-%20Setup) concluído (base `dbacademy.churn`).
- **[Ex. 7 - Multi-Agent](../07%20-%20An%C3%A1lise%20de%20Dados%20Multi-Agent)** — seu **Supervisor** publicado (o endpoint `mas-...-endpoint`).
- **[Ex. 6 - Previsão de Churn](../06%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29)** — a tabela `churn_scores`.
- **[Ex. 8 - Retenção](../08%20-%20Reten%C3%A7%C3%A3o%20com%20ML%20e%20GenAI)** — as funções `gerar_email_retencao` e `get_cliente_360`.

## O que é a Central de Retenção
Um **Databricks App** (a plataforma hospeda o app com compute próprio) com três abas, cada uma consumindo o que você construiu:

| Aba | O que faz | De onde vem |
|-----|-----------|-------------|
| **📊 Cockpit** | KPIs de churn, um **mapa do Brasil** com o risco por região e 4 gráficos que **filtram ao clicar numa região**. Cada gráfico tem um botão **✨ Explicar** que pede uma leitura à IA. | `churn_scores` (Ex. 6) + base `churn`, lidos por um SQL Warehouse |
| **💬 Assistente** | Um chat que responde perguntas de negócio (*"qual o NPS médio por canal?"*, *"total de faturas em aberto?"*) roteando para o Genie certo. | seu **Supervisor** do Ex. 7 |
| **🎯 Retenção Personalizada** | Lista os clientes mais propensos a cancelar; você cola um id, gera o **e-mail de retenção** e clica em **Enviar para CRM**. | função `gerar_email_retencao` do Ex. 8 |

> **Por que um app, e não mais um dashboard?** Porque aqui o usuário de negócio **age**: navega o risco, conversa com os dados e dispara a retenção — tudo num só lugar, com a governança do Unity Catalog por trás (o app acessa os dados **com a sua própria identidade** — veja abaixo).

## Como o app se adapta a você
O código do app é **dirigido por configuração**: ele não tem nenhum id ou nome fixo. O notebook de deploy grava **as suas** informações (seu schema, seu Supervisor, seu warehouse) nas variáveis de ambiente do app. Por isso o mesmo notebook serve para toda a turma — cada um publica a sua instância.

## Por que você não concede nenhuma permissão
O app usa **autenticação on-behalf-of (em nome do usuário)**: cada consulta ao warehouse e cada chamada de IA rodam **com a identidade de quem está logado no app** — não com uma conta de serviço. Na prática, o Databricks Apps repassa o seu token ao app (habilitado pelos *escopos* `sql` e `model-serving`, que o notebook configura). Como **você** já tem tudo de que o app precisa — `SELECT` em `dbacademy.churn` (pelo grupo do treino), a posse do seu schema e das suas funções, e a posse do seu Supervisor/Genies — **nada precisa ser concedido**: o app simplesmente age como você. É isso que torna o app reproduzível para a turma inteira sem nenhum passo de administrador.

## Passo a passo

### Passo 1 — Importar o notebook (por URL)
No menu **Workspace → Create → Import** (ou **Import → URL**), cole a URL do notebook e importe:

```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/09%20-%20Cria%C3%A7%C3%A3o%20de%20Apps/deploy_app.py
```

> É só **um** notebook — igual aos outros módulos. Ele é **autocontido**: baixa sozinho o código do app (a pasta `app/`, com o front-end **já compilado**) do GitHub em tempo de execução. Você não precisa clonar o repositório.

### Passo 2 — Rodar o notebook de deploy
Abra o notebook importado, anexe **Serverless** e:
1. **Rode a primeira célula** (a dos campos) com **Shift+Enter** — os dois campos aparecem no topo do notebook.
2. Preencha os campos:
   - **database** — o seu schema pessoal (ex.: `cbettanim`).
   - **supervisor_endpoint** — o endpoint do seu Supervisor do Ex. 7 (ex.: `mas-3d713414-endpoint`).
3. Só então clique em **Run all**.

O notebook faz **todo o trabalho pesado**:
- **baixa o código do app** do GitHub e o prepara com a **sua** configuração;
- resolve o **SQL Warehouse** pelo nome (`dbacademy_workshop_wh`), com fallback;
- **cria o app** (`central-retencao-<seu_db>`) com compute e *service principal* próprios;
- habilita o **on-behalf-of** (escopos `sql` + `model-serving`) e declara o warehouse que o app usa;
- **publica** e imprime a **URL**.

Repare no que ele **não** faz: nenhuma concessão de permissão. Sem `GRANT`, sem `EXECUTE`, sem `CAN_QUERY`, sem `CAN_RUN` em Genie. Sob o on-behalf-of, o app age com a sua identidade — que já tem acesso a tudo.

### Passo 3 — Abrir o app
Clique na **URL** que o notebook imprime no final. Explore as três abas:
- no **Cockpit**, clique numa região do mapa e veja os gráficos filtrarem; clique em **✨ Explicar**;
- no **Assistente**, pergunte *"Qual o NPS médio por canal de atendimento?"* e depois *"Qual o valor total em faturas não pagas?"* — repare que ele roteia para o especialista certo (Suporte / Faturamento);
- na **Retenção**, cole `C01575` (a Marina), gere o e-mail e mande para o CRM.

## Explore
Você acaba de **fechar o ciclo** do treinamento: dos dados crus (Setup) a um **produto de retenção** que um time de negócio usa no dia a dia — detectar, diagnosticar, decidir e agir, tudo governado pelo Unity Catalog. É o mesmo padrão que você leva para qualquer caso de uso: **dados → métricas → IA → agentes → app**.
