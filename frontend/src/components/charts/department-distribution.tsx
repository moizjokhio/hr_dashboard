"use client";

import ReactECharts from "echarts-for-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function DepartmentDistribution() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "distribution", "department"],
    queryFn: () => analyticsApi.getDistribution("department"),
  });

  // Mock data for demo
  const mockData = [
    { value: 25000, name: "Operations" },
    { value: 15000, name: "Technology" },
    { value: 18000, name: "Retail Banking" },
    { value: 12000, name: "Corporate Banking" },
    { value: 8000, name: "Risk Management" },
    { value: 5000, name: "Compliance" },
    { value: 4000, name: "Human Resources" },
    { value: 6000, name: "Finance" },
    { value: 3500, name: "Treasury" },
    { value: 3500, name: "Others" },
  ];

  const chartData =
    data?.distribution?.map((d: any) => ({
      value: d.count,
      name: d.value,
    })) || mockData;

  const option = {
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    legend: {
      type: "scroll",
      orient: "vertical",
      right: 10,
      top: 20,
      bottom: 20,
      textStyle: {
        fontSize: 11,
      },
    },
    series: [
      {
        name: "Employees",
        type: "pie",
        radius: ["40%", "70%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: "#fff",
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: "bold",
          },
        },
        data: chartData,
      },
    ],
    color: [
      "#3b82f6",
      "#06b6d4",
      "#10b981",
      "#f59e0b",
      "#ef4444",
      "#8b5cf6",
      "#ec4899",
      "#64748b",
      "#14b8a6",
      "#f97316",
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
