-- Exercício 1 — Consultas no SQL Editor + Genie Code
-- Base compartilhada (somente leitura): dbacademy.churn
-- Ajuste o catálogo se você usou outro no Setup.

-- Passo 0 — Crie seu database pessoal (você vai usá-lo a partir do Ex. 3)
-- Convenção: 1ª letra do nome + sobrenome (ex.: João Silva -> jsilva)
CREATE SCHEMA IF NOT EXISTS dbacademy.<seu_db>;

-- Passo 2 — Consultas guiadas -------------------------------------------------

-- 2.1 Clientes por segmento
SELECT segmento, COUNT(*) AS clientes
FROM dbacademy.churn.dim_cliente
GROUP BY segmento
ORDER BY clientes DESC;

-- 2.2 Assinaturas ativas x canceladas
SELECT status, COUNT(*) AS qtd
FROM dbacademy.churn.fato_assinatura
GROUP BY status
ORDER BY qtd DESC;

-- 2.3 Top motivos de cancelamento
SELECT motivo_cancelamento, COUNT(*) AS qtd
FROM dbacademy.churn.fato_assinatura
WHERE churn_flag = 1
GROUP BY motivo_cancelamento
ORDER BY qtd DESC;

-- 2.4 Taxa de churn por segmento
SELECT c.segmento, ROUND(AVG(a.churn_flag), 3) AS taxa_churn
FROM dbacademy.churn.fato_assinatura a
JOIN dbacademy.churn.dim_cliente c ON a.id_cliente = c.id_cliente
GROUP BY c.segmento
ORDER BY taxa_churn DESC;

-- Passo 4 (bônus) — Recursos Delta (somente leitura na base compartilhada) -----
DESCRIBE HISTORY dbacademy.churn.fato_assinatura;
DESCRIBE DETAIL  dbacademy.churn.dim_cliente;
-- Time travel: primeira versão da tabela
SELECT COUNT(*) FROM dbacademy.churn.fato_assinatura VERSION AS OF 0;

-- 🎯 DESAFIO — Qual plano tem a maior taxa de churn e quantos clientes perdeu?
-- (tente montar sozinho antes de olhar; confira pedindo ao Genie Code)
SELECT p.nome_plano,
       ROUND(AVG(a.churn_flag), 3) AS taxa_churn,
       SUM(a.churn_flag)           AS clientes_perdidos
FROM dbacademy.churn.fato_assinatura a
JOIN dbacademy.churn.dim_plano p ON a.id_plano = p.id_plano
GROUP BY p.nome_plano
ORDER BY taxa_churn DESC;
