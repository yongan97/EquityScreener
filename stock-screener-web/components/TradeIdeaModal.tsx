"use client";

import type { Stock } from "@/types/stock";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Copy, Check, Lock, Crown, TrendingUp, BarChart3 } from "lucide-react";
import { useState } from "react";

interface TradeIdeaModalProps {
  stock: Stock;
  isOpen: boolean;
  onClose: () => void;
  isPremium?: boolean;
  onUpgradeClick?: () => void;
}

export function TradeIdeaModal({
  stock,
  isOpen,
  onClose,
  isPremium = false,
  onUpgradeClick,
}: TradeIdeaModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!isPremium) {
      onUpgradeClick?.();
      return;
    }
    if (stock.trade_idea) {
      await navigator.clipboard.writeText(stock.trade_idea);
      setCopied(true);
      toast.success("Trade idea copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Extract just the title/first line for free users
  const getTradeIdeaPreview = () => {
    if (!stock.trade_idea) return null;
    const lines = stock.trade_idea.split("\n").filter((line) => line.trim());
    // Get first heading or first line
    const titleLine = lines.find((line) => line.startsWith("#")) || lines[0];
    return titleLine?.replace(/^#+\s*/, "") || "Trade Idea Available";
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <div className="flex items-center justify-between pr-8">
            <div>
              <DialogTitle>Trade Idea: {stock.symbol}</DialogTitle>
              <DialogDescription>
                AI-generated analysis and trade setup for {stock.name}
              </DialogDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              disabled={!stock.trade_idea}
            >
              {!isPremium && <Lock className="mr-2 h-4 w-4" />}
              {copied ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto pr-2">
          {stock.trade_idea ? (
            isPremium ? (
              // Full trade idea for premium users
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{stock.trade_idea}</ReactMarkdown>
              </div>
            ) : (
              // Preview for free users
              <div className="space-y-6">
                {/* Preview of title */}
                <div className="border-b pb-4">
                  <h3 className="text-lg font-semibold">{getTradeIdeaPreview()}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    AI Score: {stock.ai_score?.toFixed(1) ?? stock.score?.toFixed(1) ?? "N/A"}/10
                  </p>
                </div>

                {/* Blurred preview */}
                <div className="relative">
                  <div className="blur-sm select-none pointer-events-none opacity-50">
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <p>
                        <strong>Entry Point:</strong> This analysis includes specific entry points based on technical and
                        fundamental analysis, considering current market conditions...
                      </p>
                      <p>
                        <strong>Exit Strategy:</strong> Target price levels and stop-loss recommendations with risk/reward
                        calculations...
                      </p>
                      <p>
                        <strong>Key Catalysts:</strong> Upcoming earnings, sector trends, and macroeconomic factors
                        that could impact the stock...
                      </p>
                    </div>
                  </div>

                  {/* Upgrade overlay */}
                  <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-t from-background via-background/80 to-transparent">
                    <div className="text-center p-6 max-w-md">
                      <Lock className="h-12 w-12 mx-auto text-amber-500 mb-4" />
                      <h3 className="text-xl font-bold mb-2">
                        Full Trade Idea Locked
                      </h3>
                      <p className="text-muted-foreground mb-4">
                        Upgrade to Premium to see complete entry/exit points, risk analysis, and detailed trade setup.
                      </p>
                      <ul className="text-sm text-left space-y-2 mb-6">
                        <li className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-green-500" />
                          Specific entry & exit points
                        </li>
                        <li className="flex items-center gap-2">
                          <BarChart3 className="h-4 w-4 text-blue-500" />
                          Risk/reward analysis
                        </li>
                        <li className="flex items-center gap-2">
                          <Crown className="h-4 w-4 text-amber-500" />
                          AI-powered trade catalysts
                        </li>
                      </ul>
                      <Button
                        className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                        onClick={onUpgradeClick}
                      >
                        <Crown className="mr-2 h-4 w-4" />
                        Upgrade for $5/month
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )
          ) : (
            <div className="text-center text-muted-foreground py-12">
              No trade idea available for this stock.
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
