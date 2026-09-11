-- Exercício 5 — Dashboards (AI/BI)
-- Base compartilhada (somente leitura): dbacademy.churn
-- Estes são os DATASETS do dashboard. Cole cada um na aba "Dados" do AI/BI Dashboard
-- (um dataset por consulta). Os GRÁFICOS você monta no Canvas com o Assistente (✨) — ver README.

-- ============================================================
-- Dataset 1 — assinaturas  (grão: 1 linha por assinatura)
--   Usado na maioria dos gráficos: churn por plano/segmento/canal, motivos, cancelamentos no tempo.
--   status = 'Ativa' | 'Cancelada'   |   churn_flag = 1 quando cancelou
-- ============================================================
SELECT
  a.id_cliente,
  a.status,
  a.churn_flag,
  a.motivo_cancelamento,
  a.data_inicio,
  a.data_fim,
  p.nome_plano,
  p.preco_mensal,
  p.periodicidade,
  c.segmento,
  c.uf,
  c.canal_aquisicao,
  c.faixa_etaria
FROM dbacademy.churn.fato_assinatura a
JOIN dbacademy.churn.dim_plano    p ON a.id_plano   = p.id_plano
JOIN dbacademy.churn.dim_cliente  c ON a.id_cliente = c.id_cliente;

-- ============================================================
-- Dataset 2 — faturamento  (grão: 1 linha por mês)
--   Usado no gráfico de receita e inadimplência ao longo do tempo.
-- ============================================================
SELECT
  competencia,
  COUNT(*)                                            AS faturas,
  ROUND(SUM(valor), 0)                                AS receita,
  ROUND(AVG(CASE WHEN pago = false THEN 1.0 ELSE 0 END) * 100, 1) AS pct_nao_pago,
  ROUND(AVG(dias_atraso), 1)                          AS atraso_medio_dias
FROM dbacademy.churn.fato_faturamento
GROUP BY competencia
ORDER BY competencia;
