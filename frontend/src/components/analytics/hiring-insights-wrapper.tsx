"use client";

import { useState, useTransition } from "react";
import { getHiringInsights } from "@/app/actions/analytics";

interface HiringInsightsWrapperProps {
  initialData: any;
  children: (data: any, selectedYear: number, setSelectedYear: (year: number) => void, isPending: boolean) => React.ReactNode;
}

export function HiringInsightsWrapper({ initialData, children }: HiringInsightsWrapperProps) {
  const [data, setData] = useState(initialData);
  const [selectedYear, setSelectedYear] = useState(initialData.selectedYear || 2025);
  const [isPending, startTransition] = useTransition();

  const handleYearChange = (year: number) => {
    setSelectedYear(year);
    startTransition(async () => {
      const newData = await getHiringInsights(year);
      setData(newData);
    });
  };

  return <>{children(data, selectedYear, handleYearChange, isPending)}</>;
}
