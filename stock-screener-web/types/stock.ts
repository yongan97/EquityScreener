// Database types matching Supabase schema

export interface ScreenerRun {
  id: string;
  config_name: string;
  total_scanned: number;
  total_matches: number;
  execution_time_seconds: number | null;
  errors: string[] | null;
  created_at: string;
}

export interface Stock {
  id: string;
  run_id: string;
  symbol: string;
  name: string;
  exchange: string | null;
  sector: string | null;
  industry: string | null;
  price: number | null;
  market_cap: number | null;
  avg_volume: number | null;

  // Valuation metrics
  pe_ratio: number | null;
  peg_ratio: number | null;
  peg_finviz: number | null;
  fwd_pe: number | null;
  pb_ratio: number | null;
  ps_ratio: number | null;

  // Growth metrics
  eps_growth_5y: number | null;
  revenue_growth_5y: number | null;
  eps_growth_ttm: number | null;
  eps_this_year: number | null;
  eps_next_year: number | null;

  // Profitability metrics
  roe: number | null;
  roa: number | null;
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;

  // Liquidity metrics
  current_ratio: number | null;
  quick_ratio: number | null;

  // Solvency metrics
  debt_to_equity: number | null;
  interest_coverage: number | null;

  // Balance highlights
  revenue_ttm: number | null;
  net_income_ttm: number | null;
  free_cash_flow: number | null;
  total_cash: number | null;
  total_debt: number | null;

  // Scores (basic)
  score: number | null;
  score_valuation: number | null;
  score_growth: number | null;
  score_profitability: number | null;
  score_financial_health: number | null;

  // AI Score components
  ai_score: number | null;
  ai_fundamental: number | null;
  ai_valuation: number | null;
  ai_growth: number | null;
  ai_momentum: number | null;
  ai_sentiment: number | null;
  ai_quality: number | null;

  // Analysis details
  momentum_trend: string | null;
  sentiment_summary: string | null;
  growth_outlook: string | null;
  valuation_vs_sector: string | null;

  // JSON fields
  flags: string[] | null;
  news: NewsItem[] | null;
  related_assets: RelatedAsset[] | null;

  // Earnings
  next_earnings_date: string | null;

  // Price Performance
  perf_1d: number | null;
  perf_1w: number | null;
  perf_1m: number | null;
  perf_ytd: number | null;
  perf_52w: number | null;

  // Trade Idea (markdown)
  trade_idea: string | null;

  created_at: string;
}

export interface NewsItem {
  title: string;
  date: string | null;
  source: string;
}

export interface RelatedAsset {
  symbol: string;
  name: string;
  price: number;
  change: number;
  type: string;
}

export interface StockHistory {
  symbol: string;
  name: string;
  score: number | null;
  price: number | null;
  pe_ratio: number | null;
  peg_ratio: number | null;
  roe: number | null;
  run_date: string;
  config_name: string;
}

// Utility types for filtering
export interface StockFilters {
  sectors: string[];
  scoreMin: number;
  scoreMax: number;
  search: string;
}

// Sector statistics
export interface SectorStats {
  sector: string;
  count: number;
  avgScore: number;
}
