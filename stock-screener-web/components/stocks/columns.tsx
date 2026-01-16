"use client"

import { ColumnDef } from "@tanstack/react-table"
import Link from "next/link"
import { ArrowUpDown, MoreHorizontal } from "lucide-react"

import type { Stock } from "@/types/stock"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  formatNumber,
  formatPercent,
  formatRatio,
  formatCurrency,
  formatPerformance,
  cn,
} from "@/lib/utils"

function getScoreBadgeVariant(score: number | null): "default" | "secondary" | "destructive" | "outline" {
  if (score === null) return "outline"
  if (score >= 8) return "default"
  if (score >= 6) return "secondary"
  return "destructive"
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-muted-foreground">-</span>

  const variant = getScoreBadgeVariant(score)
  return (
    <Badge
      variant={variant}
      className={cn(
        score >= 8 && "bg-green-500 hover:bg-green-600",
        score >= 6 && score < 8 && "bg-emerald-500 hover:bg-emerald-600",
        score >= 4 && score < 6 && "bg-yellow-500 hover:bg-yellow-600 text-black",
        score < 4 && "bg-red-500 hover:bg-red-600"
      )}
    >
      {score.toFixed(1)}
    </Badge>
  )
}

function PerformanceCell({ value }: { value: number | null }) {
  const { text, colorClass } = formatPerformance(value)
  return <span className={cn("font-medium", colorClass)}>{text}</span>
}

interface CreateColumnsProps {
  onViewTradeIdea?: (stock: Stock) => void
}

export function createColumns({ onViewTradeIdea }: CreateColumnsProps = {}): ColumnDef<Stock>[] {
  return [
    {
      accessorKey: "symbol",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Symbol
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const symbol = row.getValue("symbol") as string
        return (
          <Link
            href={`/stock/${symbol}`}
            className="font-medium text-primary hover:underline"
          >
            {symbol}
          </Link>
        )
      },
    },
    {
      accessorKey: "name",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Name
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return (
          <div className="max-w-[200px] truncate">
            {row.getValue("name")}
          </div>
        )
      },
    },
    {
      accessorKey: "score",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            GARP
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const score = row.getValue("score") as number | null
        return <ScoreBadge score={score} />
      },
    },
    {
      accessorKey: "ai_score",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            AI
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const score = row.getValue("ai_score") as number | null
        return <ScoreBadge score={score} />
      },
    },
    {
      accessorKey: "perf_1d",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            1D
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return <PerformanceCell value={row.getValue("perf_1d")} />
      },
    },
    {
      accessorKey: "perf_1w",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            1W
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return <PerformanceCell value={row.getValue("perf_1w")} />
      },
    },
    {
      accessorKey: "perf_1m",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            1M
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return <PerformanceCell value={row.getValue("perf_1m")} />
      },
    },
    {
      accessorKey: "perf_ytd",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            YTD
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return <PerformanceCell value={row.getValue("perf_ytd")} />
      },
    },
    {
      accessorKey: "price",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Price
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return formatCurrency(row.getValue("price"))
      },
    },
    {
      accessorKey: "market_cap",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Mkt Cap
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return formatNumber(row.getValue("market_cap"))
      },
    },
    {
      accessorKey: "pe_ratio",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            P/E
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return formatRatio(row.getValue("pe_ratio"), 1)
      },
    },
    {
      accessorKey: "peg_ratio",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            PEG
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return formatRatio(row.getValue("peg_ratio"))
      },
    },
    {
      accessorKey: "next_earnings_date",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Earnings
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const date = row.getValue("next_earnings_date") as string | null
        if (!date) return <span className="text-muted-foreground">-</span>
        // Show just the date part (YYYY-MM-DD)
        return <span className="text-sm">{date.split("T")[0]}</span>
      },
    },
    {
      accessorKey: "sector",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Sector
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const sector = row.getValue("sector") as string | null
        return (
          <div className="max-w-[120px] truncate text-muted-foreground">
            {sector || "-"}
          </div>
        )
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const stock = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem
                onClick={() => navigator.clipboard.writeText(stock.symbol)}
              >
                Copy symbol
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href={`/stock/${stock.symbol}`}>
                  View details
                </Link>
              </DropdownMenuItem>
              {onViewTradeIdea && stock.trade_idea && (
                <DropdownMenuItem onClick={() => onViewTradeIdea(stock)}>
                  View trade idea
                </DropdownMenuItem>
              )}
              <DropdownMenuItem asChild>
                <a
                  href={`https://finance.yahoo.com/quote/${stock.symbol}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open in Yahoo Finance
                </a>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]
}
