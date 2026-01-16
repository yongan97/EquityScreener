"use client";

import type { ScreenerRun, Stock, SectorStats } from "@/types/stock";
import { getRelativeTime } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, BarChart3, Building2, Clock } from "lucide-react";

interface SummaryCardsProps {
  run: ScreenerRun | null | undefined;
  stocks: Stock[];
  sectorStats: SectorStats[];
  isLoading?: boolean;
}

export function SummaryCards({ run, stocks, sectorStats, isLoading }: SummaryCardsProps) {
  const avgScore =
    stocks.length > 0
      ? stocks.reduce((acc, s) => acc + (s.score || 0), 0) / stocks.length
      : 0;

  const topSector = sectorStats.length > 0 ? sectorStats[0].sector : "-";

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4 rounded" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-20 mb-1" />
              <Skeleton className="h-3 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{run?.total_matches || 0}</div>
          <p className="text-xs text-muted-foreground">
            {run?.total_scanned || 0} scanned
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Average Score</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{avgScore.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">out of 10</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Top Sector</CardTitle>
          <Building2 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold truncate">{topSector}</div>
          <p className="text-xs text-muted-foreground">
            {sectorStats[0]?.count || 0} stocks
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {run ? getRelativeTime(run.created_at) : "-"}
          </div>
          <p className="text-xs text-muted-foreground">
            {run?.execution_time_seconds
              ? `${run.execution_time_seconds.toFixed(0)}s execution`
              : ""}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
