'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import type { FilterOptions, DAMISFilters } from '@/lib/da-mis-api';
import { useState } from 'react';

interface GlobalFiltersProps {
  options: FilterOptions;
  onFilterChange: (filters: DAMISFilters) => void;
  activeFilters: DAMISFilters;
}

export function GlobalFilters({ options, onFilterChange, activeFilters }: GlobalFiltersProps) {
  const [localFilters, setLocalFilters] = useState<DAMISFilters>(activeFilters);

  const handleFilterUpdate = (key: keyof DAMISFilters, value: any) => {
    const updated = { ...localFilters, [key]: value };
    setLocalFilters(updated);
    onFilterChange(updated);
  };

  const clearFilters = () => {
    setLocalFilters({});
    onFilterChange({});
  };

  const hasActiveFilters = Object.keys(localFilters).some(
    key => localFilters[key as keyof DAMISFilters] !== undefined && localFilters[key as keyof DAMISFilters] !== ''
  );

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Global Filters</CardTitle>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Year */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Year</label>
            <Select
              value={localFilters.year?.toString() || ''}
              onValueChange={(value) => handleFilterUpdate('year', value ? parseInt(value) : undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Years" />
              </SelectTrigger>
              <SelectContent>
                {options.years.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Quarter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Quarter</label>
            <Select
              value={localFilters.quarter || ''}
              onValueChange={(value) => handleFilterUpdate('quarter', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Quarters" />
              </SelectTrigger>
              <SelectContent>
                {options.quarters.map((quarter) => (
                  <SelectItem key={quarter} value={quarter}>
                    {quarter}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Cluster */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Cluster</label>
            <Select
              value={localFilters.cluster || ''}
              onValueChange={(value) => handleFilterUpdate('cluster', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Clusters" />
              </SelectTrigger>
              <SelectContent>
                {options.clusters.map((cluster) => (
                  <SelectItem key={cluster} value={cluster}>
                    {cluster}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Region */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Region</label>
            <Select
              value={localFilters.region || ''}
              onValueChange={(value) => handleFilterUpdate('region', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Regions" />
              </SelectTrigger>
              <SelectContent>
                {options.regions.map((region) => (
                  <SelectItem key={region} value={region}>
                    {region}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Grade */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Grade</label>
            <Select
              value={localFilters.grade || ''}
              onValueChange={(value) => handleFilterUpdate('grade', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Grades" />
              </SelectTrigger>
              <SelectContent>
                {options.grades.map((grade) => (
                  <SelectItem key={grade} value={grade}>
                    {grade}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Misconduct Category */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Misconduct Category</label>
            <Select
              value={localFilters.misconduct_category || ''}
              onValueChange={(value) => handleFilterUpdate('misconduct_category', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                {options.misconduct_categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* DAC Decision */}
          <div className="space-y-2">
            <label className="text-sm font-medium">DAC Decision</label>
            <Select
              value={localFilters.dac_decision || ''}
              onValueChange={(value) => handleFilterUpdate('dac_decision', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Decisions" />
              </SelectTrigger>
              <SelectContent>
                {options.dac_decisions.map((decision) => (
                  <SelectItem key={decision} value={decision}>
                    {decision}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
