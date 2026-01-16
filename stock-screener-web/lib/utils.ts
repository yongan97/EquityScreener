import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";

  if (Math.abs(value) >= 1e12) {
    return `${(value / 1e12).toFixed(2)}T`;
  } else if (Math.abs(value) >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`;
  } else if (Math.abs(value) >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`;
  } else if (Math.abs(value) >= 1e3) {
    return `${(value / 1e3).toFixed(1)}K`;
  }
  return value.toFixed(0);
}

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return `$${value.toFixed(2)}`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  // Assume value is already a decimal (e.g., 0.15 for 15%)
  return `${(value * 100).toFixed(1)}%`;
}

export function formatRatio(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return "-";
  return value.toFixed(decimals);
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) return "-";

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return "yesterday";
  if (diffDays < 7) return `${diffDays}d ago`;

  return formatDate(dateString);
}

export function getScoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return "";
  if (score >= 7) return "text-green-600 dark:text-green-400";
  if (score >= 5) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

export function formatPerformance(value: number | null | undefined): { text: string; colorClass: string } {
  if (value === null || value === undefined) {
    return { text: "-", colorClass: "text-muted-foreground" };
  }

  const percent = value * 100;
  const sign = value >= 0 ? "+" : "";
  const text = `${sign}${percent.toFixed(1)}%`;
  const colorClass = value >= 0
    ? "text-green-600 dark:text-green-400"
    : "text-red-600 dark:text-red-400";

  return { text, colorClass };
}
