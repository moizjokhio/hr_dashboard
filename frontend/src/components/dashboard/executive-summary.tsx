"use client";

import { useState } from "react";
import { Users, DollarSign, UserMinus, PieChart, Filter } from "lucide-react";
import ReactECharts from "echarts-for-react";

interface ExecutiveSummaryProps {
  headcount: number;
  totalHeadcount: number;
  activePayrollBurn: number;
  totalPayrollBurn: number;
  attrition: number;
  activeGenderRatio: { name: string; value: number }[];
  allGenderRatio: { name: string; value: number }[];
}

export function ExecutiveSummary({
  headcount,
  totalHeadcount,
  activePayrollBurn,
  totalPayrollBurn,
  attrition,
  activeGenderRatio,
  allGenderRatio,
}: ExecutiveSummaryProps) {
  const [showAllEmployees, setShowAllEmployees] = useState(false);

  const displayHeadcount = showAllEmployees ? totalHeadcount : headcount;
  const displayGenderRatio = showAllEmployees ? allGenderRatio : activeGenderRatio;
  const displayPayrollBurn = showAllEmployees ? totalPayrollBurn : activePayrollBurn;

  const formatCurrency = (value: number) => {
    return "PKR " + new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const genderChartOption = {
    tooltip: {
      trigger: "item",
    },
    legend: {
      bottom: "0%",
      left: "center",
    },
    series: [
      {
        name: "DEI",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2,
        },
        label: {
          show: false,
          position: "center",
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: "bold",
          },
        },
        labelLine: {
          show: false,
        },
        data: displayGenderRatio,
      },
    ],
  };

  return (
    <div className="mb-8">
      {/* Toggle Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Executive Summary</h2>
          <p className="text-sm text-gray-500 mt-1">Key workforce metrics and insights</p>
        </div>
        
        {/* Modern Segmented Control */}
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-1 rounded-lg border border-gray-200 shadow-md flex items-center gap-1">
          <button
            onClick={() => setShowAllEmployees(false)}
            className={`relative px-4 py-2.5 rounded-md text-sm font-semibold transition-all duration-200 flex items-center gap-2 ${
              !showAllEmployees
                ? "bg-white text-green-600 shadow-md"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Filter className="w-4 h-4" />
            Active Only
          </button>
          <button
            onClick={() => setShowAllEmployees(true)}
            className={`relative px-4 py-2.5 rounded-md text-sm font-semibold transition-all duration-200 flex items-center gap-2 ${
              showAllEmployees
                ? "bg-white text-blue-600 shadow-md"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Users className="w-4 h-4" />
            All Employees
          </button>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Headcount */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Headcount</p>
              <h3 className="text-3xl font-bold text-gray-900 mt-2">
                {displayHeadcount.toLocaleString()}
              </h3>
            </div>
            <div className="p-2 bg-blue-50 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm font-medium">
            <span className={showAllEmployees ? "text-blue-600" : "text-green-600"}>
              {showAllEmployees ? "✓ All Employees" : "✓ Active Employees"}
            </span>
          </div>
        </div>

        {/* Payroll Burn */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Payroll Burn</p>
              <h3 className="text-3xl font-bold text-gray-900 mt-2">
                {formatCurrency(displayPayrollBurn)}
              </h3>
            </div>
            <div className="p-2 bg-green-50 rounded-lg">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-gray-500">
            <span>{showAllEmployees ? "Monthly Gross Salary (All)" : "Monthly Gross Salary (Active)"}</span>
          </div>
        </div>

        {/* Attrition Alert */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Attrition Alert</p>
              <h3 className="text-3xl font-bold text-gray-900 mt-2">
                {attrition}
              </h3>
            </div>
            <div className="p-2 bg-red-50 rounded-lg">
              <UserMinus className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-red-600">
            <span className="font-medium">Terminations this month</span>
          </div>
        </div>

        {/* Gender Ratio - DEI */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <p className="text-sm font-medium text-gray-500">DEI</p>
            <PieChart className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex-1 min-h-[120px]">
            <ReactECharts
              option={genderChartOption}
              style={{ height: "100%", width: "100%" }}
              opts={{ renderer: "svg" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
