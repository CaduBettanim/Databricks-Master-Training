-- Exercício 4 — AI Functions (GenAI no SQL)
-- Base compartilhada (somente leitura): dbacademy.churn.fato_ticket_suporte
-- Rode no SQL Editor. As funções chamam um modelo de IA — pode levar alguns segundos por linha.

-- 1) ai_analyze_sentiment — sentimento das reclamações
SELECT LEFT(texto_reclamacao, 60) AS trecho,
       csat,
       ai_analyze_sentiment(texto_reclamacao) AS sentimento
FROM dbacademy.churn.fato_ticket_suporte
ORDER BY csat
LIMIT 5;

-- 2) ai_classify — classificar o assunto do ticket
SELECT LEFT(texto_reclamacao, 60) AS trecho,
       ai_classify(texto_reclamacao,
                   ARRAY('Cobrança','Técnico','Cancelamento','Elogio','Dúvida')) AS categoria_ia
FROM dbacademy.churn.fato_ticket_suporte
ORDER BY csat
LIMIT 5;

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
