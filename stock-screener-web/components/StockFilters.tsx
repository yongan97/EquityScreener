"use client";

import { useState } from "react";
import type { StockFilters } from "@/types/stock";

interface StockFiltersProps {
  sectors: string[];
  filters: StockFilters;
  onFiltersChange: (filters: StockFilters) => void;
}

export function StockFiltersComponent({
  sectors,
  filters,
  onFiltersChange,
}: StockFiltersProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, search: e.target.value });
  };

  const handleSectorChange = (sector: string, checked: boolean) => {
    const newSectors = checked
      ? [...filters.sectors, sector]
      : filters.sectors.filter((s) => s !== sector);
    onFiltersChange({ ...filters, sectors: newSectors });
  };

  const handleScoreMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, scoreMin: Number(e.target.value) });
  };

  const handleScoreMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, scoreMax: Number(e.target.value) });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      sectors: [],
      scoreMin: 0,
      scoreMax: 10,
      search: "",
    });
  };

  const hasActiveFilters =
    filters.search ||
    filters.sectors.length > 0 ||
    filters.scoreMin > 0 ||
    filters.scoreMax < 10;

  return (
    <div className="space-y-4 rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Search */}
      <div>
        <label className="text-sm font-medium">Search</label>
        <input
          type="text"
          placeholder="Symbol or name..."
          value={filters.search}
          onChange={handleSearchChange}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
        />
      </div>

      {/* Score Range */}
      <div>
        <label className="text-sm font-medium">Score Range</label>
        <div className="mt-1 flex items-center gap-2">
          <input
            type="number"
            min={0}
            max={10}
            step={0.5}
            value={filters.scoreMin}
            onChange={handleScoreMinChange}
            className="w-20 rounded-md border bg-background px-2 py-1 text-sm"
          />
          <span className="text-muted-foreground">to</span>
          <input
            type="number"
            min={0}
            max={10}
            step={0.5}
            value={filters.scoreMax}
            onChange={handleScoreMaxChange}
            className="w-20 rounded-md border bg-background px-2 py-1 text-sm"
          />
        </div>
      </div>

      {/* Sectors */}
      <div>
        <label className="text-sm font-medium">Sectors</label>
        <div className="mt-2 flex flex-wrap gap-2">
          {sectors.map((sector) => (
            <label
              key={sector}
              className={`cursor-pointer rounded-full border px-3 py-1 text-xs transition-colors ${
                filters.sectors.includes(sector)
                  ? "border-primary bg-primary text-primary-foreground"
                  : "hover:border-primary/50"
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={filters.sectors.includes(sector)}
                onChange={(e) => handleSectorChange(sector, e.target.checked)}
              />
              {sector}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
