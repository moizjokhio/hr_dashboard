"use client";

import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function CompensationChart() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "compensation"],
    queryFn: () => analyticsApi.getCompensation(),
  });

  // Mock data for demo
  const mockData = {
    grades: ["OG-4", "OG-3", "OG-2", "OG-1", "AVP", "VP", "SVP", "EVP"],
    avgSalary: [55000, 85000, 125000, 175000, 280000, 420000, 650000, 950000],
    minSalary: [45000, 70000, 100000, 145000, 230000, 350000, 520000, 780000],
    maxSalary: [65000, 100000, 150000, 210000, 340000, 500000, 780000, 1150000],
  };

  const chartData = data?.by_grade || mockData;

  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter: (params: any) => {
        const avg = params[0];
        const min = params[1];
        const max = params[2];
        return `
          <div style="padding: 8px;">
            <strong>${avg.name}</strong><br/>
            Average: PKR ${avg.value.toLocaleString()}<br/>
            Min: PKR ${min.value.toLocaleString()}<br/>
            Max: PKR ${max.value.toLocaleString()}
          </div>
        `;
      },
    },
    legend: {
      data: ["Average Salary", "Min", "Max"],
      bottom: 0,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: chartData.grades || chartData.map((d: any) => d.grade),
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
        name: "Average Salary",
        type: "bar",
        data: chartData.avgSalary || chartData.map((d: any) => d.avg_salary),
        itemStyle: {
          color: "#3b82f6",
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: "Min",
        type: "line",
        data: chartData.minSalary || chartData.map((d: any) => d.min_salary),
        lineStyle: { type: "dashed" },
        itemStyle: { color: "#94a3b8" },
      },
      {
        name: "Max",
        type: "line",
        data: chartData.maxSalary || chartData.map((d: any) => d.max_salary),
        lineStyle: { type: "dashed" },
        itemStyle: { color: "#10b981" },
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
