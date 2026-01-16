"use client";

import type { Stock } from "@/types/stock";
import { cn, getScoreColor } from "@/lib/utils";

interface ScoreCardProps {
  stock: Stock;
}

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
    if (!score) return { text: "-", color: "text-muted-foreground" };
    if (score >= 7.5) return { text: "STRONG BUY", color: "text-green-500" };
    if (score >= 6.5) return { text: "BUY", color: "text-emerald-500" };
    if (score >= 5.5) return { text: "HOLD", color: "text-yellow-500" };
    return { text: "WATCH", color: "text-orange-500" };
  };

  const recommendation = getRecommendation(mainScore);

  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="mb-4 text-center">
        <div className="text-sm text-muted-foreground">
          {hasAIScore ? "AI Score" : "Overall Score"}
        </div>
        <div
          className={cn("text-5xl font-bold", getScoreColor(mainScore))}
        >
          {mainScore?.toFixed(1) || "-"}
        </div>
        <div className="text-sm text-muted-foreground">out of 10</div>
        {hasAIScore && (
          <div className={cn("mt-2 text-lg font-semibold", recommendation.color)}>
            {recommendation.text}
          </div>
        )}
      </div>

      <div className="space-y-3">
        {scores.map((score) => (
          <div key={score.label}>
            <div className="flex justify-between text-sm">
              <span>{score.label}</span>
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
      {hasAIScore && (
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
            <span
              key={i}
              className={cn(
                "rounded-full px-2 py-0.5 text-xs",
                flag.includes("Undervalued") || flag.includes("Growth") || flag.includes("Strong")
                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  : flag.includes("Risk") || flag.includes("Warning") || flag.includes("Debt")
                  ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {flag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
