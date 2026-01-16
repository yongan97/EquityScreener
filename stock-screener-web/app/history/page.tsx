"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { getRunHistory, getStocks } from "@/lib/queries";
import { formatDate, getRelativeTime, cn } from "@/lib/utils";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { History, Calendar, Clock, CheckCircle, AlertTriangle } from "lucide-react";

export default function HistoryPage() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const { data: runs = [], isLoading: runsLoading } = useQuery({
    queryKey: ["runHistory"],
    queryFn: () => getRunHistory(30),
  });

  const { data: stocks = [], isLoading: stocksLoading } = useQuery({
    queryKey: ["runStocks", selectedRunId],
    queryFn: () => (selectedRunId ? getStocks({ runId: selectedRunId, limit: 100 }) : Promise.resolve([])),
    enabled: !!selectedRunId,
  });

  if (runsLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-72 mt-2" />
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </CardContent>
          </Card>
          <Card className="lg:col-span-2">
            <CardContent className="p-8 text-center text-muted-foreground">
              <Skeleton className="h-40 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const selectedRun = runs.find((r) => r.id === selectedRunId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <History className="h-6 w-6" />
          Run History
        </h1>
        <p className="text-muted-foreground">
          View historical screener runs and compare results
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Runs List */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Previous Runs
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y max-h-[600px] overflow-y-auto">
              {runs.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">
                  No runs found
                </div>
              ) : (
                runs.map((run) => (
                  <button
                    key={run.id}
                    onClick={() => setSelectedRunId(run.id)}
                    className={cn(
                      "w-full p-4 text-left hover:bg-muted/50 transition-colors",
                      selectedRunId === run.id && "bg-muted"
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-medium">{run.config_name}</div>
                        <div className="text-sm text-muted-foreground">
                          {formatDate(run.created_at)}
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant="secondary">
                          {run.total_matches} stocks
                        </Badge>
                        <div className="text-xs text-muted-foreground mt-1">
                          {getRelativeTime(run.created_at)}
                        </div>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Run Details */}
        <div className="lg:col-span-2 space-y-4">
          {selectedRun ? (
            <>
              {/* Run Stats */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Run Details
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Config</div>
                      <div className="font-medium">{selectedRun.config_name}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Scanned</div>
                      <div className="font-medium">{selectedRun.total_scanned}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Matches</div>
                      <div className="font-medium">{selectedRun.total_matches}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" /> Execution
                      </div>
                      <div className="font-medium">
                        {selectedRun.execution_time_seconds?.toFixed(1)}s
                      </div>
                    </div>
                  </div>
                  {selectedRun.errors && selectedRun.errors.length > 0 && (
                    <div className="mt-4 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-destructive" />
                      <span className="text-sm text-destructive">
                        {selectedRun.errors.length} errors occurred
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Stocks from this run */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Stocks in this run</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  {stocksLoading ? (
                    <div className="p-4 space-y-3">
                      {[...Array(5)].map((_, i) => (
                        <Skeleton key={i} className="h-10 w-full" />
                      ))}
                    </div>
                  ) : stocks.length === 0 ? (
                    <div className="p-4 text-center text-muted-foreground">
                      No stocks in this run
                    </div>
                  ) : (
                    <div className="rounded-md border-0">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Symbol</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Score</TableHead>
                            <TableHead>Sector</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {stocks.map((stock) => (
                            <TableRow key={stock.id}>
                              <TableCell>
                                <Link
                                  href={`/stock/${stock.symbol}`}
                                  className="font-medium text-primary hover:underline"
                                >
                                  {stock.symbol}
                                </Link>
                              </TableCell>
                              <TableCell className="max-w-48 truncate">
                                {stock.name}
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant={
                                    stock.score && stock.score >= 7
                                      ? "default"
                                      : stock.score && stock.score >= 5
                                      ? "secondary"
                                      : "outline"
                                  }
                                  className={cn(
                                    stock.score && stock.score >= 7 && "bg-green-500 hover:bg-green-600"
                                  )}
                                >
                                  {stock.score?.toFixed(1) || "-"}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-muted-foreground">
                                {stock.sector || "-"}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select a run from the list to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
