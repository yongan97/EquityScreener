"use client";

import type { Stock } from "@/types/stock";
import { cn, getScoreColor } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ScoreCardProps {
  stock: Stock;
}

const scoreDescriptions: Record<string, string> = {
  "Fundamental": "Overall company fundamentals including balance sheet health",
  "Valuation": "How fairly priced the stock is relative to earnings and growth",
  "Growth": "Revenue and earnings growth trajectory",
  "Momentum": "Price and volume trends indicating market sentiment",
  "Sentiment": "News and analyst sentiment analysis",
  "Quality": "Business quality metrics like ROE, margins, and consistency",
  "Profitability": "Operating margins, net margins, and return metrics",
  "Financial Health": "Debt levels, cash position, and liquidity",
};

export function ScoreCard({ stock }: ScoreCardProps) {
  // Use AI score if available, otherwise fallback to basic score
  const hasAIScore = stock.ai_score !== null && stock.ai_score !== undefined;
  const mainScore = hasAIScore ? stock.ai_score : stock.score;

  const aiScores = [
    { label: "Fundamental", value: stock.ai_fundamental, max: 10 },
    { label: "Valuation", value: stock.ai_valuation, max: 10 },
    { label: "Growth", value: stock.ai_growth, max: 10 },
    { label: "Momentum", value: stock.ai_momentum, max: 10 },
    { label: "Sentiment", value: stock.ai_sentiment, max: 10 },
    { label: "Quality", value: stock.ai_quality, max: 10 },
  ];

  const basicScores = [
    { label: "Valuation", value: stock.score_valuation, max: 10 },
    { label: "Growth", value: stock.score_growth, max: 10 },
    { label: "Profitability", value: stock.score_profitability, max: 10 },
    { label: "Financial Health", value: stock.score_financial_health, max: 10 },
  ];

  const scores = hasAIScore ? aiScores : basicScores;

  // Get recommendation based on AI score
  const getRecommendation = (score: number | null) => {
    if (!score) return { text: "-", variant: "outline" as const, icon: Minus };
    if (score >= 7.5) return { text: "STRONG BUY", variant: "default" as const, icon: TrendingUp };
    if (score >= 6.5) return { text: "BUY", variant: "secondary" as const, icon: TrendingUp };
    if (score >= 5.5) return { text: "HOLD", variant: "outline" as const, icon: Minus };
    return { text: "WATCH", variant: "destructive" as const, icon: TrendingDown };
  };

  const recommendation = getRecommendation(mainScore);

  const getFlagVariant = (flag: string): "default" | "secondary" | "destructive" | "outline" => {
    if (flag.includes("Undervalued") || flag.includes("Growth") || flag.includes("Strong")) {
      return "default";
    }
    if (flag.includes("Risk") || flag.includes("Warning") || flag.includes("Debt")) {
      return "destructive";
    }
    return "secondary";
  };

  return (
    <TooltipProvider>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-center text-sm font-medium text-muted-foreground">
            {hasAIScore ? "AI Score" : "Overall Score"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 text-center">
            <div className={cn("text-5xl font-bold", getScoreColor(mainScore))}>
              {mainScore?.toFixed(1) || "-"}
            </div>
            <div className="text-sm text-muted-foreground">out of 10</div>
            {hasAIScore && (
              <Badge
                variant={recommendation.variant}
                className={cn(
                  "mt-3",
                  recommendation.text === "STRONG BUY" && "bg-green-500 hover:bg-green-600",
                  recommendation.text === "BUY" && "bg-emerald-500 hover:bg-emerald-600"
                )}
              >
                <recommendation.icon className="mr-1 h-3 w-3" />
                {recommendation.text}
              </Badge>
            )}
          </div>

          <div className="space-y-3">
            {scores.map((score) => (
              <div key={score.label}>
                <div className="flex justify-between text-sm">
                  <div className="flex items-center gap-1">
                    <span>{score.label}</span>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs">{scoreDescriptions[score.label]}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <span className={cn("font-medium", getScoreColor(score.value))}>
                    {score.value?.toFixed(1) || "-"}
                  </span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-muted">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      score.value !== null && score.value >= 8
                        ? "bg-green-500"
                        : score.value !== null && score.value >= 6
                        ? "bg-emerald-500"
                        : score.value !== null && score.value >= 4
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    )}
                    style={{
                      width: `${((score.value || 0) / score.max) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Analysis insights */}
          {hasAIScore && (stock.momentum_trend || stock.growth_outlook || stock.valuation_vs_sector) && (
            <div className="mt-6 space-y-2 border-t pt-4">
              {stock.momentum_trend && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Momentum: </span>
                  <span className="font-medium">{stock.momentum_trend}</span>
                </div>
              )}
              {stock.growth_outlook && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Growth: </span>
                  <span className="font-medium">{stock.growth_outlook}</span>
                </div>
              )}
              {stock.valuation_vs_sector && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Valuation: </span>
                  <span className="font-medium">{stock.valuation_vs_sector}</span>
                </div>
              )}
            </div>
          )}

          {/* Flags */}
          {stock.flags && stock.flags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-1">
              {stock.flags.map((flag, i) => (
                <Badge
                  key={i}
                  variant={getFlagVariant(flag)}
                  className={cn(
                    "text-xs",
                    getFlagVariant(flag) === "default" && "bg-green-500 hover:bg-green-600"
                  )}
                >
                  {flag}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}
