"use client";

import { memo } from "react";
import { TechnicalAnalysis } from "react-ts-tradingview-widgets";

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

interface TechnicalAnalysisWidgetProps {
  symbol: string;
  exchange?: string;
  height?: number;
}

function TechnicalAnalysisWidgetComponent({
  symbol,
  exchange = "NASDAQ",
  height = 400,
}: TechnicalAnalysisWidgetProps) {
  // Format symbol for TradingView (EXCHANGE:SYMBOL)
  const tvExchange = mapExchangeToTradingView(exchange);
  const tvSymbol = `${tvExchange}:${symbol}`;

  return (
    <div className="overflow-hidden rounded-lg">
      <TechnicalAnalysis
        symbol={tvSymbol}
        colorTheme="dark"
        isTransparent={false}
        width="100%"
        height={height}
        showIntervalTabs={true}
        locale="en"
      />
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const TechnicalAnalysisWidget = memo(TechnicalAnalysisWidgetComponent);
