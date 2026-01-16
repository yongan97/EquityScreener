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
import { Download, Lock, Crown } from "lucide-react";
import { toast } from "sonner";
import { useAuth, PaywallModal } from "@/components/auth";
import Link from "next/link";

export default function Dashboard() {
  const { isPremium, isLoading: authLoading } = useAuth();
  const [showPaywall, setShowPaywall] = useState(false);
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
    const filtered = stocks.filter((stock) => {
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

    // Limit to 1 stock for non-premium users (free sample)
    if (!isPremium && !authLoading) {
      return filtered.slice(0, 1);
    }

    return filtered;
  }, [stocks, filters, isPremium, authLoading]);

  // Count of locked stocks for non-premium users
  const lockedCount = useMemo(() => {
    if (isPremium) return 0;
    return Math.max(0, stocks.length - 1);
  }, [stocks.length, isPremium]);

  const isLoading = runLoading || stocksLoading;

  // Export to CSV (premium only)
  const handleExport = () => {
    if (!isPremium) {
      setShowPaywall(true);
      return;
    }
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
              {isPremium ? (
                `Showing ${filteredStocks.length} of ${stocks.length} stocks`
              ) : (
                <>
                  Showing <span className="font-medium">1 free sample</span> of{" "}
                  {stocks.length} stocks
                </>
              )}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExport}
              disabled={filteredStocks.length === 0}
            >
              {!isPremium && <Lock className="mr-2 h-4 w-4" />}
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>

          {/* Premium upsell banner for free users */}
          {!isPremium && !authLoading && lockedCount > 0 && (
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Lock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  <div>
                    <p className="font-medium">
                      {lockedCount} more AI-analyzed stocks available
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Upgrade to Premium for $5/month to unlock all picks
                    </p>
                  </div>
                </div>
                <Button
                  className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                  onClick={() => setShowPaywall(true)}
                >
                  <Crown className="mr-2 h-4 w-4" />
                  Upgrade
                </Button>
              </div>
            </div>
          )}

          <StockTable
            stocks={filteredStocks}
            isLoading={isLoading}
            isPremium={isPremium}
            onUpgradeClick={() => setShowPaywall(true)}
          />
        </div>
      </div>

      <PaywallModal
        isOpen={showPaywall}
        onClose={() => setShowPaywall(false)}
        feature="CSV Export"
      />
    </div>
  );
}
