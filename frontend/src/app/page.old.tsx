"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { DashboardSummary } from "@/components/dashboard/dashboard-summary";
import { HeadcountChart } from "@/components/charts/headcount-chart";
import { DepartmentDistribution } from "@/components/charts/department-distribution";
import { CompensationChart } from "@/components/charts/compensation-chart";
import { PerformanceChart } from "@/components/charts/performance-chart";
import { AISearchBar } from "@/components/ai/ai-search-bar";

export default function HomePage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        {/* Main content area */}
        <main className="flex-1 overflow-auto p-6">
          {/* AI Search Bar */}
          <div className="mb-6">
            <AISearchBar />
          </div>

          {/* Summary Cards */}
          <DashboardSummary />

          {/* Charts Grid */}
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-card rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Headcount by Department</h3>
              <HeadcountChart />
            </div>

            <div className="bg-card rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Department Distribution</h3>
              <DepartmentDistribution />
            </div>

            <div className="bg-card rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Compensation by Grade</h3>
              <CompensationChart />
            </div>

            <div className="bg-card rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Distribution</h3>
              <PerformanceChart />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
