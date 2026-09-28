# 07 - Análise de Dados com Solução Multi-Agent

![Trilha do Master Training com destaque no que foi construído até o Exercício 07](../assets/07%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Até aqui, você montou as análises. Agora vamos abrir isso para o time de negócio com os **Genie Agents**: qualquer pessoa pergunta em português (*"qual a receita por segmento?"*) e o Genie escreve o SQL, executa e responde, sem escrever uma linha de código.

E vamos um passo além. Você vai criar dois Genies especializados, um de **Faturamento** e um de **Suporte**, e no fim um **Supervisor** que orquestra os dois. O usuário faz uma pergunta só, e o Supervisor descobre sozinho qual especialista deve responder. É isso que chamamos de solução *multi-agent*.

---

# Parte 1: Genie de Faturamento

## Passo 1: Criar o Genie Agent
1. No menu lateral à esquerda, clique em **Genie Agents**
2. Clique em **New**
3. Em **Connect your data**, adicione:
    - `dbacademy.churn.dim_cliente`
    - `dbacademy.churn.dim_plano`
    - `dbacademy.churn.fato_assinatura`
    - `dbacademy.churn.fato_faturamento`
4. Dê o nome `Faturamento - <seu_schema>`, trocando `<seu_schema>` pelo nome do seu schema

> O Genie infere os relacionamentos entre as tabelas; você não precisa configurar os joins na mão. Vamos reutilizar este Genie Agent na Parte 3, no Supervisor

## Passo 2: Perguntar
Faça as perguntas abaixo, uma por vez:

```text
Qual a receita total por segmento?
```
Resultado esperado:
- Consumidor **R$ 3,62 mi**
- PME **R$ 1,80 mi**
- Corporativo **R$ 680 mil**

```text
Qual o percentual de faturas não pagas por plano?
```
Resultado esperado:
- Básico **7,90%**
- Padrão **6,49%**
- Premium **5,90%**
- Empresarial **5,45%**

A inadimplência acompanha o churn: é pior no Básico.

Note que você não disse de qual tabela vem o dado: o Genie descobre sozinho, mostra o SQL que escreveu e ainda desenha um gráfico.

---

# Parte 2: Genie de Suporte

## Passo 3: Criar o Genie Agent
1. Crie um novo Genie Agent como no Passo 1 (**Genie Agents → New**)
2. Em **Connect your data**, adicione:
    - `dbacademy.churn.dim_cliente`
    - `dbacademy.churn.fato_ticket_suporte`
3. Dê o nome `Suporte - <seu_schema>`, trocando `<seu_schema>` pelo nome do seu schema

## Passo 4: Perguntar
Faça as perguntas abaixo, uma por vez:

```text
Qual o CSAT médio por categoria de ticket?
```
Resultado esperado:
- Dúvida **4,08**
- Cobrança **2,99**
- Técnico **2,28**
- Cancelamento **2,27**

```text
Quantos tickets de suporte temos por canal?
```
Resultado esperado:
- Chat **447**
- Email **407**
- Telefone **399**

## Passo 5: Pergunte sobre o ano fiscal
```text
Qual a média de NPS do ano fiscal de 2024 no estado do Amazonas (AM)?
```
O Genie responde **≈ 7,3**, mas vale ler a explicação dele: *"não há definição de ano fiscal, então interpretei como o ano-calendário (jan–dez de 2024)"*. Ou seja, ele chutou que ano fiscal é o mesmo que ano civil, porque ninguém contou a ele quando começa o seu ano fiscal.

## Passo 6: Ensine a regra e pergunte de novo
1. Abra o menu de configurações do agente em **Configure** no canto superior direito
2. Na aba **Instructions**, cole a regra do seu ano fiscal:
```text
O ano fiscal (AF) da empresa vai de 1º de outubro a 30 de setembro do ano seguinte, identificado pelo ano em que começa. Exemplo: o AF2024 vai de 01/10/2024 a 30/09/2025. Sempre que a pergunta mencionar "ano fiscal", use esse período (com base em data_abertura), nunca o ano-calendário.
```
3. Faça exatamente a mesma pergunta:
```text
Qual a média de NPS do ano fiscal de 2024 no estado do Amazonas (AM)?
```

Desta vez o Genie filtra de **01/10/2024 a 30/09/2025** e responde **≈ 6,5**. É um número diferente porque o período mudou: a mesma pergunta deu duas respostas, e a diferença foi a regra que você forneceu.

> É a mesma ideia da métrica governada do Ex. 3: sem a regra explícita, a IA chuta. As *Instructions* são onde você transforma o conhecimento do negócio em respostas confiáveis, e valem para todos que usam o Genie Agent.

---

# Parte 3: Supervisor (multi-agent)

Você já tem dois especialistas. Agora vamos criar o **Supervisor**: ele recebe a pergunta do usuário e a encaminha para o Genie certo, sem que o usuário precise saber qual é qual.

## Passo 7: Criar o Supervisor e anexar os agentes
1. No menu lateral à esquerda, abra **Agents**
2. Clique em **Create agent** e selecione **Supervisor Agent**
3. Vá em **Tools and sub-agents** e selecione a opção **Genie Agents**
4. No campo de busca, digite o nome do seu agente de faturamento (`Faturamento - <seu_schema>`) e selecione-o
5. Na descrição da ferramenta, cole:
```text
Especialista em faturamento e cobrança. Responde sobre receita, inadimplência, faturas pagas e não pagas, e valores por plano e por segmento.
```
6. Repita os passos 3 a 5 para o agente de suporte (`Suporte - <seu_schema>`), com a descrição:
```text
Especialista em atendimento e satisfação do cliente. Responde sobre tickets de suporte, CSAT, NPS, canais e categorias, inclusive por ano fiscal.
```
7. Remova a ferramenta que já vem por padrão, chamada `python_exec`: passe o mouse sobre ela, clique no ícone de lixeira e confirme a exclusão

> Neste exercício o Supervisor só coordena os dois Genies, por isso removemos o `python_exec`

## Passo 8: Nomear, instruir e descrever
> O campo **nome** só fica editável depois que você anexa pelo menos um agente (Passo 7); por isso deixamos essa etapa para agora.

1. Dê um nome ao Supervisor, por exemplo `Analise-Clientes-<seu_schema>`
2. Em **Instructions**, cole as regras de coordenação:
```text
Você coordena dois especialistas: um de Faturamento (receita, inadimplência, faturas, planos) e um de Suporte (tickets, CSAT, NPS, canais). Encaminhe cada pergunta ao especialista adequado, combine as respostas quando a pergunta envolver os dois temas e responda sempre em português.
```
3. Mais abaixo, em **Description**, cole:
```text
Assistente de análise de clientes: responde perguntas de negócio sobre faturamento e sobre atendimento/suporte, encaminhando cada pergunta ao especialista certo.
```

## Passo 9: Testar o roteamento
Faça estas duas perguntas novas, uma de cada domínio, e observe o Supervisor escolher o especialista certo antes de responder:

```text
Qual o valor total em faturas não pagas?
```
Resultado esperado: o Supervisor aciona o agente de **Faturamento** → **≈ R$ 383.335** (3.846 faturas em aberto)

```text
Qual a nota média de NPS por canal de atendimento?
```
Resultado esperado: o Supervisor aciona o agente de **Suporte** →
- Chat **6,57**
- Email **6,54**
- Telefone **6,47**

> Repare que você não disse a qual Genie perguntar: o Supervisor leu a pergunta, escolheu o especialista e sintetizou a resposta. É assim que uma solução *multi-agent* simplifica a vida do usuário de negócio: uma porta de entrada, vários especialistas atrás dela.

## Passo 10: Publicar o Supervisor e copiar o endpoint
1. Se a página do agente tiver um botão **Deploy** (ou **Publish**) ainda não acionado, clique nele
2. Clique no botão **Endpoint** em cima
3. Copie e guarde o nome do endpoint que começa com `mas-` (algo como `mas-3d713414-endpoint`)

Ao criar o Supervisor, o Databricks já o publica como um **endpoint de serving**. É por ele que o app do Ex. 9 vai chamar o Supervisor.

> Você vai colar o nome do endpoint no campo `supervisor_endpoint` do Ex. 9
