# 09 - Criação de Apps

![Trilha do Master Training com destaque no que foi construído até o Exercício 09](../assets/09%20-%20arquitetura.gif?v=20260928)

> _Tudo o que você construiu durante a trilha._

Você detectou o risco (dashboards + modelo do Ex. 6), diagnosticou o porquê (agentes do Ex. 7) e criou as funções que agem (Ex. 8). Agora vamos reunir tudo num produto: a **Central de Retenção**, um app que qualquer atendente abre no navegador, sem SQL e sem notebook.

O app reúne o que você construiu nos módulos anteriores em três abas, e você o publica rodando um único notebook: preenche o seu schema, confere os seus dois Genies e clica em **Run all**. O notebook cria o app, configura automaticamente tudo que ele precisa e devolve a URL.

E tem duas novidades:
- O **Assistente** do app tem um **Supervisor** escrito em código: um agente que recebe a pergunta, escolhe qual dos seus Genies do Ex. 7 (Faturamento ou Suporte) deve responder e sintetiza a resposta. É a solução *multi-agent* que você preparou no Ex. 7
- Toda a IA do app (o Supervisor, a leitura dos gráficos e o e-mail de retenção) passa por um **model service do Unity Gateway**, criado no seu schema. É um modelo governado pelo Unity Catalog, com limite de uso e registro de cada chamada, exatamente como uma empresa colocaria IA em produção

**Pré-requisitos:**
- [Ex. 1 - SQL com IA](../01%20-%20SQL%20com%20IA)
- [Ex. 6 - Previsão de Churn (ML)](../06%20-%20Previs%C3%A3o%20de%20Churn%20%28ML%29)
- [Ex. 7 - Análise de Dados Multi-Agent](../07%20-%20An%C3%A1lise%20de%20Dados%20Multi-Agent): os Genies `Faturamento - <seu_schema>` e `Suporte - <seu_schema>`
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
    - **2. Genie de Faturamento (Ex.07)** e **3. Genie de Suporte (Ex.07)**: a lista mostra os Genie Agents que **você** criou, e cada campo já vem com o seu do Ex. 7 selecionado (`Faturamento - <seu_schema>` e `Suporte - <seu_schema>`). Confira: são os especialistas do Supervisor do app
    - **4. Warehouse**: já vem selecionado com `dbacademy_workshop_wh`. Pode deixar como está
    - **5. Model service**: já vem preenchido com `retencao-gateway`. Pode deixar como está
6. Clique em **Run all**

> Os seus Genies não aparecem na lista? Confira em **Genie Agents** se você os criou no Ex. 7 e rode de novo a primeira célula de código (a lista é montada quando ela roda)

O notebook faz todo o trabalho pesado:
- Baixa o código do app do GitHub e o prepara com a sua configuração
- Resolve o SQL Warehouse pelo nome (`dbacademy_workshop_wh`), com fallback
- Confirma os seus Genies de **Faturamento** e **Suporte** (Ex. 7) escolhidos nos campos 2 e 3 e passa os IDs ao app: são os especialistas do Supervisor
- Cria o seu **model service** `dbacademy.<seu_schema>.retencao-gateway` no Unity Gateway (modelo `gpt-oss-20b`, limite de 60 chamadas por minuto e tabela de inferência)
- Cria o app (`central-retencao-<seu_schema>`) com compute e *service principal* próprios
- Habilita o **on-behalf-of** (escopos `sql`, `dashboards.genie`, `ai-gateway` e `model-serving`) e declara o warehouse que o app usa
- Publica e imprime a URL

> O notebook é **autocontido**: baixa sozinho o código do app (a pasta `app/`, com o front-end já compilado) do GitHub em tempo de execução. Você não precisa clonar o repositório.

Repare no que ele não faz: nenhuma concessão de permissão. Sem `GRANT`, sem `EXECUTE`, sem `CAN_QUERY`, sem `CAN_RUN` em Genie. Sob o on-behalf-of, o app age com a sua identidade, que já tem acesso a tudo.


## Passo 2: Abrir o app
1. Clique na URL que o notebook imprime no final
2. Na primeira vez, o Databricks pede que você **autorize o app** a agir em seu nome (SQL, Genie, AI Gateway e Model Serving). Clique em **Authorize**
3. Na aba **📊 Cockpit**, clique numa região do mapa e veja os gráficos filtrarem
4. Ainda no **Cockpit**, clique em **✨ Explicar** em um dos gráficos
5. Na aba **💬 Assistente**, faça as perguntas abaixo, uma por vez:
```text
Qual a nota média de NPS por canal de atendimento?
```
Resultado esperado: o Supervisor aciona o Genie de **Suporte** →
- Chat **6,57**
- Email **6,54**
- Telefone **6,47**

```text
Qual o valor total em faturas não pagas?
```
Resultado esperado: o Supervisor aciona o Genie de **Faturamento** → **≈ R$ 383.335**

Agora uma pergunta que envolve os dois temas:
```text
Compare a receita total e o CSAT médio por segmento de cliente.
```
Resultado esperado: o Supervisor aciona **os dois** Genies, **Faturamento** e **Suporte**, e combina as respostas:

| Segmento | Receita | CSAT médio |
|---|---|---|
| Consumidor | R$ 3,62 mi | 3,31 |
| PME | R$ 1,80 mi | 3,55 |
| Corporativo | R$ 680 mil | 3,82 |

6. Na aba **🎯 Retenção Personalizada**, cole `C01575` (a Marina), gere o e-mail e clique em **Enviar para CRM**. Depois repita com `C00018` (a Gabriela)

No **Assistente**, repare que você não disse a qual Genie perguntar: o Supervisor leu a pergunta, escolheu o especialista e sintetizou a resposta. O nome do especialista aparece acima de cada resposta (*Supervisor · via Suporte*, ou *via Faturamento + Suporte* na pergunta combinada), e clicando nele você vê a pergunta que o Supervisor repassou ao Genie e o SQL que o Genie escreveu. É assim que uma solução *multi-agent* simplifica a vida do usuário de negócio: uma porta de entrada, vários especialistas atrás dela.

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
Você verá uma linha para cada **✨ Explicar**, para cada **e-mail** gerado e para cada rodada de raciocínio do **Supervisor** (cada pergunta do Assistente gera duas ou mais: uma para escolher o especialista e outra para escrever a resposta). Na coluna `pedido` dos e-mails, repare que as ofertas já chegam prontas ao modelo: a regra foi decidida pela sua função, não pela IA.

> A tabela de inferência pode levar alguns minutos para mostrar as chamadas mais recentes. Para uma visão de toda a conta (quem chamou, quantos tokens, qual modelo), a Databricks também registra o uso na tabela de sistema `system.ai_gateway.usage`, com algumas horas de atraso.

### O que é a Central de Retenção?
Um **Databricks App** (a plataforma hospeda o app com compute próprio) com três abas, cada uma consumindo o que você construiu:

| Aba | O que faz | De onde vem |
|-----|-----------|-------------|
| **📊 Cockpit** | KPIs de churn, um mapa do Brasil com o risco por região e 4 gráficos que filtram ao clicar numa região. Cada gráfico tem um botão **✨ Explicar** que pede uma leitura à IA. | `churn_scores` (Ex. 6) + schema compartilhado `dbacademy.churn`, lidos por um SQL Warehouse; a leitura vem do seu model service do Unity Gateway |
| **💬 Assistente** | Um chat que responde perguntas de negócio (*"qual o NPS médio por canal?"*, *"total de faturas em aberto?"*) roteando para o Genie certo. | o Supervisor em código do app + os seus Genies do Ex. 7; o raciocínio do Supervisor vem do seu model service do Unity Gateway |
| **🎯 Retenção Personalizada** | Lista os clientes mais propensos a cancelar; você cola um id, gera o e-mail de retenção e clica em **Enviar para CRM**. | função `get_cliente_360` do Ex. 8 (perfil + ofertas) + seu model service do Unity Gateway (texto) |

### Por dentro do Assistente: o Supervisor em código
O Supervisor é um agente curto, no arquivo [`app/server/supervisor.py`](app/server/supervisor.py). Ele tem três ingredientes:

1. **Instruções de coordenação**, que o modelo recebe antes de cada pergunta:
```text
Você coordena dois especialistas: um de Faturamento (receita, inadimplência, faturas, planos) e um de Suporte (tickets, CSAT, NPS, canais). Encaminhe cada pergunta ao especialista adequado, combine as respostas quando a pergunta envolver os dois temas e responda sempre em português.
```
2. **Dois especialistas como ferramentas** (*tool calling*), cada um com uma descrição que o modelo lê para decidir:

| Ferramenta | Genie (Ex. 7) | Descrição |
|---|---|---|
| `consultar_faturamento` | `Faturamento - <seu_schema>` | Especialista em faturamento e cobrança. Responde sobre receita, inadimplência, faturas pagas e não pagas, e valores por plano e por segmento. |
| `consultar_suporte` | `Suporte - <seu_schema>` | Especialista em atendimento e satisfação do cliente. Responde sobre tickets de suporte, CSAT, NPS, canais e categorias, inclusive por ano fiscal. |

3. **Um laço**: o modelo escolhe a ferramenta, o app pergunta ao Genie (que escreve e executa o SQL), devolve o resultado ao modelo, e o modelo escreve a resposta final. Se a pergunta envolver os dois temas, ele aciona os dois Genies.

Tudo roda com a **sua** identidade (on-behalf-of): o Genie consulta os dados como você, e as instruções que você deu ao Genie de Suporte no Ex. 7 (o ano fiscal) continuam valendo quando a pergunta chega pelo Supervisor.

> **Por que um app, e não mais uma dashboard?** Porque um app te permite fazer muito mais coisas do que uma dashboard: aqui você navega o risco, conversa com os dados e dispara a retenção, tudo num só lugar, com a governança do Unity Catalog por trás (o app acessa os dados com a sua própria identidade)

## Explore
Você acaba de fechar o ciclo do treinamento: dos dados crus (Setup) a um produto de retenção que um time de negócio usa no dia a dia (detectar, diagnosticar, decidir e agir), tudo governado pelo Unity Catalog, inclusive o modelo de IA, pelo Unity Gateway. É o mesmo padrão que você leva para qualquer caso de uso: **dados → métricas → IA → agentes → app**.
