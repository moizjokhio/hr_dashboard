"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import ReactECharts from "echarts-for-react";
import { HiringInsightsWrapper } from "./hiring-insights-wrapper";
import { HierarchicalHeadcount } from "./hierarchical-headcount";
import { HierarchicalGraphs } from "./hierarchical-graphs";
import { BranchManagerAnalytics } from "./branch-manager-analytics";
import Link from "next/link";
import {
  Users,
  TrendingUp,
  DollarSign,
  Heart,
  AlertTriangle,
  BarChart3,
  Download,
  UserPlus,
  Globe,
  Building2,
  UserMinus,
  Briefcase,
  PieChart,
  MapPin,
} from "lucide-react";

interface AnalyticsContentProps {
  headcount: any;
  diversity: any;
  compensation: any;
  attrition: any;
  hiring?: any;
  workforce?: any;
  geographic?: any;
  termination?: any;
  compensationInsights?: any;
  summary?: any;
  deptGroupHierarchy?: any;
  clusterHierarchy?: any;
  regionHierarchy?: any;
  divisionHierarchy?: any;
  branchManagerAnalytics?: any;
}

export function AnalyticsContent({
  headcount,
  diversity,
  compensation,
  attrition,
  hiring,
  workforce,
  geographic,
  termination,
  compensationInsights,
  summary,
  deptGroupHierarchy,
  clusterHierarchy,
  regionHierarchy,
  divisionHierarchy,
  branchManagerAnalytics,
}: AnalyticsContentProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("summary");

  const tabs = [
    { id: "summary", label: "Executive Summary", icon: PieChart },
    { id: "hiring", label: "Hiring Insights", icon: UserPlus },
    { id: "workforce", label: "Workforce", icon: Briefcase },
    { id: "headcount", label: "Headcount", icon: Users },
    { id: "diversity", label: "Diversity", icon: Heart },
    { id: "geographic", label: "Geographic", icon: Globe },
    { id: "compensation", label: "Compensation", icon: DollarSign },
    { id: "attrition", label: "Attrition", icon: UserMinus },
    { id: "branches", label: "Branch Coverage", icon: MapPin },
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
                  <h1 className="text-2xl font-bold">HR Analytics & Insights</h1>
                  <p className="text-sm text-muted-foreground">
                    Comprehensive workforce analytics for strategic decision making
                  </p>
                </div>
              </div>

              <button className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-muted transition-colors">
                <Download className="h-4 w-4" />
                Export Report
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mt-4 flex-wrap">
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
            {activeTab === "summary" && summary && <ExecutiveSummary data={summary} />}
            {activeTab === "hiring" && hiring && (
              <HiringInsightsWrapper initialData={hiring}>
                {(data, selectedYear, setSelectedYear, isPending) => (
                  <HiringInsights data={data} selectedYear={selectedYear} setSelectedYear={setSelectedYear} isPending={isPending} />
                )}
              </HiringInsightsWrapper>
            )}
            {activeTab === "workforce" && workforce && <WorkforceInsights data={workforce} />}
            {activeTab === "headcount" && (
              <>
                <HeadcountAnalytics data={headcount} />
                {deptGroupHierarchy && clusterHierarchy && regionHierarchy && divisionHierarchy && (
                  <div className="mt-8 space-y-8">
                    <HierarchicalGraphs
                      deptGroupHierarchy={deptGroupHierarchy}
                      clusterHierarchy={clusterHierarchy}
                      regionHierarchy={regionHierarchy}
                      divisionHierarchy={divisionHierarchy}
                    />
                    <HierarchicalHeadcount
                      deptGroupHierarchy={deptGroupHierarchy}
                      clusterHierarchy={clusterHierarchy}
                      regionHierarchy={regionHierarchy}
                      divisionHierarchy={divisionHierarchy}
                    />
                  </div>
                )}
              </>
            )}
            {activeTab === "diversity" && <DiversityAnalytics data={diversity} />}
            {activeTab === "geographic" && geographic && <GeographicInsights data={geographic} />}
            {activeTab === "compensation" && <CompensationAnalytics data={compensation} insights={compensationInsights} />}
            {activeTab === "attrition" && <AttritionAnalytics data={attrition} termination={termination} />}
            {activeTab === "branches" && branchManagerAnalytics && <BranchManagerAnalytics data={branchManagerAnalytics} />}
          </div>
        </main>
      </div>
    </div>
  );
}

// ==================== EXECUTIVE SUMMARY ====================
function ExecutiveSummary({ data }: { data: any }) {
  const kpiCards = [
    { title: "Total Active Employees", value: data.activeEmployees?.toLocaleString() || "0", icon: Users, color: "bg-blue-500", description: "Currently employed staff" },
    { title: "Hired in 2025", value: data.hires2025?.toLocaleString() || "0", icon: UserPlus, color: "bg-green-500", description: `${data.femaleHires2025 || 0} females hired` },
    { title: "Terminations 2025", value: data.terminations2025?.toLocaleString() || "0", icon: UserMinus, color: "bg-red-500", description: "Left the organization" },
    { title: "Net Headcount 2025", value: data.netHeadcount2025 >= 0 ? `+${data.netHeadcount2025}` : data.netHeadcount2025, icon: TrendingUp, color: data.netHeadcount2025 >= 0 ? "bg-emerald-500" : "bg-orange-500", description: "Hires minus terminations" },
    { title: "Average Age", value: `${data.avgAge || 0} yrs`, icon: Users, color: "bg-purple-500", description: "Workforce average age" },
    { title: "Average Tenure", value: `${data.avgTenure || 0} yrs`, icon: Briefcase, color: "bg-indigo-500", description: "Average years of service" },
    { title: "Average Salary", value: `PKR ${(data.avgSalary || 0).toLocaleString()}`, icon: DollarSign, color: "bg-amber-500", description: "Gross monthly salary" },
    { title: "Recent Hires (30 days)", value: data.recentHires?.toLocaleString() || "0", icon: UserPlus, color: "bg-cyan-500", description: "New joiners this month" },
  ];

  const genderRatio = data.activeEmployees > 0 ? ((data.activeFemales / data.activeEmployees) * 100).toFixed(1) : "0";

  const genderChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0 },
    series: [{
      type: "pie", radius: ["50%", "70%"], avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: "#fff", borderWidth: 2 },
      label: { show: true, formatter: "{b}\n{c}" },
      data: [
        { value: data.activeMales || 0, name: "Male", itemStyle: { color: "#3b82f6" } },
        { value: data.activeFemales || 0, name: "Female", itemStyle: { color: "#ec4899" } },
      ],
    }],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi, index) => (
          <div key={index} className="bg-card p-6 rounded-xl border shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{kpi.title}</p>
                <p className="text-3xl font-bold mt-1">{kpi.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{kpi.description}</p>
              </div>
              <div className={`p-3 rounded-lg ${kpi.color}`}>
                <kpi.icon className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm">
          <h3 className="font-semibold mb-4">Gender Distribution</h3>
          <ReactECharts option={genderChart} style={{ height: "250px" }} />
          <div className="text-center mt-2">
            <span className="text-sm text-muted-foreground">Female Ratio: </span>
            <span className="font-semibold text-pink-500">{genderRatio}%</span>
          </div>
        </div>

        <div className="bg-card p-6 rounded-xl border shadow-sm col-span-2">
          <h3 className="font-semibold mb-4">Organization Overview</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Building2 className="h-8 w-8 mx-auto text-blue-500 mb-2" />
              <p className="text-2xl font-bold">{data.groups || 0}</p>
              <p className="text-sm text-muted-foreground">Groups</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Globe className="h-8 w-8 mx-auto text-green-500 mb-2" />
              <p className="text-2xl font-bold">{data.regions || 0}</p>
              <p className="text-sm text-muted-foreground">Regions</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Building2 className="h-8 w-8 mx-auto text-purple-500 mb-2" />
              <p className="text-2xl font-bold">{data.branches || 0}</p>
              <p className="text-sm text-muted-foreground">Branches</p>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 rounded-lg">
            <h4 className="font-medium mb-2">Key Insight</h4>
            <p className="text-sm text-muted-foreground">
              {data.hires2025 > 0 ? (
                <>In 2025, <span className="font-semibold text-green-600">{data.hires2025} employees</span> were hired, 
                with <span className="font-semibold text-pink-600">{data.femaleHires2025} ({((data.femaleHires2025/data.hires2025)*100).toFixed(1)}%) being female</span>. 
                The net headcount change is <span className={`font-semibold ${data.netHeadcount2025 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {data.netHeadcount2025 >= 0 ? `+${data.netHeadcount2025}` : data.netHeadcount2025}
                </span>.</>
              ) : "No hiring data available for 2025 yet."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ==================== HIRING INSIGHTS ====================
function HiringInsights({ data, selectedYear, setSelectedYear, isPending }: { data: any; selectedYear: number; setSelectedYear: (year: number) => void; isPending: boolean }) {
  // Get available years from the data
  const availableYears = data.hiringByYear?.map((d: any) => d.year) || [];
  
  const yearlyHiringChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Yearly Hiring Trend", left: "center" },
    xAxis: { type: "category", data: [...data.hiringByYear].reverse().map((d: any) => d.year) },
    yAxis: { type: "value", name: "Hires" },
    series: [{ type: "bar", data: [...data.hiringByYear].reverse().map((d: any) => d.value),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#059669' }]}, borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top" }
    }],
  };

  const monthlyHiring2025Chart = {
    tooltip: { trigger: "axis" },
    title: { text: `${selectedYear} Monthly Hiring`, left: "center" },
    xAxis: { type: "category", data: data.hires2025ByMonth?.map((d: any) => d.month) || [] },
    yAxis: { type: "value" },
    series: [{ type: "line", smooth: true, data: data.hires2025ByMonth?.map((d: any) => d.value) || [],
      itemStyle: { color: "#3b82f6" }, areaStyle: { opacity: 0.3 }, label: { show: true, position: "top" }
    }],
  };

  const genderHires2025Chart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: `${selectedYear} Hires by Gender`, left: "center" },
    legend: { bottom: 0 },
    series: [{ type: "pie", radius: ["40%", "65%"],
      data: data.genderHires2025?.map((d: any) => ({
        value: d.value,
        name: d.name === 'M' || d.name === 'Male' ? 'Male' : d.name === 'F' || d.name === 'Female' ? 'Female' : d.name,
        itemStyle: { color: (d.name === 'M' || d.name === 'Male') ? '#3b82f6' : '#ec4899' }
      })) || [],
    }],
  };

  const groupHires2025Chart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: `${selectedYear} Hires by Group (Top 10)`, left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: [...(data.groupHires2025 || [])].reverse().map((d: any) => d.name), axisLabel: { width: 120, overflow: "truncate" } },
    series: [{ type: "bar", data: [...(data.groupHires2025 || [])].reverse().map((d: any) => d.value),
      itemStyle: { color: "#8b5cf6", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" }
    }],
  };

  const yoyChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Year-over-Year Comparison", left: "center" },
    legend: { bottom: 0 },
    xAxis: { type: "category", data: data.yoyComparison?.map((d: any) => d.year) || [] },
    yAxis: { type: "value" },
    series: [
      { name: "Total Hires", type: "bar", data: data.yoyComparison?.map((d: any) => d.total_hires) || [], itemStyle: { color: "#3b82f6" } },
      { name: "Female Hires", type: "bar", data: data.yoyComparison?.map((d: any) => d.female_hires) || [], itemStyle: { color: "#ec4899" } },
      { name: "Male Hires", type: "bar", data: data.yoyComparison?.map((d: any) => d.male_hires) || [], itemStyle: { color: "#06b6d4" } }
    ],
  };

  const contractTypeChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: `${selectedYear} Hires by Contract Type`, left: "center" },
    legend: { bottom: 0 },
    series: [{ type: "pie", radius: ["40%", "65%"],
      data: data.contractTypeHires?.map((d: any) => ({
        value: d.value,
        name: d.name,
        itemStyle: { color: d.name?.toLowerCase().includes('permanent') ? '#10b981' : '#f59e0b' }
      })) || [],
    }],
  };

  const cadreChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: `${selectedYear} Hires by Cadre`, left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: [...(data.cadreHires || [])].reverse().map((d: any) => d.name), axisLabel: { width: 120, overflow: "truncate" } },
    series: [{ type: "bar", data: [...(data.cadreHires || [])].reverse().map((d: any) => d.value),
      itemStyle: { color: "#6366f1", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" }
    }],
  };

  return (
    <div className="space-y-6">
      {/* Year Selector */}
      <div className="flex items-center justify-between bg-card p-4 rounded-xl border shadow-sm">
        <div>
          <h3 className="text-lg font-semibold">Select Year</h3>
          <p className="text-sm text-muted-foreground">View hiring insights for a specific year</p>
        </div>
        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          disabled={isPending}
          className="px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {availableYears.map((year: number) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      {isPending && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <span className="ml-2 text-muted-foreground">Loading data for {selectedYear}...</span>
        </div>
      )}

      <div className={isPending ? "opacity-50 pointer-events-none" : ""}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Total Hires in {selectedYear}</p>
            <p className="text-4xl font-bold mt-2">{data.totalHires2025?.toLocaleString() || 0}</p>
            <UserPlus className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-pink-500 to-rose-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Female Hires {selectedYear}</p>
            <p className="text-4xl font-bold mt-2">{data.genderHires2025?.find((g: any) => g.name === 'Female' || g.name === 'F')?.value || 0}</p>
            <Heart className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Male Hires {selectedYear}</p>
            <p className="text-4xl font-bold mt-2">{data.genderHires2025?.find((g: any) => g.name === 'Male' || g.name === 'M')?.value || 0}</p>
            <Users className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-violet-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Top Hiring Dept</p>
            <p className="text-lg font-bold mt-2 truncate">{data.deptHires2025?.[0]?.name || "N/A"}</p>
            <p className="text-2xl font-bold">{data.deptHires2025?.[0]?.value || 0} hires</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={yearlyHiringChart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={monthlyHiring2025Chart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={genderHires2025Chart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={groupHires2025Chart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={contractTypeChart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={cadreChart} style={{ height: "350px" }} /></div>
          <div className="bg-card p-6 rounded-xl border shadow-sm lg:col-span-2"><ReactECharts option={yoyChart} style={{ height: "400px" }} /></div>
        </div>
      </div>
    </div>
  );
}

// ==================== WORKFORCE INSIGHTS ====================
function WorkforceInsights({ data }: { data: any }) {
  const statusChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Employment Status Breakdown", left: "center" },
    legend: { bottom: 0 },
    series: [{ type: "pie", radius: "60%", data: data.statusBreakdown || [],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: "rgba(0,0,0,0.5)" } }
    }],
  };

  const tenureChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Tenure Distribution", left: "center" },
    xAxis: { type: "category", data: data.tenureDistribution?.map((d: any) => d.name) || [] },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: data.tenureDistribution?.map((d: any) => d.value) || [],
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#6366f1' }, { offset: 1, color: '#a855f7' }]}, borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top" }
    }],
  };

  const contractChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Contract Type Distribution", left: "center" },
    series: [{ type: "pie", radius: ["40%", "60%"], data: data.contractType || [] }],
  };

  const cadreChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Cadre Distribution", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: [...(data.cadreDistribution || [])].reverse().map((d: any) => d.name) },
    series: [{ type: "bar", data: [...(data.cadreDistribution || [])].reverse().map((d: any) => d.value),
      itemStyle: { color: "#f59e0b", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" }
    }],
  };

  const maritalChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Marital Status", left: "center" },
    series: [{ type: "pie", radius: "55%", data: data.maritalStatus || [], color: ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"] }],
  };

  const religionChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Religion Distribution", left: "center" },
    series: [{ type: "pie", radius: ["30%", "55%"], roseType: "radius", data: data.religionDistribution || [] }],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl text-white">
          <p className="text-sm opacity-90">Total Active Employees</p>
          <p className="text-4xl font-bold mt-2">{data.totalActive?.toLocaleString() || 0}</p>
        </div>
        <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 p-6 rounded-xl text-white">
          <p className="text-sm opacity-90">Nationalities</p>
          <p className="text-4xl font-bold mt-2">{data.nationalityDistribution?.length || 0}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl text-white">
          <p className="text-sm opacity-90">Divisions</p>
          <p className="text-4xl font-bold mt-2">{data.divisionBreakdown?.length || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={statusChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={tenureChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={contractChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={cadreChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={maritalChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={religionChart} style={{ height: "350px" }} /></div>
      </div>
    </div>
  );
}

// ==================== GEOGRAPHIC INSIGHTS ====================
function GeographicInsights({ data }: { data: any }) {
  const regionChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Employees by Region", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: [...(data.byRegion || [])].slice(0, 15).reverse().map((d: any) => d.name) },
    series: [{ type: "bar", data: [...(data.byRegion || [])].slice(0, 15).reverse().map((d: any) => d.value),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#3b82f6' }, { offset: 1, color: '#06b6d4' }]}, borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: "right" }
    }],
  };

  const districtChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Top 15 Districts by Headcount", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: [...(data.byDistrict || [])].reverse().map((d: any) => d.name) },
    series: [{ type: "bar", data: [...(data.byDistrict || [])].reverse().map((d: any) => d.value),
      itemStyle: { color: "#10b981", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" }
    }],
  };

  const clusterChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Cluster Distribution", left: "center" },
    series: [{ type: "pie", radius: ["35%", "60%"], data: data.byCluster || [] }],
  };

  const branchLevelChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Branch Level Distribution", left: "center" },
    series: [{ type: "pie", radius: "55%", data: data.branchLevel || [], color: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"] }],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-xl border shadow-sm text-center">
          <Globe className="h-10 w-10 mx-auto text-blue-500 mb-2" />
          <p className="text-3xl font-bold">{data.byRegion?.length || 0}</p>
          <p className="text-sm text-muted-foreground">Regions</p>
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm text-center">
          <Building2 className="h-10 w-10 mx-auto text-green-500 mb-2" />
          <p className="text-3xl font-bold">{data.byDistrict?.length || 0}</p>
          <p className="text-sm text-muted-foreground">Districts</p>
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm text-center">
          <Building2 className="h-10 w-10 mx-auto text-purple-500 mb-2" />
          <p className="text-3xl font-bold">{data.byCluster?.length || 0}</p>
          <p className="text-sm text-muted-foreground">Clusters</p>
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm text-center">
          <TrendingUp className="h-10 w-10 mx-auto text-amber-500 mb-2" />
          <p className="text-3xl font-bold">{data.byRegion?.[0]?.name || "N/A"}</p>
          <p className="text-sm text-muted-foreground">Largest Region</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={regionChart} style={{ height: "450px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={districtChart} style={{ height: "450px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={clusterChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={branchLevelChart} style={{ height: "350px" }} /></div>
      </div>
    </div>
  );
}

// ==================== HEADCOUNT ANALYTICS ====================
function HeadcountAnalytics({ data }: { data: any }) {
  const topGroups = data.byGroup?.slice(0, 10).reverse() || [];
  const topSubGroups = data.bySubGroup?.slice(0, 15).reverse() || [];
  const topLocations = [...(data.byLocation || [])].sort((a: any, b: any) => b.value - a.value).slice(0, 10).reverse();

  const groupChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Headcount by Group (Top 10)", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: topGroups.map((d: any) => d.name), axisLabel: { interval: 0, width: 150, overflow: "truncate" } },
    series: [{ type: "bar", data: topGroups.map((d: any) => d.value), itemStyle: { color: "#3b82f6", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" } }],
  };

  const subGroupChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Headcount by Sub-Group (Top 15)", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: topSubGroups.map((d: any) => d.name), axisLabel: { interval: 0, width: 150, overflow: "truncate" } },
    series: [{ type: "bar", data: topSubGroups.map((d: any) => d.value), itemStyle: { color: "#8b5cf6", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" } }],
  };

  const gradeChart = {
    tooltip: { trigger: "axis" },
    title: { text: "By Grade", left: "center" },
    xAxis: { type: "category", data: data.byGrade.map((d: any) => d.name), axisLabel: { rotate: 45 } },
    yAxis: { type: "value" },
    grid: { bottom: 80 },
    series: [{ type: "bar", data: data.byGrade.map((d: any) => d.value), itemStyle: { borderRadius: [4, 4, 0, 0] } }],
  };

  const locationChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Headcount by Location (Top 10)", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: topLocations.map((d: any) => d.name), axisLabel: { interval: 0, width: 150, overflow: "truncate" } },
    series: [{ type: "bar", data: topLocations.map((d: any) => d.value), itemStyle: { color: "#10b981", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right" } }],
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={groupChart} style={{ height: "400px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={gradeChart} style={{ height: "400px" }} /></div>
      </div>
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={subGroupChart} style={{ height: "500px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={locationChart} style={{ height: "500px" }} /></div>
      </div>
    </div>
  );
}

// ==================== DIVERSITY ANALYTICS ====================
function DiversityAnalytics({ data }: { data: any }) {
  const genderChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Gender Distribution", left: "center" },
    series: [{ type: "pie", radius: ["40%", "70%"],
      data: data.gender?.map((d: any) => ({
        ...d, name: d.name === 'M' ? 'Male' : d.name === 'F' ? 'Female' : d.name,
        itemStyle: { color: (d.name === 'M' || d.name === 'Male') ? '#3b82f6' : '#ec4899' }
      })) || [],
      label: { formatter: "{b}\n{c} ({d}%)" }
    }],
  };

  const ageChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Age Distribution", left: "center" },
    xAxis: { type: "category", data: data.age.map((d: any) => d.name) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: data.age.map((d: any) => d.value),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#8b5cf6' }, { offset: 1, color: '#a855f7' }]}, borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top" }
    }],
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={genderChart} style={{ height: "350px" }} /></div>
      <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={ageChart} style={{ height: "350px" }} /></div>
    </div>
  );
}

// ==================== COMPENSATION ANALYTICS ====================
function CompensationAnalytics({ data, insights }: { data: any; insights?: any }) {
  const topGroups = data.avgByGroup?.slice(0, 10).reverse() || [];
  const topDepts = data.avgByDepartment?.slice(0, 10).reverse() || [];

  const groupChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Avg Salary by Group (Top 10)", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: topGroups.map((d: any) => d.name), axisLabel: { interval: 0, width: 150, overflow: "truncate" } },
    series: [{ type: "bar", data: topGroups.map((d: any) => d.value), itemStyle: { color: "#10b981", borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: "right", formatter: (params: any) => `PKR ${Math.round(params.value).toLocaleString()}` }
    }],
  };

  const deptChart = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Avg Salary by Department (Top 10)", left: "center" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: topDepts.map((d: any) => d.name), axisLabel: { interval: 0, width: 150, overflow: "truncate" } },
    series: [{ type: "bar", data: topDepts.map((d: any) => d.value), itemStyle: { color: "#6366f1", borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: "right", formatter: (params: any) => `PKR ${Math.round(params.value).toLocaleString()}` }
    }],
  };

  const gradeChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Avg Salary by Grade", left: "center" },
    xAxis: { type: "category", data: data.avgByGrade.map((d: any) => d.name), axisLabel: { rotate: 45 } },
    yAxis: { type: "value" },
    grid: { bottom: 80 },
    series: [{ type: "bar", data: data.avgByGrade.map((d: any) => d.value), itemStyle: { color: "#f59e0b", borderRadius: [4, 4, 0, 0] } }],
  };

  const salaryDistChart = insights?.salaryDistribution ? {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Salary Distribution", left: "center" },
    series: [{ type: "pie", radius: ["35%", "60%"], data: insights.salaryDistribution, color: ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6", "#ec4899"] }],
  } : null;

  const genderPayChart = insights?.salaryByGender ? {
    tooltip: { trigger: "axis" },
    title: { text: "Average Salary by Gender", left: "center" },
    xAxis: { type: "category", data: insights.salaryByGender.map((d: any) => d.name === 'M' ? 'Male' : d.name === 'F' ? 'Female' : d.name) },
    yAxis: { type: "value", name: "PKR" },
    series: [{ type: "bar", data: insights.salaryByGender.map((d: any) => d.avg_salary),
      itemStyle: { color: (params: any) => params.dataIndex === 0 ? '#3b82f6' : '#ec4899', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top", formatter: (params: any) => `PKR ${Math.round(params.value).toLocaleString()}` }
    }],
  } : null;

  return (
    <div className="space-y-6">
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-emerald-500 to-green-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Total Monthly Payroll</p>
            <p className="text-3xl font-bold mt-2">PKR {(insights.totalPayroll / 1000000).toFixed(1)}M</p>
            <DollarSign className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-amber-500 to-orange-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Average Salary</p>
            <p className="text-3xl font-bold mt-2">PKR {Math.round(insights.avgSalary).toLocaleString()}</p>
            <TrendingUp className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">With PF Benefits</p>
            <p className="text-3xl font-bold mt-2">{insights.benefitsSummary?.with_pf || 0}</p>
            <Users className="h-8 w-8 mt-2 opacity-80" />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={deptChart} style={{ height: "400px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={gradeChart} style={{ height: "400px" }} /></div>
        {salaryDistChart && <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={salaryDistChart} style={{ height: "350px" }} /></div>}
        {genderPayChart && <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={genderPayChart} style={{ height: "350px" }} /></div>}
      </div>
    </div>
  );
}

// ==================== ATTRITION ANALYTICS ====================
function AttritionAnalytics({ data, termination }: { data: any; termination?: any }) {
  const trendChart = {
    tooltip: { trigger: "axis" },
    title: { text: "Termination Trend (Last 12 Months)", left: "center" },
    xAxis: { type: "category", data: data.trend.map((d: any) => d.name), axisLabel: { rotate: 45 } },
    yAxis: { type: "value" },
    grid: { bottom: 80 },
    series: [{ type: "line", smooth: true, data: data.trend.map((d: any) => d.value), itemStyle: { color: "#ef4444" }, areaStyle: { opacity: 0.2 },
      markPoint: { data: [{ type: "max", name: "Max" }, { type: "min", name: "Min" }] }
    }],
  };

  const reasonChart = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Termination Reasons", left: "center" },
    legend: { bottom: 0, type: "scroll" },
    series: [{ type: "pie", radius: ["30%", "55%"], data: data.byReason || [] }],
  };

  const tenureAtTermChart = termination?.terminationsByTenure ? {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    title: { text: "Tenure at Termination", left: "center" },
    series: [{ type: "pie", radius: "55%", data: termination.terminationsByTenure, color: ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"] }],
  } : null;

  const yearlyTermChart = termination?.terminationsByYear ? {
    tooltip: { trigger: "axis" },
    title: { text: "Yearly Terminations", left: "center" },
    xAxis: { type: "category", data: [...termination.terminationsByYear].reverse().map((d: any) => d.year) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: [...termination.terminationsByYear].reverse().map((d: any) => d.value),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#ef4444' }, { offset: 1, color: '#dc2626' }]}, borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top" }
    }],
  } : null;

  return (
    <div className="space-y-6">
      {termination && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-red-500 to-rose-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Terminations 2025</p>
            <p className="text-4xl font-bold mt-2">{termination.totalTerminations2025}</p>
            <UserMinus className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Avg Tenure at Exit</p>
            <p className="text-4xl font-bold mt-2">{termination.avgTenureAtTermination} yrs</p>
            <Briefcase className="h-8 w-8 mt-2 opacity-80" />
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-violet-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Top Exit Reason</p>
            <p className="text-lg font-bold mt-2 truncate">{termination.terminationsByReason?.[0]?.name || "N/A"}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-6 rounded-xl text-white">
            <p className="text-sm opacity-90">Top Exit Group</p>
            <p className="text-lg font-bold mt-2 truncate">{termination.terminationsByGroup?.[0]?.name || "N/A"}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={trendChart} style={{ height: "350px" }} /></div>
        <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={reasonChart} style={{ height: "350px" }} /></div>
        {yearlyTermChart && <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={yearlyTermChart} style={{ height: "350px" }} /></div>}
        {tenureAtTermChart && <div className="bg-card p-6 rounded-xl border shadow-sm"><ReactECharts option={tenureAtTermChart} style={{ height: "350px" }} /></div>}
      </div>
    </div>
  );
}
