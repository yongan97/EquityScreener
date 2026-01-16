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
import { Copy, Check } from "lucide-react";
import { useState } from "react";

interface TradeIdeaModalProps {
  stock: Stock;
  isOpen: boolean;
  onClose: () => void;
}

export function TradeIdeaModal({ stock, isOpen, onClose }: TradeIdeaModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (stock.trade_idea) {
      await navigator.clipboard.writeText(stock.trade_idea);
      setCopied(true);
      toast.success("Trade idea copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
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
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{stock.trade_idea}</ReactMarkdown>
            </div>
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
