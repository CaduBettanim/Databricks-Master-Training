-- Exercício 4 — AI Functions (GenAI no SQL)
-- Base compartilhada (somente leitura): dbacademy.churn.fato_ticket_suporte
-- Rode no SQL Editor. As funções chamam um modelo de IA — pode levar alguns segundos por linha.

-- Amostra variada (csat alto, médio e baixo) para ver a IA distinguindo os casos
-- 1) ai_analyze_sentiment — sentimento das reclamações
WITH amostra AS (
  (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 5 LIMIT 2)
  UNION ALL (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 3 LIMIT 2)
  UNION ALL (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 1 LIMIT 2)
)
SELECT LEFT(texto_reclamacao, 60) AS trecho, csat,
       ai_analyze_sentiment(texto_reclamacao) AS sentimento
FROM amostra ORDER BY csat DESC;

-- 1b) Distribuição de sentimento em TODOS os tickets
-- (mais lenta: roda a IA em toda a tabela — ~1 a alguns minutos)
SELECT sentimento, COUNT(*) AS qtd
FROM (
  SELECT ai_analyze_sentiment(texto_reclamacao) AS sentimento
  FROM dbacademy.churn.fato_ticket_suporte
)
GROUP BY sentimento
ORDER BY qtd DESC;

-- 2) ai_classify — classificar o assunto do ticket
WITH amostra AS (
  (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 5 LIMIT 2)
  UNION ALL (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 3 LIMIT 2)
  UNION ALL (SELECT texto_reclamacao, csat FROM dbacademy.churn.fato_ticket_suporte WHERE csat = 1 LIMIT 2)
)
SELECT LEFT(texto_reclamacao, 60) AS trecho, csat,
       ai_classify(texto_reclamacao,
                   ARRAY('Cobrança','Técnico','Cancelamento','Elogio','Dúvida')) AS categoria_ia
FROM amostra ORDER BY csat DESC;

-- 3) ai_mask — mascarar dados pessoais (PII) no texto
SELECT ai_mask(texto_reclamacao, ARRAY('person','phone','email')) AS texto_anonimizado
FROM dbacademy.churn.fato_ticket_suporte
WHERE texto_reclamacao LIKE '%@%' OR texto_reclamacao LIKE '%-____%'
LIMIT 5;

-- 4) ai_summarize — resumir as dores dos tickets negativos (csat <= 2)
SELECT ai_summarize(array_join(collect_list(texto_reclamacao), ' | '), 40) AS resumo_dores
FROM (
  SELECT texto_reclamacao
  FROM dbacademy.churn.fato_ticket_suporte
  WHERE csat <= 2
  LIMIT 20
);
