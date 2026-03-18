"use client";

import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function PerformanceChart() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "performance"],
    queryFn: () => analyticsApi.getPerformance(),
  });

  // Mock data for demo
  const mockData = {
    distribution: [
      { range: "1.0-1.5", count: 2500 },
      { range: "1.5-2.0", count: 5000 },
      { range: "2.0-2.5", count: 12000 },
      { range: "2.5-3.0", count: 18000 },
      { range: "3.0-3.5", count: 25000 },
      { range: "3.5-4.0", count: 22000 },
      { range: "4.0-4.5", count: 12000 },
      { range: "4.5-5.0", count: 3500 },
    ],
  };

  const chartData = data?.distribution || mockData.distribution;

  const option = {
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
      type: "category",
      data: chartData.map((d: any) => d.range || d.score_range),
      axisLabel: {
        rotate: 0,
      },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        formatter: (value: number) =>
          value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value,
      },
    },
    series: [
      {
        name: "Employees",
        type: "bar",
        data: chartData.map((d: any) => ({
          value: d.count,
          itemStyle: {
            color: getColorForScore(d.range || d.score_range),
          },
        })),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
        },
        label: {
          show: true,
          position: "top",
          formatter: (params: any) =>
            params.value >= 1000
              ? `${(params.value / 1000).toFixed(1)}k`
              : params.value,
        },
      },
    ],
  };

  if (isLoading) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading chart...</div>
      </div>
    );
  }

  return <ReactECharts option={option} style={{ height: "350px" }} />;
}

function getColorForScore(range: string): string {
  const score = parseFloat(range.split("-")[0]);
  if (score >= 4.0) return "#22c55e";
  if (score >= 3.5) return "#84cc16";
  if (score >= 3.0) return "#eab308";
  if (score >= 2.5) return "#f59e0b";
  if (score >= 2.0) return "#f97316";
  return "#ef4444";
}
