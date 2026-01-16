"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  getLatestRun,
  getLatestStocks,
  getSectors,
  getSectorStats,
} from "@/lib/queries";
import type { StockFilters } from "@/types/stock";
import { SummaryCards } from "@/components/SummaryCards";
import { StockTable } from "@/components/StockTable";
import { StockFiltersComponent } from "@/components/StockFilters";
import { SectorChart } from "@/components/SectorChart";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { toast } from "sonner";

export default function Dashboard() {
  const [filters, setFilters] = useState<StockFilters>({
    sectors: [],
    scoreMin: 0,
    scoreMax: 10,
    search: "",
  });

  // Fetch data
  const { data: run, isLoading: runLoading } = useQuery({
    queryKey: ["latestRun"],
    queryFn: getLatestRun,
  });

  const { data: stocks = [], isLoading: stocksLoading } = useQuery({
    queryKey: ["latestStocks"],
    queryFn: () => getLatestStocks(500),
  });

  const { data: sectors = [] } = useQuery({
    queryKey: ["sectors"],
    queryFn: getSectors,
  });

  const { data: sectorStats = [] } = useQuery({
    queryKey: ["sectorStats"],
    queryFn: getSectorStats,
  });

  // Filter stocks client-side for instant filtering
  const filteredStocks = useMemo(() => {
    return stocks.filter((stock) => {
      // Search filter
      if (filters.search) {
        const search = filters.search.toLowerCase();
        if (
          !stock.symbol.toLowerCase().includes(search) &&
          !stock.name.toLowerCase().includes(search)
        ) {
          return false;
        }
      }

      // Sector filter
      if (filters.sectors.length > 0) {
        if (!stock.sector || !filters.sectors.includes(stock.sector)) {
          return false;
        }
      }

      // Score filter
      const score = stock.score ?? 0;
      if (score < filters.scoreMin || score > filters.scoreMax) {
        return false;
      }

      return true;
    });
  }, [stocks, filters]);

  const isLoading = runLoading || stocksLoading;

  // Export to CSV
  const handleExport = () => {
    if (filteredStocks.length === 0) return;

    const headers = [
      "Symbol",
      "Name",
      "Score",
      "Price",
      "Market Cap",
      "P/E",
      "PEG",
      "ROE",
      "D/E",
      "Sector",
    ];

    const rows = filteredStocks.map((s) => [
      s.symbol,
      `"${s.name}"`,
      s.score?.toFixed(2) ?? "",
      s.price?.toFixed(2) ?? "",
      s.market_cap ?? "",
      s.pe_ratio?.toFixed(2) ?? "",
      s.peg_ratio?.toFixed(2) ?? "",
      s.roe ? (s.roe * 100).toFixed(2) : "",
      s.debt_to_equity?.toFixed(2) ?? "",
      s.sector ?? "",
    ]);

    const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `stock-screener-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Exported ${filteredStocks.length} stocks to CSV`);
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <SummaryCards
        run={run}
        stocks={filteredStocks}
        sectorStats={sectorStats}
        isLoading={isLoading}
      />

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <StockFiltersComponent
            sectors={sectors}
            filters={filters}
            onFiltersChange={setFilters}
          />
          <SectorChart sectorStats={sectorStats} />
        </div>

        {/* Stock Table */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {filteredStocks.length} of {stocks.length} stocks
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExport}
              disabled={filteredStocks.length === 0}
            >
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
          <StockTable stocks={filteredStocks} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
