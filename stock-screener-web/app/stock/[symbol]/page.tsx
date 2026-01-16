"use client";

import { useState, use } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { getStockBySymbol, getStockHistory } from "@/lib/queries";
import { ScoreCard } from "@/components/ScoreCard";
import { TradeIdeaModal } from "@/components/TradeIdeaModal";
import { TradingViewChart } from "@/components/charts/TradingViewChart";
import { TechnicalAnalysisWidget } from "@/components/charts/TechnicalAnalysisWidget";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatRatio,
  formatDate,
  cn,
  getScoreColor,
} from "@/lib/utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface StockPageProps {
  params: Promise<{ symbol: string }>;
}

export default function StockPage({ params }: StockPageProps) {
  const { symbol } = use(params);
  const [showTradeIdea, setShowTradeIdea] = useState(false);

  const { data: stock, isLoading } = useQuery({
    queryKey: ["stock", symbol],
    queryFn: () => getStockBySymbol(symbol),
  });

  const { data: history = [] } = useQuery({
    queryKey: ["stockHistory", symbol],
    queryFn: () => getStockHistory(symbol),
  });

  if (isLoading) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Loading stock data...
      </div>
    );
  }

  if (!stock) {
    return (
      <div className="space-y-4">
        <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
          &larr; Back to Dashboard
        </Link>
        <div className="p-8 text-center text-muted-foreground">
          Stock not found in the latest screener run.
        </div>
      </div>
    );
  }

  // Prepare history data for chart (reverse to show oldest first)
  const chartData = [...history].reverse().map((h) => ({
    date: new Date(h.run_date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    score: h.score,
    price: h.price,
  }));

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
        &larr; Back to Dashboard
      </Link>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">{stock.symbol}</h1>
          <p className="text-lg text-muted-foreground">{stock.name}</p>
          <div className="mt-2 flex gap-2 text-sm">
            <span className="rounded-full bg-muted px-2 py-0.5">
              {stock.sector || "N/A"}
            </span>
            <span className="rounded-full bg-muted px-2 py-0.5">
              {stock.industry || "N/A"}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          {stock.trade_idea && (
            <button
              onClick={() => setShowTradeIdea(true)}
              className="rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Trade Idea
            </button>
          )}
          <a
            href={`https://finance.yahoo.com/quote/${stock.symbol}`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border px-3 py-1.5 text-sm hover:bg-muted"
          >
            Yahoo Finance
          </a>
          <a
            href={`https://www.tradingview.com/symbols/${stock.exchange || "NASDAQ"}-${stock.symbol}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border px-3 py-1.5 text-sm hover:bg-muted"
          >
            TradingView
          </a>
        </div>
      </div>

      {/* Trade Idea Modal */}
      <TradeIdeaModal
        stock={stock}
        isOpen={showTradeIdea}
        onClose={() => setShowTradeIdea(false)}
      />

      {/* TradingView Chart Section */}
      <div className="grid gap-4 lg:grid-cols-4">
        {/* Price Chart - Large, 3/4 width */}
        <div className="lg:col-span-3 rounded-lg border bg-card p-4">
          <h3 className="font-semibold mb-2">Price Chart</h3>
          <TradingViewChart
            symbol={stock.symbol}
            exchange={stock.exchange || "NASDAQ"}
            height={2000}
            showIndicators={true}
          />
        </div>

        {/* Technical Analysis - Compact, 1/4 width, to the right */}
        <div className="lg:col-span-1 rounded-lg border bg-card p-4">
          <h3 className="font-semibold mb-2">Technical Analysis</h3>
          <TechnicalAnalysisWidget
            symbol={stock.symbol}
            exchange={stock.exchange || "NASDAQ"}
            height={300}
          />
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Score Card */}
        <div className="md:col-span-1">
          <ScoreCard stock={stock} />
        </div>

        {/* Metrics */}
        <div className="md:col-span-2 space-y-6">
          {/* Market Data */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Market Data</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricItem label="Price" value={formatCurrency(stock.price)} />
              <MetricItem label="Market Cap" value={formatNumber(stock.market_cap)} />
              <MetricItem label="Avg Volume" value={formatNumber(stock.avg_volume)} />
              <MetricItem label="Exchange" value={stock.exchange || "-"} />
            </div>
          </div>

          {/* Valuation Metrics */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Valuation</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricItem label="P/E Ratio" value={formatRatio(stock.pe_ratio, 1)} />
              <MetricItem label="PEG Ratio" value={formatRatio(stock.peg_ratio)} />
              <MetricItem label="P/B Ratio" value={formatRatio(stock.pb_ratio)} />
              <MetricItem label="P/S Ratio" value={formatRatio(stock.ps_ratio)} />
            </div>
          </div>

          {/* Growth Metrics */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Growth</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <MetricItem label="EPS Growth (5Y)" value={formatPercent(stock.eps_growth_5y)} />
              <MetricItem label="Revenue Growth (5Y)" value={formatPercent(stock.revenue_growth_5y)} />
              <MetricItem label="EPS Growth (TTM)" value={formatPercent(stock.eps_growth_ttm)} />
            </div>
          </div>

          {/* Profitability Metrics */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Profitability</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <MetricItem label="ROE" value={formatPercent(stock.roe)} />
              <MetricItem label="ROA" value={formatPercent(stock.roa)} />
              <MetricItem label="Gross Margin" value={formatPercent(stock.gross_margin)} />
              <MetricItem label="Operating Margin" value={formatPercent(stock.operating_margin)} />
              <MetricItem label="Net Margin" value={formatPercent(stock.net_margin)} />
            </div>
          </div>

          {/* Financial Health */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Financial Health</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricItem label="Current Ratio" value={formatRatio(stock.current_ratio)} />
              <MetricItem label="Quick Ratio" value={formatRatio(stock.quick_ratio)} />
              <MetricItem label="Debt/Equity" value={formatRatio(stock.debt_to_equity)} />
              <MetricItem label="Interest Coverage" value={formatRatio(stock.interest_coverage, 1)} />
            </div>
          </div>

          {/* Balance Highlights */}
          {(stock.revenue_ttm || stock.net_income_ttm || stock.free_cash_flow) && (
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-4">Balance Highlights</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <MetricItem label="Revenue (TTM)" value={formatNumber(stock.revenue_ttm)} />
                <MetricItem label="Net Income (TTM)" value={formatNumber(stock.net_income_ttm)} />
                <MetricItem label="Free Cash Flow" value={formatNumber(stock.free_cash_flow)} />
                <MetricItem label="Total Cash" value={formatNumber(stock.total_cash)} />
                <MetricItem label="Total Debt" value={formatNumber(stock.total_debt)} />
              </div>
            </div>
          )}

          {/* Earnings */}
          {stock.next_earnings_date && (
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold mb-4">Earnings</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <MetricItem label="Next Earnings Date" value={stock.next_earnings_date} />
                <MetricItem label="EPS This Year" value={formatPercent(stock.eps_this_year)} />
                <MetricItem label="EPS Next Year" value={formatPercent(stock.eps_next_year)} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* News and Related Assets */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* News */}
        {stock.news && stock.news.length > 0 && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Recent News</h3>
            <div className="space-y-3">
              {stock.news.map((item, i) => (
                <div key={i} className="border-b pb-3 last:border-0 last:pb-0">
                  <p className="font-medium text-sm">{item.title}</p>
                  <div className="flex gap-2 text-xs text-muted-foreground mt-1">
                    <span>{item.source}</span>
                    {item.date && <span>{item.date}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Related Assets */}
        {stock.related_assets && stock.related_assets.length > 0 && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="font-semibold mb-4">Related Assets</h3>
            <div className="space-y-2">
              {stock.related_assets.map((asset, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <span className="font-medium">{asset.symbol}</span>
                    <span className="text-muted-foreground text-sm ml-2">{asset.name}</span>
                    <span className="text-xs text-muted-foreground ml-2 rounded-full bg-muted px-2 py-0.5">
                      {asset.type}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatCurrency(asset.price)}</div>
                    <div className={cn(
                      "text-sm",
                      asset.change >= 0 ? "text-green-500" : "text-red-500"
                    )}>
                      {asset.change >= 0 ? "+" : ""}{asset.change?.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Historical Score Chart */}
      {chartData.length > 1 && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold mb-4">Score History</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis domain={[0, 10]} className="text-xs" />
                <Tooltip
                  formatter={(value: number) => [value.toFixed(2), "Score"]}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: "#3b82f6" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* History Table */}
      {history.length > 0 && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold mb-4">Run History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="px-4 py-2 text-left">Date</th>
                  <th className="px-4 py-2 text-left">Score</th>
                  <th className="px-4 py-2 text-left">Price</th>
                  <th className="px-4 py-2 text-left">P/E</th>
                  <th className="px-4 py-2 text-left">PEG</th>
                  <th className="px-4 py-2 text-left">ROE</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {history.map((h, i) => (
                  <tr key={i} className="hover:bg-muted/30">
                    <td className="px-4 py-2">{formatDate(h.run_date)}</td>
                    <td className={cn("px-4 py-2 font-medium", getScoreColor(h.score))}>
                      {h.score?.toFixed(1) || "-"}
                    </td>
                    <td className="px-4 py-2">{formatCurrency(h.price)}</td>
                    <td className="px-4 py-2">{formatRatio(h.pe_ratio, 1)}</td>
                    <td className="px-4 py-2">{formatRatio(h.peg_ratio)}</td>
                    <td className="px-4 py-2">{formatPercent(h.roe)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-medium">{value}</div>
    </div>
  );
}
