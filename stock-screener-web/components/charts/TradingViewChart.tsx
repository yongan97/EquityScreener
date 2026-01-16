"use client";

import { memo } from "react";
import { AdvancedRealTimeChart, Studies } from "react-ts-tradingview-widgets";

// Map Yahoo Finance exchange codes to TradingView exchange codes
function mapExchangeToTradingView(exchange: string | null | undefined): string {
  const exchangeMap: Record<string, string> = {
    // NYSE variants
    NYQ: "NYSE",
    NYSE: "NYSE",
    // NASDAQ variants
    NMS: "NASDAQ",
    NGM: "NASDAQ",
    NCM: "NASDAQ",
    NASDAQ: "NASDAQ",
    // AMEX variants
    PCX: "AMEX",
    ASE: "AMEX",
    AMEX: "AMEX",
    // Other
    ARCA: "AMEX",
    BATS: "BATS",
  };

  if (!exchange) return "NASDAQ";
  return exchangeMap[exchange.toUpperCase()] || "NASDAQ";
}

interface TradingViewChartProps {
  symbol: string;
  exchange?: string;
  height?: number;
  showIndicators?: boolean;
}

function TradingViewChartComponent({
  symbol,
  exchange = "NASDAQ",
  height = 500,
  showIndicators = true,
}: TradingViewChartProps) {
  // Format symbol for TradingView (EXCHANGE:SYMBOL)
  const tvExchange = mapExchangeToTradingView(exchange);
  const tvSymbol = `${tvExchange}:${symbol}`;

  // Default studies for technical analysis
  const defaultStudies: Studies[] = showIndicators
    ? [
        "MASimple@tv-basicstudies" as Studies, // SMA
        "MAExp@tv-basicstudies" as Studies, // EMA
        "Volume@tv-basicstudies" as Studies, // Volume
      ]
    : [];

  return (
    <div style={{ height: `${height}px`, minHeight: `${height}px` }}>
      <AdvancedRealTimeChart
        symbol={tvSymbol}
        theme="dark"
        autosize={false}
        width="100%"
        height={height}
        interval="D"
        timezone="America/New_York"
        style="1"
        locale="en"
        toolbar_bg="#1e1e1e"
        enable_publishing={false}
        hide_top_toolbar={false}
        hide_legend={false}
        save_image={true}
        studies={defaultStudies}
        container_id={`tradingview-chart-${symbol}`}
      />
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const TradingViewChart = memo(TradingViewChartComponent);
