"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { analyticsApi } from "@/lib/api";
import { formatNumber, formatCurrency, formatPercentage } from "@/lib/utils";
import ReactECharts from "echarts-for-react";
import {
  Users,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Heart,
  AlertTriangle,
  BarChart3,
  Download,
} from "lucide-react";

export default function AnalyticsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("headcount");
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);

  const { data: headcountData, isLoading: headcountLoading } = useQuery({
    queryKey: ["analytics", "headcount", selectedDepartments],
    queryFn: () => analyticsApi.getHeadcount({ departments: selectedDepartments }),
    enabled: activeTab === "headcount",
  });

  const { data: diversityData, isLoading: diversityLoading } = useQuery({
    queryKey: ["analytics", "diversity", selectedDepartments],
    queryFn: () => analyticsApi.getDiversity({ departments: selectedDepartments }),
    enabled: activeTab === "diversity",
  });

  const { data: compensationData, isLoading: compensationLoading } = useQuery({
    queryKey: ["analytics", "compensation", selectedDepartments],
    queryFn: () => analyticsApi.getCompensation({ departments: selectedDepartments }),
    enabled: activeTab === "compensation",
  });

  const { data: performanceData, isLoading: performanceLoading } = useQuery({
    queryKey: ["analytics", "performance", selectedDepartments],
    queryFn: () => analyticsApi.getPerformance({ departments: selectedDepartments }),
    enabled: activeTab === "performance",
  });

  const { data: attritionData, isLoading: attritionLoading } = useQuery({
    queryKey: ["analytics", "attrition", selectedDepartments],
    queryFn: () => analyticsApi.getAttrition({ departments: selectedDepartments }),
    enabled: activeTab === "attrition",
  });

  const tabs = [
    { id: "headcount", label: "Headcount", icon: Users },
    { id: "diversity", label: "Diversity", icon: Heart },
    { id: "compensation", label: "Compensation", icon: DollarSign },
    { id: "performance", label: "Performance", icon: TrendingUp },
    { id: "attrition", label: "Attrition", icon: AlertTriangle },
  ];

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          {/* Page header */}
          <div className="bg-card border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Analytics</h1>
                  <p className="text-sm text-muted-foreground">
                    Comprehensive workforce analytics and insights
                  </p>
                </div>
              </div>

              <button className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-muted transition-colors">
                <Download className="h-4 w-4" />
                Export Report
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mt-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === "headcount" && (
              <HeadcountAnalytics data={headcountData} isLoading={headcountLoading} />
            )}
            {activeTab === "diversity" && (
              <DiversityAnalytics data={diversityData} isLoading={diversityLoading} />
            )}
            {activeTab === "compensation" && (
              <CompensationAnalytics data={compensationData} isLoading={compensationLoading} />
            )}
            {activeTab === "performance" && (
              <PerformanceAnalytics data={performanceData} isLoading={performanceLoading} />
            )}
            {activeTab === "attrition" && (
              <AttritionAnalytics data={attritionData} isLoading={attritionLoading} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

// ============= Headcount Analytics =============
function HeadcountAnalytics({ data, isLoading }: { data: any; isLoading: boolean }) {
  // Mock data
  const mockData = {
    total: 100000,
    by_department: [
      { department: "Operations", count: 25000 },
      { department: "Technology", count: 15000 },
      { department: "Retail Banking", count: 18000 },
      { department: "Corporate Banking", count: 12000 },
      { department: "Risk Management", count: 8000 },
    ],
    by_grade: [
      { grade: "OG-4", count: 20000 },
      { grade: "OG-3", count: 25000 },
      { grade: "OG-2", count: 20000 },
      { grade: "OG-1", count: 15000 },
      { grade: "AVP", count: 10000 },
      { grade: "VP", count: 6000 },
      { grade: "SVP+", count: 4000 },
    ],
    by_country: [
      { country: "Pakistan", count: 85000 },
      { country: "UAE", count: 8000 },
      { country: "Bahrain", count: 4000 },
      { country: "Qatar", count: 3000 },
    ],
  };

  const chartData = data || mockData;

  const departmentChart = {
    tooltip: { trigger: "item" },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      data: chartData.by_department?.map((d: any) => ({
        value: d.count,
        name: d.department,
      })) || [],
    }],
  };

  const gradeChart = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: chartData.by_grade?.map((d: any) => d.grade) || [] },
    yAxis: { type: "value" },
    series: [{
      type: "bar",
      data: chartData.by_grade?.map((d: any) => d.count) || [],
      itemStyle: { borderRadius: [4, 4, 0, 0] },
    }],
  };

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Employees"
          value={formatNumber(chartData.total || 100000)}
          icon={Users}
          trend="+2.5%"
          trendUp={true}
        />
        <MetricCard
          label="Pakistan"
          value={formatNumber(chartData.by_country?.[0]?.count || 85000)}
          icon={Users}
        />
        <MetricCard
          label="Gulf Region"
          value={formatNumber(15000)}
          icon={Users}
        />
        <MetricCard
          label="Departments"
          value="20"
          icon={Users}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">By Department</h3>
          <ReactECharts option={departmentChart} style={{ height: "350px" }} />
        </div>
        <div className="bg-card border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">By Grade Level</h3>
          <ReactECharts option={gradeChart} style={{ height: "350px" }} />
        </div>
      </div>
    </div>
  );
}

// ============= Diversity Analytics =============
function DiversityAnalytics({ data, isLoading }: { data: any; isLoading: boolean }) {
  const mockData = {
    gender: { male: 70000, female: 30000 },
    female_leadership: 0.15,
  };

  const chartData = data || mockData;

  const genderChart = {
    tooltip: { trigger: "item" },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      data: [
        { value: chartData.gender?.male || 70000, name: "Male" },
        { value: chartData.gender?.female || 30000, name: "Female" },
      ],
      color: ["#3b82f6", "#ec4899"],
    }],
  };

  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Female %"
          value="30%"
          icon={Heart}
          trend="+2%"
          trendUp={true}
        />
        <MetricCard
          label="Female Leadership"
          value="15%"
          icon={TrendingUp}
          trend="+3%"
          trendUp={true}
        />
        <MetricCard
          label="Diversity Index"
          value="0.72"
          icon={Heart}
        />
        <MetricCard
          label="PWD %"
          value="2.1%"
          icon={Heart}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
          <ReactECharts option={genderChart} style={{ height: "350px" }} />
        </div>
        <div className="bg-card border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Gender by Department</h3>
          <p className="text-muted-foreground text-center py-20">Chart coming soon</p>
        </div>
      </div>
    </div>
  );
}

// ============= Compensation Analytics =============
function CompensationAnalytics({ data, isLoading }: { data: any; isLoading: boolean }) {
  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Salary"
          value={formatCurrency(185000)}
          icon={DollarSign}
          trend="+5.8%"
          trendUp={true}
        />
        <MetricCard
          label="Median Salary"
          value={formatCurrency(145000)}
          icon={DollarSign}
        />
        <MetricCard
          label="Gender Pay Gap"
          value="4.2%"
          icon={TrendingDown}
          trend="-0.5%"
          trendUp={false}
        />
        <MetricCard
          label="Total Payroll"
          value="PKR 18.5B"
          icon={DollarSign}
        />
      </div>

      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Salary by Grade</h3>
        <p className="text-muted-foreground text-center py-20">Chart coming soon</p>
      </div>
    </div>
  );
}

// ============= Performance Analytics =============
function PerformanceAnalytics({ data, isLoading }: { data: any; isLoading: boolean }) {
  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Score"
          value="3.75"
          icon={TrendingUp}
          trend="+0.15"
          trendUp={true}
        />
        <MetricCard
          label="High Performers"
          value={formatNumber(15000)}
          icon={TrendingUp}
        />
        <MetricCard
          label="Needs Improvement"
          value={formatNumber(7500)}
          icon={AlertTriangle}
        />
        <MetricCard
          label="Score > 4.0"
          value="25%"
          icon={TrendingUp}
        />
      </div>

      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Performance Distribution</h3>
        <p className="text-muted-foreground text-center py-20">Chart coming soon</p>
      </div>
    </div>
  );
}

// ============= Attrition Analytics =============
function AttritionAnalytics({ data, isLoading }: { data: any; isLoading: boolean }) {
  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Attrition Rate"
          value="8.2%"
          icon={TrendingDown}
          trend="-0.5%"
          trendUp={false}
        />
        <MetricCard
          label="Voluntary"
          value="6.5%"
          icon={AlertTriangle}
        />
        <MetricCard
          label="Involuntary"
          value="1.7%"
          icon={AlertTriangle}
        />
        <MetricCard
          label="High Risk"
          value={formatNumber(1250)}
          icon={AlertTriangle}
        />
      </div>

      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Attrition by Department</h3>
        <p className="text-muted-foreground text-center py-20">Chart coming soon</p>
      </div>
    </div>
  );
}

// ============= Helper Components =============
function MetricCard({
  label,
  value,
  icon: Icon,
  trend,
  trendUp,
}: {
  label: string;
  value: string;
  icon: any;
  trend?: string;
  trendUp?: boolean;
}) {
  return (
    <div className="bg-card border rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="p-3 rounded-lg bg-primary/10">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      </div>
      {trend && (
        <div className="mt-2 flex items-center gap-1">
          {trendUp ? (
            <TrendingUp className="h-4 w-4 text-green-500" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-500" />
          )}
          <span className={`text-sm ${trendUp ? "text-green-500" : "text-red-500"}`}>
            {trend}
          </span>
        </div>
      )}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-card border rounded-lg p-6 animate-pulse">
            <div className="h-4 bg-muted rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-muted rounded w-3/4"></div>
          </div>
        ))}
      </div>
      <div className="bg-card border rounded-lg p-6 h-96 animate-pulse">
        <div className="h-6 bg-muted rounded w-1/4 mb-4"></div>
        <div className="h-full bg-muted rounded"></div>
      </div>
    </div>
  );
}
