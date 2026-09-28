# 09 - Criação de Apps

![Trilha do Master Training com destaque no que foi construído até o Exercício 09](../assets/09%20-%20arquitetura.gif)

> _Tudo o que você construiu durante a trilha._

Você detectou o risco (dashboards + modelo do Ex. 6), diagnosticou o porquê (agentes do Ex. 7) e criou as funções que agem (Ex. 8). Agora vamos reunir tudo num produto: a **Central de Retenção**, um app que qualquer atendente abre no navegador, sem SQL e sem notebook.

O app reúne o que você construiu nos módulos anteriores em três abas, e você o publica rodando um único notebook: preenche dois campos e clica em **Run all**. O notebook cria o app, configura automaticamente tudo que ele precisa e devolve a URL.

E tem uma novidade: a IA do app (a leitura dos gráficos e o e-mail de retenção) passa por um **model service do Unity Gateway**, criado no seu schema. É um modelo governado pelo Unity Catalog, com limite de uso e registro de cada chamada, exatamente como uma empresa colocaria IA em produção.

**Pré-requisitos:**
- [Ex. 1 - SQL com IA](../01%20-%20SQL%20com%20IA)
- [Ex. 6 - Previsão de Churn (ML)](../06%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29)
- [Ex. 7 - Análise de Dados Multi-Agent](../07%20-%20An%C3%A1lise%20de%20Dados%20Multi-Agent)
- [Ex. 8 - Retenção com ML e GenAI](../08%20-%20Reten%C3%A7%C3%A3o%20com%20ML%20e%20GenAI)

---

## Passo 1: Publicar o app
1. Importe o notebook: **Workspace → Três pontinhos no topo → Import → URL**, e cole o seguinte:
```
https://github.com/CaduBettanim/Databricks-Master-Training/blob/main/09%20-%20Cria%C3%A7%C3%A3o%20de%20Apps/deploy_app.py
```
2. Após clicar em **Import**, você será redirecionado para o notebook
3. No dropdown na barra superior, ao lado de **Run all**, selecione o cluster `dbacademy_workshop_cluster`
4. Rode a primeira célula de código, abaixo de **Passo 1 — Preencha os campos e rode tudo**, para exibir os widgets
5. Preencha os widgets:
    - **1. Seu schema**: o schema que você criou no Ex. 1
    - **2. Endpoint do Supervisor (Ex.07)**: o nome do endpoint que você copiou no Passo 10 do Ex. 7 (ex.: `mas-3d713414-endpoint`)
    - **5. Model service (Unity Gateway)**: já vem preenchido com `retencao-gateway`. Pode deixar como está
6. Clique em **Run all**

> Não guardou o endpoint? Em **Agents**, abra o seu Supervisor e clique no botão **Endpoint** em cima

O notebook faz todo o trabalho pesado:
- Baixa o código do app do GitHub e o prepara com a sua configuração
- Resolve o SQL Warehouse pelo nome (`dbacademy_workshop_wh`), com fallback
- Cria o seu **model service** `dbacademy.<seu_schema>.retencao-gateway` no Unity Gateway (modelo `gpt-oss-20b`, limite de 60 chamadas por minuto e tabela de inferência)
- Cria o app (`central-retencao-<seu_schema>`) com compute e *service principal* próprios
- Habilita o **on-behalf-of** (escopos `sql`, `model-serving` e `ai-gateway`) e declara o warehouse que o app usa
- Publica e imprime a URL

> O notebook é **autocontido**: baixa sozinho o código do app (a pasta `app/`, com o front-end já compilado) do GitHub em tempo de execução. Você não precisa clonar o repositório.

Repare no que ele não faz: nenhuma concessão de permissão. Sem `GRANT`, sem `EXECUTE`, sem `CAN_QUERY`, sem `CAN_RUN` em Genie. Sob o on-behalf-of, o app age com a sua identidade, que já tem acesso a tudo.


## Passo 2: Abrir o app
1. Clique na URL que o notebook imprime no final
2. Na primeira vez, o Databricks pede que você **autorize o app** a agir em seu nome (SQL, Model Serving e AI Gateway). Clique em **Authorize**
3. Na aba **📊 Cockpit**, clique numa região do mapa e veja os gráficos filtrarem
4. Ainda no **Cockpit**, clique em **✨ Explicar** em um dos gráficos
5. Na aba **💬 Assistente**, faça as perguntas abaixo, uma por vez:
```text
Qual o NPS médio por canal de atendimento?
```
```text
Qual o valor total em faturas não pagas?
```
6. Na aba **🎯 Retenção Personalizada**, cole `C01575` (a Marina), gere o e-mail e clique em **Enviar para CRM**. Depois repita com `C00018` (a Gabriela)

No **Assistente**, repare que cada pergunta é roteada para o especialista certo (Suporte / Faturamento).

Na **Retenção**, compare os dois e-mails: a Marina recebe 15% + 10 GB + gerente dedicado, e a Gabriela 10% + dobro da internet com WhatsApp + renegociação. As ofertas vêm da sua `get_cliente_360` (a regra do Ex. 8), e o modelo do Unity Gateway só escreve o texto.

> **Por que o app precisa autorizar o AI Gateway?** Porque cada chamada ao modelo é feita **com a sua identidade** (on-behalf-of). Sem o escopo `ai-gateway`, o Gateway recusa a chamada. É isso que permite saber, depois, quem usou o modelo e quando.

## Passo 3: Ver a governança do Unity Gateway
1. No **Catalog Explorer**, abra `dbacademy` → o seu schema. Além das suas tabelas e funções, você verá o model service **`retencao-gateway`**: é um ativo do Unity Catalog, com dono (você), permissões e linhagem, como qualquer tabela
2. Toda chamada que o app fez ao modelo foi registrada na **tabela de inferência** do model service. No **SQL Editor**, rode (trocando `<seu_schema>`):
```sql
SELECT
    event_time,
    status_code,
    latency_ms,
    destination_model,
    LEFT(get_json_object(request, '$.messages[1].content'), 200) AS pedido
FROM dbacademy.<seu_schema>.retencao_gateway_payload
ORDER BY event_time DESC
LIMIT 10;
```
Você verá uma linha para cada **✨ Explicar** e para cada **e-mail** gerado. Na coluna `pedido`, repare que as ofertas já chegam prontas ao modelo: a regra foi decidida pela sua função, não pela IA.

> A tabela de inferência pode levar alguns minutos para mostrar as chamadas mais recentes. Para uma visão de toda a conta (quem chamou, quantos tokens, qual modelo), a Databricks também registra o uso na tabela de sistema `system.ai_gateway.usage`, com algumas horas de atraso.

### O que é a Central de Retenção?
Um **Databricks App** (a plataforma hospeda o app com compute próprio) com três abas, cada uma consumindo o que você construiu:

| Aba | O que faz | De onde vem |
|-----|-----------|-------------|
| **📊 Cockpit** | KPIs de churn, um mapa do Brasil com o risco por região e 4 gráficos que filtram ao clicar numa região. Cada gráfico tem um botão **✨ Explicar** que pede uma leitura à IA. | `churn_scores` (Ex. 6) + schema compartilhado `dbacademy.churn`, lidos por um SQL Warehouse; a leitura vem do seu model service do Unity Gateway |
| **💬 Assistente** | Um chat que responde perguntas de negócio (*"qual o NPS médio por canal?"*, *"total de faturas em aberto?"*) roteando para o Genie certo. | seu Supervisor do Ex. 7 |
| **🎯 Retenção Personalizada** | Lista os clientes mais propensos a cancelar; você cola um id, gera o e-mail de retenção e clica em **Enviar para CRM**. | função `get_cliente_360` do Ex. 8 (perfil + ofertas) + seu model service do Unity Gateway (texto) |

> **Por que um app, e não mais uma dashboard?** Porque um app te permite fazer muito mais coisas do que uma dashboard: aqui você navega o risco, conversa com os dados e dispara a retenção, tudo num só lugar, com a governança do Unity Catalog por trás (o app acessa os dados com a sua própria identidade)

## Explore
Você acaba de fechar o ciclo do treinamento: dos dados crus (Setup) a um produto de retenção que um time de negócio usa no dia a dia (detectar, diagnosticar, decidir e agir), tudo governado pelo Unity Catalog, inclusive o modelo de IA, pelo Unity Gateway. É o mesmo padrão que você leva para qualquer caso de uso: **dados → métricas → IA → agentes → app**.
