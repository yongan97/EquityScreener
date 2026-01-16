"use client";

import type { ScreenerRun, Stock, SectorStats } from "@/types/stock";
import { formatNumber, getRelativeTime } from "@/lib/utils";

interface SummaryCardsProps {
  run: ScreenerRun | null | undefined;
  stocks: Stock[];
  sectorStats: SectorStats[];
}

export function SummaryCards({ run, stocks, sectorStats }: SummaryCardsProps) {
  const avgScore =
    stocks.length > 0
      ? stocks.reduce((acc, s) => acc + (s.score || 0), 0) / stocks.length
      : 0;

  const topSector = sectorStats.length > 0 ? sectorStats[0].sector : "-";

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <div className="rounded-lg border bg-card p-4">
        <div className="text-sm font-medium text-muted-foreground">
          Total Stocks
        </div>
        <div className="mt-1 text-2xl font-bold">{run?.total_matches || 0}</div>
        <div className="mt-1 text-xs text-muted-foreground">
          {run?.total_scanned || 0} scanned
        </div>
      </div>

      <div className="rounded-lg border bg-card p-4">
        <div className="text-sm font-medium text-muted-foreground">
          Average Score
        </div>
        <div className="mt-1 text-2xl font-bold">{avgScore.toFixed(1)}</div>
        <div className="mt-1 text-xs text-muted-foreground">out of 10</div>
      </div>

      <div className="rounded-lg border bg-card p-4">
        <div className="text-sm font-medium text-muted-foreground">
          Top Sector
        </div>
        <div className="mt-1 text-2xl font-bold truncate">{topSector}</div>
        <div className="mt-1 text-xs text-muted-foreground">
          {sectorStats[0]?.count || 0} stocks
        </div>
      </div>

      <div className="rounded-lg border bg-card p-4">
        <div className="text-sm font-medium text-muted-foreground">
          Last Updated
        </div>
        <div className="mt-1 text-2xl font-bold">
          {run ? getRelativeTime(run.created_at) : "-"}
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          {run?.execution_time_seconds
            ? `${run.execution_time_seconds.toFixed(0)}s execution`
            : ""}
        </div>
      </div>
    </div>
  );
}
