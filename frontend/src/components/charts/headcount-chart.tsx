"use client";

import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function HeadcountChart() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "headcount"],
    queryFn: () => analyticsApi.getHeadcount(),
  });

  // Mock data for demo
  const mockData = {
    departments: [
      { name: "Operations", count: 25000 },
      { name: "Technology", count: 15000 },
      { name: "Retail Banking", count: 18000 },
      { name: "Corporate Banking", count: 12000 },
      { name: "Risk Management", count: 8000 },
      { name: "Compliance", count: 5000 },
      { name: "Human Resources", count: 4000 },
      { name: "Finance", count: 6000 },
      { name: "Treasury", count: 3500 },
      { name: "Digital Banking", count: 3500 },
    ],
  };

  const chartData = data?.by_department || mockData.departments;

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
      type: "value",
      axisLabel: {
        formatter: (value: number) =>
          value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value,
      },
    },
    yAxis: {
      type: "category",
      data: chartData.map((d: any) => d.name || d.department),
      axisLabel: {
        width: 100,
        overflow: "truncate",
      },
    },
    series: [
      {
        name: "Employees",
        type: "bar",
        data: chartData.map((d: any) => d.count || d.total),
        itemStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: "#3b82f6" },
              { offset: 1, color: "#06b6d4" },
            ],
          },
          borderRadius: [0, 4, 4, 0],
        },
        label: {
          show: true,
          position: "right",
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
