"use client";

import { useQuery } from "@tanstack/react-query";
import { getRunHistory, getStocks } from "@/lib/queries";
import { formatDate, getRelativeTime } from "@/lib/utils";
import { useState } from "react";

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

  const isLoading = runsLoading;

  if (isLoading) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Loading history...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Run History</h1>
        <p className="text-muted-foreground">
          View historical screener runs and compare results
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Runs List */}
        <div className="lg:col-span-1">
          <div className="rounded-lg border bg-card">
            <div className="border-b p-4">
              <h2 className="font-semibold">Previous Runs</h2>
            </div>
            <div className="divide-y max-h-[600px] overflow-y-auto">
              {runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => setSelectedRunId(run.id)}
                  className={`w-full p-4 text-left hover:bg-muted/50 transition-colors ${
                    selectedRunId === run.id ? "bg-muted" : ""
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium">{run.config_name}</div>
                      <div className="text-sm text-muted-foreground">
                        {formatDate(run.created_at)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {run.total_matches} stocks
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {getRelativeTime(run.created_at)}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Run Details */}
        <div className="lg:col-span-2">
          {selectedRunId ? (
            <div className="space-y-4">
              {/* Run Stats */}
              {runs
                .filter((r) => r.id === selectedRunId)
                .map((run) => (
                  <div key={run.id} className="rounded-lg border bg-card p-4">
                    <h2 className="font-semibold mb-4">Run Details</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Config</div>
                        <div className="font-medium">{run.config_name}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Scanned</div>
                        <div className="font-medium">{run.total_scanned}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Matches</div>
                        <div className="font-medium">{run.total_matches}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Execution</div>
                        <div className="font-medium">
                          {run.execution_time_seconds?.toFixed(1)}s
                        </div>
                      </div>
                    </div>
                    {run.errors && run.errors.length > 0 && (
                      <div className="mt-4">
                        <div className="text-sm text-muted-foreground">Errors</div>
                        <div className="text-sm text-red-500">
                          {run.errors.length} errors occurred
                        </div>
                      </div>
                    )}
                  </div>
                ))}

              {/* Stocks from this run */}
              <div className="rounded-lg border bg-card">
                <div className="border-b p-4">
                  <h2 className="font-semibold">Stocks in this run</h2>
                </div>
                {stocksLoading ? (
                  <div className="p-4 text-center text-muted-foreground">
                    Loading stocks...
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="border-b bg-muted/50">
                        <tr>
                          <th className="px-4 py-2 text-left">Symbol</th>
                          <th className="px-4 py-2 text-left">Name</th>
                          <th className="px-4 py-2 text-left">Score</th>
                          <th className="px-4 py-2 text-left">Sector</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {stocks.map((stock) => (
                          <tr key={stock.id} className="hover:bg-muted/30">
                            <td className="px-4 py-2 font-medium">
                              {stock.symbol}
                            </td>
                            <td className="px-4 py-2 truncate max-w-48">
                              {stock.name}
                            </td>
                            <td className="px-4 py-2">
                              {stock.score?.toFixed(1) || "-"}
                            </td>
                            <td className="px-4 py-2 text-muted-foreground">
                              {stock.sector || "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="rounded-lg border bg-card p-8 text-center text-muted-foreground">
              Select a run from the list to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
