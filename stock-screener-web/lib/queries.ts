import { supabase } from "./supabase";
import type { Stock, ScreenerRun, StockHistory, SectorStats } from "@/types/stock";

/**
 * Get the most recent screener run metadata
 */
export async function getLatestRun(): Promise<ScreenerRun | null> {
  const { data, error } = await supabase
    .from("screener_runs")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(1)
    .single();

  if (error) {
    console.error("Error fetching latest run:", error);
    return null;
  }

  return data;
}

/**
 * Get stocks from the most recent screener run
 */
export async function getLatestStocks(limit = 100): Promise<Stock[]> {
  const { data, error } = await supabase
    .from("latest_stocks")
    .select("*")
    .order("score", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Error fetching latest stocks:", error);
    return [];
  }

  return data || [];
}

/**
 * Get all stocks with optional filtering
 */
export async function getStocks(options: {
  runId?: string;
  sectors?: string[];
  scoreMin?: number;
  scoreMax?: number;
  search?: string;
  limit?: number;
}): Promise<Stock[]> {
  let query = supabase.from("stocks").select("*");

  if (options.runId) {
    query = query.eq("run_id", options.runId);
  }

  if (options.sectors && options.sectors.length > 0) {
    query = query.in("sector", options.sectors);
  }

  if (options.scoreMin !== undefined) {
    query = query.gte("score", options.scoreMin);
  }

  if (options.scoreMax !== undefined) {
    query = query.lte("score", options.scoreMax);
  }

  if (options.search) {
    query = query.or(
      `symbol.ilike.%${options.search}%,name.ilike.%${options.search}%`
    );
  }

  query = query.order("score", { ascending: false });

  if (options.limit) {
    query = query.limit(options.limit);
  }

  const { data, error } = await query;

  if (error) {
    console.error("Error fetching stocks:", error);
    return [];
  }

  return data || [];
}

/**
 * Get a single stock by symbol from the latest run
 */
export async function getStockBySymbol(symbol: string): Promise<Stock | null> {
  const { data, error } = await supabase
    .from("latest_stocks")
    .select("*")
    .eq("symbol", symbol.toUpperCase())
    .single();

  if (error) {
    console.error("Error fetching stock:", error);
    return null;
  }

  return data;
}

/**
 * Get historical data for a stock symbol
 */
export async function getStockHistory(
  symbol: string,
  limit = 30
): Promise<StockHistory[]> {
  const { data, error } = await supabase
    .from("stock_history")
    .select("*")
    .eq("symbol", symbol.toUpperCase())
    .order("run_date", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Error fetching stock history:", error);
    return [];
  }

  return data || [];
}

/**
 * Get screener run history
 */
export async function getRunHistory(limit = 30): Promise<ScreenerRun[]> {
  const { data, error } = await supabase
    .from("screener_runs")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Error fetching run history:", error);
    return [];
  }

  return data || [];
}

/**
 * Get unique sectors from latest stocks
 */
export async function getSectors(): Promise<string[]> {
  const { data, error } = await supabase
    .from("latest_stocks")
    .select("sector")
    .not("sector", "is", null);

  if (error) {
    console.error("Error fetching sectors:", error);
    return [];
  }

  const sectors = [...new Set(data?.map((d) => d.sector).filter(Boolean))];
  return sectors.sort();
}

/**
 * Get sector statistics from latest run
 */
export async function getSectorStats(): Promise<SectorStats[]> {
  const stocks = await getLatestStocks(500);

  const sectorMap = new Map<string, { count: number; totalScore: number }>();

  stocks.forEach((stock) => {
    if (stock.sector) {
      const current = sectorMap.get(stock.sector) || { count: 0, totalScore: 0 };
      sectorMap.set(stock.sector, {
        count: current.count + 1,
        totalScore: current.totalScore + (stock.score || 0),
      });
    }
  });

  return Array.from(sectorMap.entries())
    .map(([sector, stats]) => ({
      sector,
      count: stats.count,
      avgScore: stats.count > 0 ? stats.totalScore / stats.count : 0,
    }))
    .sort((a, b) => b.count - a.count);
}

/**
 * Get stocks for comparison
 */
export async function getStocksForComparison(
  symbols: string[]
): Promise<Stock[]> {
  const { data, error } = await supabase
    .from("latest_stocks")
    .select("*")
    .in(
      "symbol",
      symbols.map((s) => s.toUpperCase())
    );

  if (error) {
    console.error("Error fetching stocks for comparison:", error);
    return [];
  }

  return data || [];
}
