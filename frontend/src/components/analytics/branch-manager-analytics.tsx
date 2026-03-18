"use client";

import ReactECharts from "echarts-for-react";
import { Building2, Users, AlertTriangle, CheckCircle2 } from "lucide-react";

interface BranchManagerAnalyticsProps {
  data: {
    totalBranches: number;
    branchesWithBM: number;
    branchesWithBOM: number;
    branchesWithoutBM: number;
    branchesWithoutBOM: number;
    branchesWithoutBoth: number;
    branchesWithoutBMList: string[];
    branchesWithoutBOMList: string[];
    branchesWithoutBothList: string[];
    bmByCluster: Array<{ cluster: string; bm_count: number }>;
    bmByRegion: Array<{ region: string; bm_count: number }>;
  };
}

export function BranchManagerAnalytics({ data }: BranchManagerAnalyticsProps) {
  const bmByClusterChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Branch Managers by Cluster", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: {
      type: "category",
      data: data.bmByCluster?.slice(0, 15).map((d) => d.cluster) || [],
      axisLabel: { interval: 0, width: 150, overflow: "truncate" },
    },
    series: [
      {
        type: "bar",
        data: data.bmByCluster?.slice(0, 15).map((d) => d.bm_count) || [],
        itemStyle: { color: "#3b82f6", borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: "right" },
      },
    ],
  };

  const bmByRegionChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Branch Managers by Region", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: {
      type: "category",
      data: data.bmByRegion?.slice(0, 15).map((d) => d.region) || [],
      axisLabel: { interval: 0, width: 150, overflow: "truncate" },
    },
    series: [
      {
        type: "bar",
        data: data.bmByRegion?.slice(0, 15).map((d) => d.bm_count) || [],
        itemStyle: { color: "#10b981", borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: "right" },
      },
    ],
  };

  const coverageChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Branch Coverage Status", left: "center" },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: "#fff", borderWidth: 2 },
        label: { show: true, formatter: "{b}\n{c} branches" },
        data: [
          {
            value: data.branchesWithBM || 0,
            name: "With BM",
            itemStyle: { color: "#10b981" },
          },
          {
            value: data.branchesWithoutBM || 0,
            name: "Without BM",
            itemStyle: { color: "#ef4444" },
          },
        ],
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 p-6 rounded-xl border">
        <h2 className="text-2xl font-bold mb-2">Branch Manager Coverage Analysis</h2>
        <p className="text-muted-foreground">
          Comprehensive analysis of branch management coverage across the organization
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-cyan-600 p-6 rounded-xl text-white">
          <Building2 className="h-8 w-8 mb-2 opacity-80" />
          <p className="text-sm opacity-90">Total Branches</p>
          <p className="text-4xl font-bold mt-2">{data.totalBranches}</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-xl text-white">
          <CheckCircle2 className="h-8 w-8 mb-2 opacity-80" />
          <p className="text-sm opacity-90">Branches with BM</p>
          <p className="text-4xl font-bold mt-2">{data.branchesWithBM}</p>
          <p className="text-xs opacity-75 mt-1">
            {((data.branchesWithBM / data.totalBranches) * 100).toFixed(1)}% coverage
          </p>
        </div>

        <div className="bg-gradient-to-br from-amber-500 to-orange-600 p-6 rounded-xl text-white">
          <CheckCircle2 className="h-8 w-8 mb-2 opacity-80" />
          <p className="text-sm opacity-90">Branches with BOM</p>
          <p className="text-4xl font-bold mt-2">{data.branchesWithBOM}</p>
          <p className="text-xs opacity-75 mt-1">
            {((data.branchesWithBOM / data.totalBranches) * 100).toFixed(1)}% coverage
          </p>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-rose-600 p-6 rounded-xl text-white">
          <AlertTriangle className="h-8 w-8 mb-2 opacity-80" />
          <p className="text-sm opacity-90">Without Both</p>
          <p className="text-4xl font-bold mt-2">{data.branchesWithoutBoth}</p>
          <p className="text-xs opacity-75 mt-1">
            {((data.branchesWithoutBoth / data.totalBranches) * 100).toFixed(1)}% critical
          </p>
        </div>
      </div>

      {/* Alert Cards for Missing Managers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-red-50 dark:bg-red-950/30 p-4 rounded-lg border-2 border-red-200 dark:border-red-800">
          <h3 className="font-semibold text-red-900 dark:text-red-100 mb-2 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Branches Without BM ({data.branchesWithoutBM})
          </h3>
          <div className="max-h-40 overflow-y-auto text-sm text-red-800 dark:text-red-200">
            {data.branchesWithoutBMList?.slice(0, 20).map((branch, idx) => (
              <div key={idx} className="py-1">• {branch}</div>
            ))}
            {data.branchesWithoutBM > 20 && (
              <div className="text-xs italic mt-2">
                ... and {data.branchesWithoutBM - 20} more
              </div>
            )}
          </div>
        </div>

        <div className="bg-orange-50 dark:bg-orange-950/30 p-4 rounded-lg border-2 border-orange-200 dark:border-orange-800">
          <h3 className="font-semibold text-orange-900 dark:text-orange-100 mb-2 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Branches Without BOM ({data.branchesWithoutBOM})
          </h3>
          <div className="max-h-40 overflow-y-auto text-sm text-orange-800 dark:text-orange-200">
            {data.branchesWithoutBOMList?.slice(0, 20).map((branch, idx) => (
              <div key={idx} className="py-1">• {branch}</div>
            ))}
            {data.branchesWithoutBOM > 20 && (
              <div className="text-xs italic mt-2">
                ... and {data.branchesWithoutBOM - 20} more
              </div>
            )}
          </div>
        </div>

        <div className="bg-rose-50 dark:bg-rose-950/30 p-4 rounded-lg border-2 border-rose-200 dark:border-rose-800">
          <h3 className="font-semibold text-rose-900 dark:text-rose-100 mb-2 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Without Both BM & BOM ({data.branchesWithoutBoth})
          </h3>
          <div className="max-h-40 overflow-y-auto text-sm text-rose-800 dark:text-rose-200">
            {data.branchesWithoutBothList?.slice(0, 20).map((branch, idx) => (
              <div key={idx} className="py-1">• {branch}</div>
            ))}
            {data.branchesWithoutBoth > 20 && (
              <div className="text-xs italic mt-2">
                ... and {data.branchesWithoutBoth - 20} more
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm">
          <ReactECharts option={coverageChart} style={{ height: "350px" }} />
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm lg:col-span-2">
          <ReactECharts option={bmByClusterChart} style={{ height: "350px" }} />
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm lg:col-span-3">
          <ReactECharts option={bmByRegionChart} style={{ height: "400px" }} />
        </div>
      </div>
    </div>
  );
}
