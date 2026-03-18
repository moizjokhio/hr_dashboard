"use client";

import { useState } from "react";
import ReactECharts from "echarts-for-react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface OrgStructureProps {
  spanOfControl: { name: string; value: number }[];
  locationHeatmap: { name: string; value: number }[];
}

export function OrgStructure({
  spanOfControl,
  locationHeatmap,
}: OrgStructureProps) {
  const [page, setPage] = useState(0);
  const ITEMS_PER_PAGE = 10;

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
      data: spanOfControl.map((item) => item.name),
      axisLabel: {
        width: 100,
        overflow: "truncate",
      },
    },
    series: [
      {
        name: "Direct Reports",
        type: "bar",
        data: spanOfControl.map((item) => item.value),
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
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Span of Control (Top 10 Managers)
        </h3>
        <ReactECharts option={spanOption} style={{ height: "350px" }} />
      </div>

      {/* Location Headcount */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Headcount by Location
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
