"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import type { Stock } from "@/types/stock";
import {
  formatNumber,
  formatPercent,
  formatRatio,
  formatCurrency,
  getScoreColor,
  cn,
} from "@/lib/utils";

interface StockTableProps {
  stocks: Stock[];
  isLoading?: boolean;
}

type SortKey =
  | "symbol"
  | "name"
  | "score"
  | "price"
  | "market_cap"
  | "pe_ratio"
  | "peg_ratio"
  | "roe"
  | "debt_to_equity"
  | "sector";

export function StockTable({ stocks, isLoading }: StockTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sortedStocks = useMemo(() => {
    return [...stocks].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      // Handle nulls
      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return sortDir === "asc" ? -1 : 1;
      if (bVal === null) return sortDir === "asc" ? 1 : -1;

      // Compare
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      const numA = Number(aVal);
      const numB = Number(bVal);
      return sortDir === "asc" ? numA - numB : numB - numA;
    });
  }, [stocks, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const SortHeader = ({
    label,
    sortKeyValue,
    className,
  }: {
    label: string;
    sortKeyValue: SortKey;
    className?: string;
  }) => (
    <th
      className={cn(
        "cursor-pointer select-none px-4 py-3 text-left text-sm font-medium hover:bg-muted/50",
        className
      )}
      onClick={() => handleSort(sortKeyValue)}
    >
      <div className="flex items-center gap-1">
        {label}
        {sortKey === sortKeyValue && (
          <span className="text-xs">{sortDir === "asc" ? "^" : "v"}</span>
        )}
      </div>
    </th>
  );

  if (isLoading) {
    return (
      <div className="rounded-lg border">
        <div className="p-8 text-center text-muted-foreground">
          Loading stocks...
        </div>
      </div>
    );
  }

  if (stocks.length === 0) {
    return (
      <div className="rounded-lg border">
        <div className="p-8 text-center text-muted-foreground">
          No stocks found matching your criteria.
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border overflow-x-auto">
      <table className="w-full">
        <thead className="border-b bg-muted/50">
          <tr>
            <SortHeader label="Symbol" sortKeyValue="symbol" />
            <SortHeader label="Name" sortKeyValue="name" className="min-w-48" />
            <SortHeader label="Score" sortKeyValue="score" />
            <SortHeader label="Price" sortKeyValue="price" />
            <SortHeader label="Mkt Cap" sortKeyValue="market_cap" />
            <SortHeader label="P/E" sortKeyValue="pe_ratio" />
            <SortHeader label="PEG" sortKeyValue="peg_ratio" />
            <SortHeader label="ROE" sortKeyValue="roe" />
            <SortHeader label="D/E" sortKeyValue="debt_to_equity" />
            <SortHeader label="Sector" sortKeyValue="sector" />
          </tr>
        </thead>
        <tbody className="divide-y">
          {sortedStocks.map((stock) => (
            <tr key={stock.id} className="hover:bg-muted/30">
              <td className="px-4 py-3">
                <Link
                  href={`/stock/${stock.symbol}`}
                  className="font-medium text-primary hover:underline"
                >
                  {stock.symbol}
                </Link>
              </td>
              <td className="px-4 py-3 text-sm truncate max-w-48">
                {stock.name}
              </td>
              <td className="px-4 py-3">
                <span className={cn("font-semibold", getScoreColor(stock.score))}>
                  {stock.score?.toFixed(1) || "-"}
                </span>
              </td>
              <td className="px-4 py-3 text-sm">
                {formatCurrency(stock.price)}
              </td>
              <td className="px-4 py-3 text-sm">
                {formatNumber(stock.market_cap)}
              </td>
              <td className="px-4 py-3 text-sm">
                {formatRatio(stock.pe_ratio, 1)}
              </td>
              <td className="px-4 py-3 text-sm">
                {formatRatio(stock.peg_ratio)}
              </td>
              <td className="px-4 py-3 text-sm">
                {formatPercent(stock.roe)}
              </td>
              <td className="px-4 py-3 text-sm">
                {formatRatio(stock.debt_to_equity)}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground truncate max-w-32">
                {stock.sector || "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
