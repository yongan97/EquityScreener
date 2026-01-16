"use client";

import { useMemo, useState } from "react";
import type { Stock } from "@/types/stock";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DataTable } from "@/components/ui/data-table";
import { createColumns } from "@/components/stocks/columns";
import { TradeIdeaModal } from "@/components/TradeIdeaModal";

interface StockTableProps {
  stocks: Stock[];
  isLoading?: boolean;
}

export function StockTable({ stocks, isLoading }: StockTableProps) {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewTradeIdea = (stock: Stock) => {
    setSelectedStock(stock);
    setIsModalOpen(true);
  };

  const columns = useMemo(
    () => createColumns({ onViewTradeIdea: handleViewTradeIdea }),
    []
  );

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-3">
            <Skeleton className="h-10 w-full" />
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (stocks.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-muted-foreground">
          No stocks found matching your criteria.
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <DataTable columns={columns} data={stocks} pageSize={20} />
      {selectedStock && (
        <TradeIdeaModal
          stock={selectedStock}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
}
