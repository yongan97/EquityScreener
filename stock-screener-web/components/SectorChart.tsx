"use client";

import type { SectorStats } from "@/types/stock";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart as PieChartIcon } from "lucide-react";

interface SectorChartProps {
  sectorStats: SectorStats[];
}

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "#8b5cf6",
  "#ec4899",
  "#06b6d4",
  "#f97316",
  "#84cc16",
];

export function SectorChart({ sectorStats }: SectorChartProps) {
  // Take top 8 sectors, group rest as "Other"
  const topSectors = sectorStats.slice(0, 8);
  const otherCount = sectorStats.slice(8).reduce((acc, s) => acc + s.count, 0);

  const data =
    otherCount > 0
      ? [...topSectors, { sector: "Other", count: otherCount, avgScore: 0 }]
      : topSectors;

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-base">Distribution by Sector</CardTitle>
          <PieChartIcon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="h-52 flex items-center justify-center text-muted-foreground">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base">Distribution by Sector</CardTitle>
        <PieChartIcon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="sector"
                cx="50%"
                cy="50%"
                outerRadius={70}
                label={({ sector, percent }) =>
                  percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : ""
                }
                labelLine={false}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    className="stroke-background"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="rounded-lg border bg-background p-2 shadow-md">
                        <p className="font-medium">{payload[0].name}</p>
                        <p className="text-sm text-muted-foreground">
                          {payload[0].value} stocks
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="mt-2 flex flex-wrap gap-2 text-xs">
          {data.slice(0, 5).map((entry, index) => (
            <div key={entry.sector} className="flex items-center gap-1">
              <div
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-muted-foreground truncate max-w-[80px]">
                {entry.sector}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
