"use client";

import { useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import { ChevronLeft, ChevronRight, Search, Users } from "lucide-react";

interface OrgStructureProps {
  spanOfControl: {
    name: string;
    value: number;
    employeeNumber?: string;
    departmentName?: string;
  }[];
  locationHeatmap: { name: string; value: number }[];
}

const SPAN_RANGE_OPTIONS = [
  { value: "all", label: "Top 10" },
  { value: "0-5", label: "0-5" },
  { value: "6-10", label: "6-10" },
  { value: "11-20", label: "11-20" },
  { value: "21-50", label: "21-50" },
  { value: "51-100", label: "51-100" },
  { value: "101+", label: "101+" },
] as const;

function matchesSpanRange(value: number, filter: string) {
  if (filter === "all") return true;
  if (filter === "0-5") return value >= 0 && value <= 5;
  if (filter === "6-10") return value >= 6 && value <= 10;
  if (filter === "11-20") return value >= 11 && value <= 20;
  if (filter === "21-50") return value >= 21 && value <= 50;
  if (filter === "51-100") return value >= 51 && value <= 100;
  if (filter === "101+") return value >= 101;
  return true;
}
function formatEmployeeNumber(value?: string) {
  const raw = String(value ?? '').trim();
  if (!raw) return '-';
  return raw.replace(/\.0+$/, '');
}

function cleanDepartmentName(value?: string) {
  const raw = String(value ?? '').trim();
  if (!raw) return 'Unknown';
  const cleaned = raw.replace(/^\d+\./, '').trim();
  return cleaned || 'Unknown';
}

export function OrgStructure({
  spanOfControl,
  locationHeatmap,
}: OrgStructureProps) {
  const [page, setPage] = useState(0);
  const [managerSearch, setManagerSearch] = useState("");
  const [teamSizeFilter, setTeamSizeFilter] = useState("all");
  const ITEMS_PER_PAGE = 10;

  const normalizedManagerSearch = managerSearch.trim().toLowerCase();
  const isSpanFilterApplied = normalizedManagerSearch.length > 0 || teamSizeFilter !== "all";

  const filteredSpanData = useMemo(() => {
    return spanOfControl.filter((item) => {
      const matchesManager =
        normalizedManagerSearch.length === 0 || item.name.toLowerCase().includes(normalizedManagerSearch);

      const matchesTeamSize = matchesSpanRange(item.value, teamSizeFilter);

      return matchesManager && matchesTeamSize;
    });
  }, [normalizedManagerSearch, spanOfControl, teamSizeFilter]);

  const defaultTopTenSpanData = useMemo(() => {
    return [...spanOfControl].sort((a, b) => b.value - a.value).slice(0, 10);
  }, [spanOfControl]);

  const selectedSpanRangeLabel = useMemo(() => {
    return SPAN_RANGE_OPTIONS.find((option) => option.value === teamSizeFilter)?.label ?? "Top 10";
  }, [teamSizeFilter]);

  const totalPages = Math.ceil(locationHeatmap.length / ITEMS_PER_PAGE);
  const currentData = locationHeatmap.slice(
    page * ITEMS_PER_PAGE,
    (page + 1) * ITEMS_PER_PAGE
  );

  const spanOption = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "value",
      boundaryGap: [0, 0.01],
    },
    yAxis: {
      type: "category",
      data: defaultTopTenSpanData.map((item) => item.name),
      axisLabel: {
        width: 100,
        overflow: "truncate",
      },
    },
    series: [
      {
        name: "Direct Reports",
        type: "bar",
        data: defaultTopTenSpanData.map((item) => item.value),
        itemStyle: {
          color: "#3b82f6",
          borderRadius: [0, 4, 4, 0],
        },
      },
    ],
  };

  const locationOption = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "value",
    },
    yAxis: {
      type: "category",
      data: currentData.map((item) => item.name),
      axisLabel: {
        width: 100,
        overflow: "truncate",
      },
    },
    series: [
      {
        name: "Headcount",
        type: "bar",
        data: currentData.map((item) => item.value),
        itemStyle: {
          color: "#10b981",
          borderRadius: [0, 4, 4, 0],
        },
        label: {
          show: true,
          position: "right",
        },
      },
    ],
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Span of Control */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Span of Control (Top 10 Managers)
        </h3>

        <div className="mb-4 space-y-2">
          <label className="text-xs text-gray-600 block">
            Search manager
            <div className="mt-1 flex items-center gap-2 rounded-md border border-gray-200 px-2 py-1.5">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                value={managerSearch}
                onChange={(e) => setManagerSearch(e.target.value)}
                placeholder="Manager name"
                className="w-full bg-transparent outline-none text-sm"
              />
              <div className="relative">
                <Users className="w-4 h-4 text-blue-500 absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none" />
                <select
                  value={teamSizeFilter}
                  onChange={(e) => setTeamSizeFilter(e.target.value)}
                  className="appearance-none bg-blue-50 border border-blue-200 text-blue-700 rounded-full pl-7 pr-6 py-1 text-sm font-medium"
                >
                  {SPAN_RANGE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </label>
        </div>

        {!isSpanFilterApplied ? (
          <ReactECharts option={spanOption} style={{ height: "350px" }} />
        ) : (
          <div className="border border-gray-100 rounded-lg overflow-hidden">
            <div className="px-4 py-2 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500">
                {teamSizeFilter === "all" ? "Matching Managers" : `Range ${selectedSpanRangeLabel}`}
              </span>
              <span className="text-xs font-semibold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                Managers: {filteredSpanData.length}
              </span>
            </div>
            <div className="grid grid-cols-[1.3fr_.8fr_1fr_auto] gap-4 px-4 py-2 text-xs font-semibold text-gray-500 bg-gray-50 border-b border-gray-100">
              <span>MANAGER</span>
              <span>EMP NO</span>
              <span>DEPARTMENT</span>
              <span>DIRECT REPORTS</span>
            </div>
            <div className="max-h-[350px] overflow-y-auto divide-y divide-gray-100">
              {filteredSpanData.length > 0 ? (
                filteredSpanData.map((item) => {
                  const employeeNumber = formatEmployeeNumber(item.employeeNumber);
                  const departmentName = cleanDepartmentName(item.departmentName);

                  return (
                    <div key={`${item.name}-${item.employeeNumber ?? ""}`} className="grid grid-cols-[1.3fr_.8fr_1fr_auto] gap-4 px-4 py-3 text-sm">
                      <div className="relative group">
                        <span className="text-gray-800 truncate cursor-help">{item.name}</span>
                        <div className="absolute left-0 top-full mt-2 w-72 rounded-lg border border-gray-200 bg-white p-3 shadow-lg z-20 hidden group-hover:block">
                          <p className="text-xs text-gray-500 mb-1">Manager Details</p>
                          <p className="text-sm text-gray-800"><span className="font-medium">Employee No:</span> {employeeNumber}</p>
                          <p className="text-sm text-gray-800 mt-1"><span className="font-medium">Department:</span> {departmentName}</p>
                        </div>
                      </div>
                      <span className="text-gray-600 truncate">{employeeNumber}</span>
                      <span className="text-gray-600 truncate">{departmentName}</span>
                      <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                        {item.value}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="px-4 py-6 text-sm text-gray-500">No managers match this search/filter.</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Cluster Headcount */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Headcount by Cluster
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-5 w-5 text-gray-500" />
            </button>
            <span className="text-sm text-gray-500">
              {page + 1} / {Math.max(1, totalPages)}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="h-5 w-5 text-gray-500" />
            </button>
          </div>
        </div>
        <ReactECharts option={locationOption} style={{ height: "350px" }} />
      </div>
    </div>
  );
}





