"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import { formatNumber, formatCurrency, formatPercentage } from "@/lib/utils";
import {
  Users,
  UserCheck,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Star,
  AlertTriangle,
  UserPlus,
} from "lucide-react";

export function DashboardSummary() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: analyticsApi.getSummary,
  });

  // Mock data for demo
  const mockSummary = {
    total_employees: 100000,
    active_employees: 95000,
    average_salary: 185000,
    average_performance: 3.75,
    attrition_rate: 0.082,
    new_hires_30d: 250,
    departments_count: 20,
    high_risk_employees: 1250,
  };

  const metrics = [
    {
      label: "Total Employees",
      value: formatNumber(summary?.total_employees || mockSummary.total_employees),
      icon: Users,
      color: "text-blue-500",
      bgColor: "bg-blue-50",
      trend: "+2.5%",
      trendUp: true,
    },
    {
      label: "Active Employees",
      value: formatNumber(summary?.active_employees || mockSummary.active_employees),
      icon: UserCheck,
      color: "text-green-500",
      bgColor: "bg-green-50",
      trend: "+1.2%",
      trendUp: true,
    },
    {
      label: "Average Salary",
      value: formatCurrency(summary?.average_salary || mockSummary.average_salary),
      icon: DollarSign,
      color: "text-emerald-500",
      bgColor: "bg-emerald-50",
      trend: "+5.8%",
      trendUp: true,
    },
    {
      label: "Avg Performance",
      value: (summary?.average_performance || mockSummary.average_performance).toFixed(2),
      icon: Star,
      color: "text-yellow-500",
      bgColor: "bg-yellow-50",
      trend: "+0.15",
      trendUp: true,
    },
    {
      label: "Attrition Rate",
      value: formatPercentage(summary?.attrition_rate || mockSummary.attrition_rate),
      icon: TrendingDown,
      color: "text-red-500",
      bgColor: "bg-red-50",
      trend: "-0.5%",
      trendUp: false,
    },
    {
      label: "New Hires (30d)",
      value: formatNumber(summary?.new_hires_30d || mockSummary.new_hires_30d),
      icon: UserPlus,
      color: "text-purple-500",
      bgColor: "bg-purple-50",
      trend: "+15%",
      trendUp: true,
    },
    {
      label: "Departments",
      value: formatNumber(summary?.departments_count || mockSummary.departments_count),
      icon: Users,
      color: "text-indigo-500",
      bgColor: "bg-indigo-50",
      trend: "0",
      trendUp: true,
    },
    {
      label: "High Risk",
      value: formatNumber(summary?.high_risk_employees || mockSummary.high_risk_employees),
      icon: AlertTriangle,
      color: "text-orange-500",
      bgColor: "bg-orange-50",
      trend: "-8%",
      trendUp: false,
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="bg-card rounded-lg border p-6 animate-pulse"
          >
            <div className="h-4 bg-muted rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-muted rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="bg-card rounded-lg border p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{metric.label}</p>
              <p className="text-2xl font-bold mt-1">{metric.value}</p>
            </div>
            <div className={`p-3 rounded-lg ${metric.bgColor}`}>
              <metric.icon className={`h-6 w-6 ${metric.color}`} />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1">
            {metric.trendUp ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            <span
              className={`text-sm ${
                metric.trendUp ? "text-green-500" : "text-red-500"
              }`}
            >
              {metric.trend}
            </span>
            <span className="text-xs text-muted-foreground ml-1">vs last month</span>
          </div>
        </div>
      ))}
    </div>
  );
}
