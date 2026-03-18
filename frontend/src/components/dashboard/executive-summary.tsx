"use client";

import { Users, DollarSign, UserMinus, PieChart } from "lucide-react";
import ReactECharts from "echarts-for-react";

interface ExecutiveSummaryProps {
  headcount: number;
  payrollBurn: number;
  attrition: number;
  genderRatio: { name: string; value: number }[];
}

export function ExecutiveSummary({
  headcount,
  payrollBurn,
  attrition,
  genderRatio,
}: ExecutiveSummaryProps) {
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
        data: genderRatio,
      },
    ],
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Headcount */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-gray-500">Total Headcount</p>
            <h3 className="text-3xl font-bold text-gray-900 mt-2">
              {headcount.toLocaleString()}
            </h3>
          </div>
          <div className="p-2 bg-blue-50 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
        </div>
        <div className="mt-4 flex items-center text-sm text-green-600">
          <span className="font-medium">Active Employees</span>
        </div>
      </div>

      {/* Payroll Burn */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-gray-500">Payroll Burn</p>
            <h3 className="text-3xl font-bold text-gray-900 mt-2">
              {formatCurrency(payrollBurn)}
            </h3>
          </div>
          <div className="p-2 bg-green-50 rounded-lg">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
        </div>
        <div className="mt-4 flex items-center text-sm text-gray-500">
          <span>Monthly Gross Salary</span>
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

      {/* Gender Ratio */}
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
  );
}
