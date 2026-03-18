"use client";

import { useFilterStore } from "@/lib/store";
import { X, Plus, ChevronDown, ChevronUp, RotateCcw } from "lucide-react";
import { useState } from "react";

export function FilterPanel() {
  const {
    filterBlocks,
    filterOptions,
    addFilterBlock,
    removeFilterBlock,
    updateFilterBlock,
    clearAllFilters,
  } = useFilterStore();

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        <button
          onClick={clearAllFilters}
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
        >
          <RotateCcw className="h-3 w-3" />
          Reset all
        </button>
      </div>

      {/* Filter blocks */}
      {filterBlocks.map((block, index) => (
        <FilterBlock
          key={block.id}
          block={block}
          index={index}
          options={filterOptions}
          onUpdate={(updates) => updateFilterBlock(block.id, updates)}
          onRemove={() => removeFilterBlock(block.id)}
          canRemove={filterBlocks.length > 1}
        />
      ))}

      {/* Add filter block button */}
      <button
        onClick={addFilterBlock}
        className="w-full flex items-center justify-center gap-2 py-2 border-2 border-dashed rounded-lg text-muted-foreground hover:text-foreground hover:border-primary transition-colors"
      >
        <Plus className="h-4 w-4" />
        Add filter block
      </button>
    </div>
  );
}

interface FilterBlockProps {
  block: any;
  index: number;
  options: any;
  onUpdate: (updates: any) => void;
  onRemove: () => void;
  canRemove: boolean;
}

function FilterBlock({
  block,
  index,
  options,
  onUpdate,
  onRemove,
  canRemove,
}: FilterBlockProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Block header */}
      <div
        className="flex items-center justify-between px-3 py-2 bg-muted cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="text-sm font-medium">Filter Block {index + 1}</span>
        <div className="flex items-center gap-1">
          {canRemove && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
              className="p-1 hover:bg-background rounded transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          {expanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </div>
      </div>

      {/* Block content */}
      {expanded && (
        <div className="p-3 space-y-4">
          {/* Search */}
          <div>
            <label className="text-xs font-medium text-muted-foreground">Search</label>
            <input
              type="text"
              value={block.searchTerm}
              onChange={(e) => onUpdate({ searchTerm: e.target.value })}
              placeholder="Name, ID, or email..."
              className="w-full mt-1 px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Departments */}
          <MultiSelect
            label="Departments"
            options={options.departments}
            selected={block.departments}
            onChange={(departments) => onUpdate({ departments })}
          />

          {/* Grades */}
          <MultiSelect
            label="Grade Levels"
            options={options.grades}
            selected={block.grades}
            onChange={(grades) => onUpdate({ grades })}
          />

          {/* Countries */}
          <MultiSelect
            label="Countries"
            options={options.countries}
            selected={block.countries}
            onChange={(countries) => onUpdate({ countries })}
          />

          {/* Statuses */}
          <MultiSelect
            label="Status"
            options={options.statuses}
            selected={block.statuses}
            onChange={(statuses) => onUpdate({ statuses })}
          />

          {/* Salary range */}
          <div>
            <label className="text-xs font-medium text-muted-foreground">Salary Range (PKR)</label>
            <div className="flex items-center gap-2 mt-1">
              <input
                type="number"
                value={block.salaryMin || ""}
                onChange={(e) => onUpdate({ salaryMin: e.target.value ? Number(e.target.value) : null })}
                placeholder="Min"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <span className="text-muted-foreground">-</span>
              <input
                type="number"
                value={block.salaryMax || ""}
                onChange={(e) => onUpdate({ salaryMax: e.target.value ? Number(e.target.value) : null })}
                placeholder="Max"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Experience range */}
          <div>
            <label className="text-xs font-medium text-muted-foreground">Experience (years)</label>
            <div className="flex items-center gap-2 mt-1">
              <input
                type="number"
                value={block.experienceMin || ""}
                onChange={(e) => onUpdate({ experienceMin: e.target.value ? Number(e.target.value) : null })}
                placeholder="Min"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <span className="text-muted-foreground">-</span>
              <input
                type="number"
                value={block.experienceMax || ""}
                onChange={(e) => onUpdate({ experienceMax: e.target.value ? Number(e.target.value) : null })}
                placeholder="Max"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Performance range */}
          <div>
            <label className="text-xs font-medium text-muted-foreground">Performance Score</label>
            <div className="flex items-center gap-2 mt-1">
              <input
                type="number"
                step="0.1"
                min="1"
                max="5"
                value={block.performanceMin || ""}
                onChange={(e) => onUpdate({ performanceMin: e.target.value ? Number(e.target.value) : null })}
                placeholder="Min"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <span className="text-muted-foreground">-</span>
              <input
                type="number"
                step="0.1"
                min="1"
                max="5"
                value={block.performanceMax || ""}
                onChange={(e) => onUpdate({ performanceMax: e.target.value ? Number(e.target.value) : null })}
                placeholder="Max"
                className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface MultiSelectProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  return (
    <div>
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <div className="relative mt-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-3 py-2 text-sm border rounded-md hover:bg-muted transition-colors text-left"
        >
          <span className={selected.length === 0 ? "text-muted-foreground" : ""}>
            {selected.length === 0
              ? `Select ${label.toLowerCase()}...`
              : `${selected.length} selected`}
          </span>
          <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-card border rounded-md shadow-lg max-h-60 overflow-auto">
            {options.map((option) => (
              <label
                key={option}
                className="flex items-center gap-2 px-3 py-2 hover:bg-muted cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selected.includes(option)}
                  onChange={() => toggleOption(option)}
                  className="rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="text-sm">{option}</span>
              </label>
            ))}
            {options.length === 0 && (
              <p className="px-3 py-2 text-sm text-muted-foreground">No options available</p>
            )}
          </div>
        )}
      </div>

      {/* Selected tags */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {selected.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full"
            >
              {item}
              <button
                onClick={() => toggleOption(item)}
                className="hover:bg-primary/20 rounded-full"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
