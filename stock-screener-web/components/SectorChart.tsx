"use client";

import type { SectorStats } from "@/types/stock";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface SectorChartProps {
  sectorStats: SectorStats[];
}

const COLORS = [
  "#3b82f6", // blue
  "#10b981", // emerald
  "#f59e0b", // amber
  "#ef4444", // red
  "#8b5cf6", // violet
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#f97316", // orange
  "#84cc16", // lime
  "#6366f1", // indigo
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
      <div className="rounded-lg border bg-card p-4">
        <h3 className="font-semibold mb-4">Distribution by Sector</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="font-semibold mb-4">Distribution by Sector</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="sector"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ sector, percent }) =>
                `${sector} (${(percent * 100).toFixed(0)}%)`
              }
              labelLine={false}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string) => [
                `${value} stocks`,
                name,
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
