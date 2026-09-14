-- =====================================================================
-- 08 - Retenção com ML e GenAI
-- =====================================================================
-- TROQUE  <seu_db>  pelo SEU database pessoal (o mesmo do Ex. 1 e Ex. 7).
-- As funções são criadas NO SEU schema:  dbacademy.<seu_db>
-- Elas leem a base compartilhada (dbacademy.churn) e a SUA tabela de
-- scores (dbacademy.<seu_db>.churn_scores, criada no Ex. 7).
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) get_cliente_360  —  passa o id do cliente, recebe o perfil dele
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION dbacademy.<seu_db>.get_cliente_360(p_id STRING)
RETURNS TABLE(
  id_cliente      STRING,
  nome_cliente    STRING,
  cidade          STRING,
  uf              STRING,
  segmento        STRING,
  canal_aquisicao STRING,
  data_cadastro   DATE,
  nome_plano      STRING,
  preco_mensal    STRING,
  prob_churn      STRING,
  faixa_risco     STRING,
  fator_principal STRING
)
COMMENT 'Perfil 360 do cliente (cadastro + risco de churn) por id'
RETURN
  SELECT c.id_cliente, c.nome_cliente, c.cidade, c.uf, c.segmento,
         c.canal_aquisicao, c.data_cadastro,
         s.nome_plano, s.preco_mensal, s.prob_churn, s.faixa_risco, s.fator_principal
  FROM dbacademy.churn.dim_cliente c
  JOIN dbacademy.<seu_db>.churn_scores s USING (id_cliente)
  WHERE c.id_cliente = p_id;

-- teste
SELECT * FROM dbacademy.<seu_db>.get_cliente_360('C01575');


-- ---------------------------------------------------------------------
-- 2) gerar_email_retencao  —  passa o id, recebe o e-mail já pronto
-- ---------------------------------------------------------------------
-- As REGRAS de oferta são calculadas em SQL (CASE) e a oferta exata é
-- entregue pronta para a IA. A IA só ESCREVE o e-mail — ela não decide
-- o desconto nem o benefício. Por isso o resultado é sempre verificável.
CREATE OR REPLACE FUNCTION dbacademy.<seu_db>.gerar_email_retencao(p_id STRING)
RETURNS TABLE(email STRING)
COMMENT 'Gera um e-mail de retenção personalizado aplicando as regras de oferta'
RETURN
  WITH base AS (
    SELECT
      c.nome_cliente, c.cidade, c.uf, c.data_cadastro,
      floor(datediff(current_date(), c.data_cadastro) / 365) AS anos_casa,
      s.nome_plano, s.fator_principal,

      -- Regra 1 — tempo de casa
      CASE WHEN floor(datediff(current_date(), c.data_cadastro) / 365) >= 5
           THEN '15%' ELSE '10%' END                             AS desconto,

      -- Regra 2 — plano
      CASE WHEN s.nome_plano = 'Básico'
           THEN '10GB de internet grátis no celular'
           ELSE 'o dobro da internet do plano + WhatsApp ilimitado' END AS beneficio_internet,

      -- Regra 3 — motivo do risco (fator_principal do modelo do Ex. 7)
      CASE s.fator_principal
           WHEN 'Insatisfação (CSAT)' THEN 'atendimento prioritário com um gerente de conta dedicado'
           WHEN 'Inadimplência'       THEN 'a renegociação da sua fatura sem juros'
           WHEN 'Baixo uso'           THEN 'uma sessão gratuita de treinamento para aproveitar melhor o serviço'
           ELSE                            'uma ligação com um especialista para ouvir você' END AS gesto
    FROM dbacademy.churn.dim_cliente c
    JOIN dbacademy.<seu_db>.churn_scores s USING (id_cliente)
    WHERE c.id_cliente = p_id
  )
  SELECT ai_query(
    'databricks-meta-llama-3-3-70b-instruct',
    'Escreva um e-mail de retenção curto, caloroso e em português do Brasil. ' ||
    'Comece citando o nome, a cidade e há quantos anos é cliente, para mostrar que conhecemos ele. ' ||
    'Ofereça EXATAMENTE estes três benefícios (não invente outros valores): ' ||
    '1) desconto de ' || desconto || ' na fatura; ' ||
    '2) ' || beneficio_internet || '; ' ||
    '3) ' || gesto || '. ' ||
    'Dados do cliente: nome=' || nome_cliente || ', cidade=' || cidade || '/' || uf ||
    ', anos_como_cliente=' || anos_casa || ', plano=' || nome_plano || '.'
  ) AS email
  FROM base;

-- teste
SELECT email FROM dbacademy.<seu_db>.gerar_email_retencao('C01575');
