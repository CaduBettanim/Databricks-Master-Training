# 02 - Geração de Alertas

![Trilha do Master Training com destaque no que foi construído até o Exercício 02](../assets/02%20-%20arquitetura.gif)

> _Em destaque, o que você já construiu na trilha até este ponto; em cinza, o que ainda vem._

Agora vamos configurar um alerta que avisa sozinho quando um indicador de churn cruza um limite, sem precisar abrir relatórios todo dia.

## Objetivo
Criar um **Alerta** no Databricks: uma consulta que roda em uma agenda e notifica quando uma condição é atendida.

> Você pode encontrar todas as consultas usadas aqui em [`alertas.sql`](./alertas.sql)

---

## Passo 1: Criar o alerta
1. No menu lateral à esquerda, navegue até **Alerts**
2. Clique em **Create alert**
3. Cole a seguinte query no espaço em branco:
```sql
SELECT
    ROUND(AVG(churn_flag) * 100, 1) AS taxa_churn_pct
FROM dbacademy.churn.fato_assinatura;
```
4. Rode a query (Run all). O resultado deve ser `taxa_churn_pct = 27.0`

O alerta observa o resultado de uma consulta. A consulta que colamos serve para monitorar a taxa de churn global (%).

## Passo 2: Configurar o alerta
1. Configure a **condição de disparo**:
    - Coluna: `taxa_churn_pct`
    - Operador: **maior que (>)**
    - Valor (threshold): **25**
2. Troque o nome do alerta clicando em "New Alert \[...\]" na aba superior para `Alerta_Churn_<seu_nome>`
3. Em **Notifications**, informe o e-mail para receber o alerta
4. Clique no ícone de calendário e defina o agendamento (ex.: todo dia)
5. Clique em **Run Alert**

> Como a taxa atual é **27,0** e o limite é **25**, o alerta entra em estado disparado (triggered)

## Passo 3 (variação): Alerta de NPS baixo
Repita os processos dos Passos 1 e 2 com esta consulta e a condição `nps_medio < 7`:
```sql
SELECT
    ROUND(AVG(nps), 2) AS nps_medio
FROM dbacademy.churn.fato_ticket_suporte;
```
Valor atual: **6,53** → também dispara.

> **Nota:** aqui os dados são fixos, então o valor não muda, o que é ótimo para ver o alerta disparar de forma previsível. Em produção, a mesma configuração vira monitoramento contínuo: a agenda reavalia a consulta e avisa quando o indicador cruza o limite.

---

## Resultado esperado
| Alerta | Consulta retorna | Condição | Estado |
|--------|:---:|:---:|:---:|
| Taxa de churn | **27,0** | > 25 | 🔴 Disparado |
| NPS médio | **6,53** | < 7 | 🔴 Disparado |
