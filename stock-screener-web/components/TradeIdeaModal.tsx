"use client";

import { useState } from "react";
import type { Stock } from "@/types/stock";
import ReactMarkdown from "react-markdown";

interface TradeIdeaModalProps {
  stock: Stock;
  isOpen: boolean;
  onClose: () => void;
}

export function TradeIdeaModal({ stock, isOpen, onClose }: TradeIdeaModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = async () => {
    if (stock.trade_idea) {
      await navigator.clipboard.writeText(stock.trade_idea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="relative max-h-[90vh] w-full max-w-3xl overflow-hidden rounded-lg bg-background shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-xl font-semibold">
            Trade Idea: {stock.symbol}
          </h2>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              {copied ? "Copied!" : "Copy to Clipboard"}
            </button>
            <button
              onClick={onClose}
              className="rounded-md border px-3 py-2 text-sm hover:bg-muted"
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="max-h-[calc(90vh-80px)] overflow-y-auto p-6">
          {stock.trade_idea ? (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{stock.trade_idea}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-center text-muted-foreground py-12">
              No trade idea available for this stock.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
