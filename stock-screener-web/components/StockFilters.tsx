"use client";

import type { StockFilters } from "@/types/stock";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Search, X } from "lucide-react";

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

  const handleSectorToggle = (sector: string) => {
    const isSelected = filters.sectors.includes(sector);
    const newSectors = isSelected
      ? filters.sectors.filter((s) => s !== sector)
      : [...filters.sectors, sector];
    onFiltersChange({ ...filters, sectors: newSectors });
  };

  const handleScoreRangeChange = (values: number[]) => {
    onFiltersChange({ ...filters, scoreMin: values[0], scoreMax: values[1] });
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
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Filters</CardTitle>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={handleClearFilters}>
              <X className="mr-1 h-3 w-3" />
              Clear all
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Search</label>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Symbol or name..."
              value={filters.search}
              onChange={handleSearchChange}
              className="pl-8"
            />
          </div>
        </div>

        {/* Score Range */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Score Range</label>
            <span className="text-sm text-muted-foreground">
              {filters.scoreMin} - {filters.scoreMax}
            </span>
          </div>
          <Slider
            value={[filters.scoreMin, filters.scoreMax]}
            onValueChange={handleScoreRangeChange}
            min={0}
            max={10}
            step={0.5}
            className="py-2"
          />
        </div>

        {/* Sectors */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Sectors</label>
          <div className="flex flex-wrap gap-1.5">
            {sectors.map((sector) => {
              const isSelected = filters.sectors.includes(sector);
              return (
                <Badge
                  key={sector}
                  variant={isSelected ? "default" : "outline"}
                  className="cursor-pointer transition-colors hover:bg-primary/80"
                  onClick={() => handleSectorToggle(sector)}
                >
                  {sector}
                </Badge>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
