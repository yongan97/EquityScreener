"use client";

import { memo } from "react";
import { TechnicalAnalysis } from "react-ts-tradingview-widgets";

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
  const tvSymbol = `${exchange}:${symbol}`;

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
