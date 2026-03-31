"use client";

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";

interface CompensationProps {
  salaryByGrade: Record<string, number[]>;
}

const PRIORITY_GRADE_ORDER = [
  "CON",
  "OG-4",
  "OG-3",
  "OG-2",
  "OG-1",
  "AVP-1",
  "AVP-II",
  "RVP",
  "VP",
  "VP-1",
  "VP-11",
  "SVP",
  "SVP-1",
  "SVP-11",
  "REST SVP",
  "EVP",
  "EVP-1",
  "EVP-11",
  "EVP-111",
  "REST EVP",
  "SEVP",
  "SEVP-1",
  "SEVP-11",
  "PRES",
] as const;

function normalizeGradeForOrder(value: string) {
  return value
    .toUpperCase()
    .replace(/_/g, "-")
    .replace(/\s+/g, " ")
    .replace(/\bI\b/g, "1")
    .replace(/\bII\b/g, "11")
    .replace(/\bIII\b/g, "111")
    .trim();
}

const ORDER_INDEX = new Map(
  PRIORITY_GRADE_ORDER.map((grade, idx) => [normalizeGradeForOrder(grade), idx])
);

export function Compensation({ salaryByGrade }: CompensationProps) {
  const chartData = useMemo(() => {
    const categories = Object.keys(salaryByGrade).sort((a, b) => {
      const aNorm = normalizeGradeForOrder(a);
      const bNorm = normalizeGradeForOrder(b);

      const aIdx = ORDER_INDEX.get(aNorm);
      const bIdx = ORDER_INDEX.get(bNorm);

      const aKnown = aIdx !== undefined;
      const bKnown = bIdx !== undefined;

      if (aKnown && bKnown) {
        return (aIdx as number) - (bIdx as number);
      }
      if (aKnown) return -1;
      if (bKnown) return 1;

      return aNorm.localeCompare(bNorm);
    });
    const avgData: number[] = [];
    const minData: number[] = [];
    const maxData: number[] = [];
    const q1Data: number[] = [];
    const q3Data: number[] = [];

    categories.forEach((grade) => {
      const salaries = salaryByGrade[grade].sort((a, b) => a - b);
      if (salaries.length === 0) {
        avgData.push(0);
        minData.push(0);
        maxData.push(0);
        q1Data.push(0);
        q3Data.push(0);
      } else {
        const sum = salaries.reduce((a, b) => a + b, 0);
        avgData.push(Math.round(sum / salaries.length));
        minData.push(salaries[0]);
        maxData.push(salaries[salaries.length - 1]);
        q1Data.push(salaries[Math.floor(salaries.length * 0.25)]);
        q3Data.push(salaries[Math.floor(salaries.length * 0.75)]);
      }
    });

    return {
      categories,
      avgData,
      minData,
      maxData,
      q1Data,
      q3Data,
    };
  }, [salaryByGrade]);

  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter: (params: any) => {
        let result = `<strong>${params[0].axisValue}</strong><br/>`;
        params.forEach((param: any) => {
          result += `${param.marker} ${param.seriesName}: PKR ${param.value.toLocaleString()}<br/>`;
        });
        return result;
      },
    },
    legend: {
      data: ["Average", "Min", "Max", "Q1 (25%)", "Q3 (75%)"],
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
      data: chartData.categories,
      axisLabel: {
        rotate: 45,
        interval: 0,
      },
    },
    yAxis: {
      type: "value",
      name: "Salary (PKR)",
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
          if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
          return value.toString();
        },
      },
    },
    series: [
      {
        name: "Average",
        type: "bar",
        data: chartData.avgData,
        itemStyle: {
          color: "#10b981",
        },
        label: {
          show: false,
        },
      },
      {
        name: "Min",
        type: "line",
        data: chartData.minData,
        lineStyle: {
          type: "dashed",
          width: 2,
        },
        itemStyle: {
          color: "#94a3b8",
        },
      },
      {
        name: "Max",
        type: "line",
        data: chartData.maxData,
        lineStyle: {
          type: "dashed",
          width: 2,
        },
        itemStyle: {
          color: "#ef4444",
        },
      },
      {
        name: "Q1 (25%)",
        type: "line",
        data: chartData.q1Data,
        lineStyle: {
          type: "dotted",
        },
        itemStyle: {
          color: "#8b5cf6",
        },
      },
      {
        name: "Q3 (75%)",
        type: "line",
        data: chartData.q3Data,
        lineStyle: {
          type: "dotted",
        },
        itemStyle: {
          color: "#f59e0b",
        },
      },
    ],
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Compensation Distribution by Grade
      </h3>
      <p className="text-sm text-gray-600 mb-4">
        Shows average, minimum, maximum, and quartile (Q1, Q3) salaries for each grade
      </p>
      <ReactECharts option={option} style={{ height: "450px" }} />
    </div>
  );
}
