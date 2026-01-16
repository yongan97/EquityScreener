-- Migración: Agregar campos de análisis IA y Trade Ideas
-- Ejecutar en Supabase SQL Editor

-- Agregar nuevos campos a la tabla stocks
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS peg_finviz REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS fwd_pe REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS eps_this_year REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS eps_next_year REAL;

-- Balance highlights
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS revenue_ttm BIGINT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS net_income_ttm BIGINT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS free_cash_flow BIGINT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS total_cash BIGINT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS total_debt BIGINT;

-- AI Score components
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_score REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_fundamental REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_valuation REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_growth REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_momentum REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_sentiment REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS ai_quality REAL;

-- Analysis details
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS momentum_trend TEXT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS sentiment_summary TEXT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS growth_outlook TEXT;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS valuation_vs_sector TEXT;

-- JSON fields
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS flags JSONB;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS news JSONB;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS related_assets JSONB;

-- Earnings
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS next_earnings_date TEXT;

-- Trade Idea (markdown completo)
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS trade_idea TEXT;

-- Índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_stocks_ai_score ON stocks(ai_score DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_run_symbol ON stocks(run_id, symbol);

-- Actualizar la vista latest_stocks para incluir AI score
DROP VIEW IF EXISTS latest_stocks;
CREATE VIEW latest_stocks AS
SELECT s.*
FROM stocks s
INNER JOIN (
    SELECT id FROM screener_runs ORDER BY created_at DESC LIMIT 1
) r ON s.run_id = r.id
ORDER BY COALESCE(s.ai_score, s.score) DESC;

-- Comentarios
COMMENT ON COLUMN stocks.ai_score IS 'Score IA total (0-10)';
COMMENT ON COLUMN stocks.trade_idea IS 'Trade Idea completa en formato Markdown';
COMMENT ON COLUMN stocks.flags IS 'Array de flags de oportunidad/riesgo';
COMMENT ON COLUMN stocks.news IS 'Array de últimas noticias';
COMMENT ON COLUMN stocks.related_assets IS 'Array de activos relacionados (commodities, ETFs, índices)';
