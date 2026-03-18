"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { ExecutiveSummary } from "./executive-summary";
import { HRWorkflow } from "./hr-workflow";
import { OrgStructure } from "./org-structure";
import { Compensation } from "./compensation";

interface DashboardContentProps {
  metrics: {
    headcount: number;
    payrollBurn: number;
    attrition: number;
    genderRatio: { name: string; value: number }[];
  };
  workflow: {
    probationCliff: any[];
    retirementRadar: any[];
    disciplinaryWatch: any[];
  };
  orgStructure: {
    spanOfControl: { name: string; value: number }[];
    locationHeatmap: { name: string; value: number }[];
  };
  compensation: {
    salaryByGrade: Record<string, number[]>;
  };
}

export function DashboardContent({
  metrics,
  workflow,
  orgStructure,
  compensation,
}: DashboardContentProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        {/* Main content area */}
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900">HR Analytics Dashboard</h1>
              <p className="text-gray-500">Real-time insights and workforce metrics</p>
            </div>

            <ExecutiveSummary {...metrics} />
            

            <h2 className="text-xl font-semibold text-gray-900 mb-4">Organization & DEI</h2>
            <OrgStructure {...orgStructure} />
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Workflow Operations</h2>
            <HRWorkflow {...workflow} />

            <h2 className="text-xl font-semibold text-gray-900 mb-4">Compensation Analytics</h2>
            <Compensation {...compensation} />
          </div>
        </main>
      </div>
    </div>
  );
}
