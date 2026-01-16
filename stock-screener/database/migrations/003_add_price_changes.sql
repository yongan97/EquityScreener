-- Migración: Agregar campos de variación de precio
-- Ejecutar en Supabase SQL Editor

-- Agregar campos de performance de precio
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS perf_1d REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS perf_1w REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS perf_1m REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS perf_ytd REAL;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS perf_52w REAL;

-- Índices para mejor performance en ordenamiento
CREATE INDEX IF NOT EXISTS idx_stocks_perf_1d ON stocks(perf_1d DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_perf_1w ON stocks(perf_1w DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_perf_1m ON stocks(perf_1m DESC);

-- Comentarios
COMMENT ON COLUMN stocks.perf_1d IS 'Variación de precio 1 día (decimal, ej: 0.05 = +5%)';
COMMENT ON COLUMN stocks.perf_1w IS 'Variación de precio 1 semana (decimal)';
COMMENT ON COLUMN stocks.perf_1m IS 'Variación de precio 1 mes (decimal)';
COMMENT ON COLUMN stocks.perf_ytd IS 'Variación de precio Year-to-Date (decimal)';
COMMENT ON COLUMN stocks.perf_52w IS 'Variación de precio 52 semanas (decimal)';
