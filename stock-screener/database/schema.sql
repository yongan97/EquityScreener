-- Supabase Schema for Stock Screener GARP
-- Run this in the Supabase SQL Editor to create the database structure

-- Enable UUID extension (usually enabled by default in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: screener_runs
-- Stores metadata about each screener execution
CREATE TABLE screener_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_name TEXT NOT NULL,
    total_scanned INTEGER NOT NULL DEFAULT 0,
    total_matches INTEGER NOT NULL DEFAULT 0,
    execution_time_seconds FLOAT,
    errors TEXT[], -- Array of error messages if any
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: stocks
-- Stores individual stock results from each screener run
CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES screener_runs(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT,
    sector TEXT,
    industry TEXT,
    price FLOAT,
    market_cap BIGINT,
    avg_volume BIGINT,

    -- Valuation metrics
    pe_ratio FLOAT,
    peg_ratio FLOAT,
    pb_ratio FLOAT,
    ps_ratio FLOAT,

    -- Growth metrics
    eps_growth_5y FLOAT,
    revenue_growth_5y FLOAT,
    eps_growth_ttm FLOAT,

    -- Profitability metrics
    roe FLOAT,
    roa FLOAT,
    gross_margin FLOAT,
    operating_margin FLOAT,
    net_margin FLOAT,

    -- Liquidity metrics
    current_ratio FLOAT,
    quick_ratio FLOAT,

    -- Solvency metrics
    debt_to_equity FLOAT,
    interest_coverage FLOAT,

    -- Scores
    score FLOAT,
    score_valuation FLOAT,
    score_growth FLOAT,
    score_profitability FLOAT,
    score_financial_health FLOAT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_stocks_run_id ON stocks(run_id);
CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_stocks_score ON stocks(score DESC);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_screener_runs_created_at ON screener_runs(created_at DESC);

-- View: latest_stocks
-- Returns stocks from the most recent screener run
CREATE VIEW latest_stocks AS
SELECT s.*
FROM stocks s
JOIN screener_runs r ON s.run_id = r.id
WHERE r.id = (
    SELECT id
    FROM screener_runs
    ORDER BY created_at DESC
    LIMIT 1
);

-- View: latest_run
-- Returns the most recent screener run metadata
CREATE VIEW latest_run AS
SELECT *
FROM screener_runs
ORDER BY created_at DESC
LIMIT 1;

-- View: stock_history
-- Returns historical data for each stock symbol across all runs
CREATE VIEW stock_history AS
SELECT
    s.symbol,
    s.name,
    s.score,
    s.price,
    s.pe_ratio,
    s.peg_ratio,
    s.roe,
    r.created_at as run_date,
    r.config_name
FROM stocks s
JOIN screener_runs r ON s.run_id = r.id
ORDER BY s.symbol, r.created_at DESC;

-- Function: get_stock_comparison
-- Compare metrics between two runs
CREATE OR REPLACE FUNCTION get_stock_comparison(run_id_1 UUID, run_id_2 UUID)
RETURNS TABLE (
    symbol TEXT,
    name TEXT,
    score_1 FLOAT,
    score_2 FLOAT,
    score_change FLOAT,
    price_1 FLOAT,
    price_2 FLOAT,
    in_run_1 BOOLEAN,
    in_run_2 BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(s1.symbol, s2.symbol) as symbol,
        COALESCE(s1.name, s2.name) as name,
        s1.score as score_1,
        s2.score as score_2,
        COALESCE(s2.score, 0) - COALESCE(s1.score, 0) as score_change,
        s1.price as price_1,
        s2.price as price_2,
        s1.id IS NOT NULL as in_run_1,
        s2.id IS NOT NULL as in_run_2
    FROM
        (SELECT * FROM stocks WHERE stocks.run_id = run_id_1) s1
    FULL OUTER JOIN
        (SELECT * FROM stocks WHERE stocks.run_id = run_id_2) s2
    ON s1.symbol = s2.symbol
    ORDER BY score_change DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) - Optional, enable if needed for multi-user
-- ALTER TABLE screener_runs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;

-- Grant permissions for anonymous access (for public dashboard)
-- Uncomment these after creating the tables if you want public read access
-- GRANT SELECT ON screener_runs TO anon;
-- GRANT SELECT ON stocks TO anon;
-- GRANT SELECT ON latest_stocks TO anon;
-- GRANT SELECT ON latest_run TO anon;
-- GRANT SELECT ON stock_history TO anon;

COMMENT ON TABLE screener_runs IS 'Stores metadata about each stock screener execution';
COMMENT ON TABLE stocks IS 'Stores individual stock results with all metrics and scores';
COMMENT ON VIEW latest_stocks IS 'Returns stocks from the most recent screener run';
COMMENT ON VIEW latest_run IS 'Returns metadata from the most recent screener run';
COMMENT ON VIEW stock_history IS 'Historical data for tracking stock scores over time';
