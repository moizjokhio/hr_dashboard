"use client";

import { Clock, Search, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { type ReactNode, useEffect, useMemo, useState } from "react";

const PROBATION_DAY_OPTIONS = ["15", "30", "45", "60", "75", "90", "180"] as const;
const NUMERIC_DAY_OPTIONS = [15, 30, 45, 60, 75, 90, 180] as const;
const RETIREMENT_YEAR_OPTIONS = ["1", "2", "3", "5", "7", "10"] as const;
const NUMERIC_RETIREMENT_YEAR_OPTIONS = [1, 2, 3, 5, 7, 10] as const;

function toStartOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function getDaysUntil(dateValue?: string) {
  if (!dateValue) return null;

  const target = new Date(dateValue);
  if (Number.isNaN(target.getTime())) return null;

  const todayStart = toStartOfDay(new Date());
  const targetStart = toStartOfDay(target);
  const msPerDay = 1000 * 60 * 60 * 24;

  return Math.ceil((targetStart.getTime() - todayStart.getTime()) / msPerDay);
}

function getYearsUntilRetirement(dateOfBirth?: string, retirementAge = 60) {
  if (!dateOfBirth) return null;

  const dob = new Date(dateOfBirth);
  if (Number.isNaN(dob.getTime())) return null;

  const retirementDate = new Date(dob);
  retirementDate.setFullYear(retirementDate.getFullYear() + retirementAge);

  const todayStart = toStartOfDay(new Date());
  const retirementStart = toStartOfDay(retirementDate);
  const msPerDay = 1000 * 60 * 60 * 24;
  const daysUntil = Math.ceil((retirementStart.getTime() - todayStart.getTime()) / msPerDay);

  return Math.ceil(daysUntil / 365.25);
}

// Year range mappings: key is the filter value, value is [min, max)
const RETIREMENT_YEAR_RANGES: Record<string, [number, number]> = {
  "1": [0, 1],    // 0 to <1 year
  "2": [1, 2],    // 1 to <2 years
  "3": [2, 3],    // 2 to <3 years
  "5": [3, 5],    // 3 to <5 years
  "7": [5, 7],    // 5 to <7 years
  "10": [7, 10],  // 7 to <10 years
} as const;

interface WorkflowItem {
  EMPLOYEE_NUMBER: string;
  EMPLOYEE_FULL_NAME: string;
  DEPARTMENT_NAME?: string;
  DATE_PROBATION_END?: string;
  EMPLOYMENT_STATUS?: string;
  DATE_OF_BIRTH?: string;
  ACTION_REASON?: string;
  CONFIRMED_DATE?: string;
}

interface HRWorkflowProps {
  probationCliff: WorkflowItem[];
  retirementRadar: WorkflowItem[];
  disciplinaryWatch: WorkflowItem[];
}

export function HRWorkflow({
  probationCliff,
  retirementRadar,
  disciplinaryWatch,
}: HRWorkflowProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Probation Cliff */}
      <WorkflowCard
        title="Probation Cliff"
        icon={<Clock className="w-5 h-5 text-amber-600" />}
        description="Probation ending < 30 days"
        items={probationCliff}
        type="probation"
      />

      {/* Retirement Radar */}
      <WorkflowCard
        title="Retirement Radar"
        icon={<UsersIcon className="w-5 h-5 text-blue-600" />}
        description="Retiring within 3 years"
        items={retirementRadar}
        type="retirement"
      />

      {/* Disciplinary Watch */}
      <WorkflowCard
        title="Disciplinary Watch"
        icon={<ShieldAlert className="w-5 h-5 text-red-600" />}
        description="Recent disciplinary actions"
        items={disciplinaryWatch}
        type="disciplinary"
      />
    </div>
  );
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function WorkflowCard({
  title,
  icon,
  description,
  items,
  type,
}: {
  title: string;
  icon: ReactNode;
  description: string;
  items: WorkflowItem[];
  type: "probation" | "retirement" | "disciplinary";
}) {
  const [dayFilter, setDayFilter] = useState<string>("30");
  const [retirementYearFilter, setRetirementYearFilter] = useState<string>("3");
  const [searchTerm, setSearchTerm] = useState("");

  const normalizedSearch = searchTerm.trim().toLowerCase();
  const isNumericPrefix = /^\d+$/.test(normalizedSearch);

  const matchesSearch = (item: WorkflowItem) => {
    if (!normalizedSearch) return true;

    const name = item.EMPLOYEE_FULL_NAME?.toLowerCase() || "";
    const empNo = item.EMPLOYEE_NUMBER?.toLowerCase() || "";

    if (isNumericPrefix) {
      return empNo.startsWith(normalizedSearch);
    }

    return name.includes(normalizedSearch) || empNo.includes(normalizedSearch);
  };

  const probationAll = useMemo(() => {
    if (type !== "probation") return [] as Array<{ item: WorkflowItem; daysUntil: number }>;

    return items
      .map((item) => ({ item, daysUntil: getDaysUntil(item.DATE_PROBATION_END) }))
      .filter((entry): entry is { item: WorkflowItem; daysUntil: number } => entry.daysUntil !== null && entry.daysUntil >= 0)
      .sort((a, b) => a.daysUntil - b.daysUntil);
  }, [items, type]);

  const probationMatches = useMemo(() => {
    if (type !== "probation") return [] as Array<{ item: WorkflowItem; daysUntil: number }>;
    return probationAll.filter(({ item }) => matchesSearch(item));
  }, [probationAll, type, normalizedSearch]);

  const filteredProbation = useMemo(() => {
    if (type !== "probation") return [] as Array<{ item: WorkflowItem; daysUntil: number }>;

    const maxDays = Number(dayFilter);
    return probationMatches.filter((entry) => entry.daysUntil <= maxDays);
  }, [dayFilter, probationMatches, type]);

  useEffect(() => {
    if (type !== "probation") return;
    if (!normalizedSearch || probationMatches.length === 0) return;

    const maxRequiredDays = probationMatches.reduce((maxDays, entry) => Math.max(maxDays, entry.daysUntil), 0);
    if (maxRequiredDays <= Number(dayFilter)) return;

    const nextFilter = NUMERIC_DAY_OPTIONS.find((option) => option >= maxRequiredDays);
    if (nextFilter) {
      const nextValue = String(nextFilter);
      if (nextValue !== dayFilter) {
        setDayFilter(nextValue);
      }
    }
  }, [dayFilter, normalizedSearch, probationMatches, type]);

  const retirementAll = useMemo(() => {
    if (type !== "retirement") return [] as Array<{ item: WorkflowItem; yearsLeft: number }>;

    return items
      .map((item) => ({ item, yearsLeft: getYearsUntilRetirement(item.DATE_OF_BIRTH) }))
      .filter((entry): entry is { item: WorkflowItem; yearsLeft: number } => entry.yearsLeft !== null && entry.yearsLeft >= 0)
      .sort((a, b) => a.yearsLeft - b.yearsLeft);
  }, [items, type]);

  const retirementMatches = useMemo(() => {
    if (type !== "retirement") return [] as Array<{ item: WorkflowItem; yearsLeft: number }>;
    return retirementAll.filter(({ item }) => matchesSearch(item));
  }, [retirementAll, type, normalizedSearch]);

  const filteredRetirement = useMemo(() => {
    if (type !== "retirement") return [] as Array<{ item: WorkflowItem; yearsLeft: number }>;

    const [minYears, maxYears] = RETIREMENT_YEAR_RANGES[retirementYearFilter] || [0, 10];
    return retirementMatches.filter((entry) => entry.yearsLeft >= minYears && entry.yearsLeft < maxYears);
  }, [retirementMatches, retirementYearFilter, type]);

  useEffect(() => {
    if (type !== "retirement") return;
    if (!normalizedSearch || retirementMatches.length === 0) return;

    const maxRequiredYears = retirementMatches.reduce((maxYears, entry) => Math.max(maxYears, entry.yearsLeft), 0);
    
    // Find a year range option that contains the maxRequiredYears
    const currentRange = RETIREMENT_YEAR_RANGES[retirementYearFilter];
    if (currentRange && maxRequiredYears >= currentRange[0] && maxRequiredYears < currentRange[1]) return;

    // Find the first year range that can contain maxRequiredYears
    const nextFilter = Object.entries(RETIREMENT_YEAR_RANGES).find(([_, [min, max]]) => {
      return maxRequiredYears >= min && maxRequiredYears < max;
    })?.[0];

    if (nextFilter && nextFilter !== retirementYearFilter) {
      setRetirementYearFilter(nextFilter);
    }
  }, [normalizedSearch, retirementMatches, retirementYearFilter, type]);

  const rows =
    type === "probation"
      ? filteredProbation.map((entry) => entry.item)
      : type === "retirement"
      ? filteredRetirement.map((entry) => entry.item)
      : items;

  const count =
    type === "probation"
      ? filteredProbation.length
      : type === "retirement"
      ? filteredRetirement.length
      : items.length;

  const effectiveDescription =
    type === "probation"
      ? `Probation ending in <= ${dayFilter} days`
      : type === "retirement"
      ? (() => {
          const [min, max] = RETIREMENT_YEAR_RANGES[retirementYearFilter] || [0, 10];
          return `Retiring ${min}-${max} years from now`;
        })()
      : description;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col h-full">
      <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 rounded-t-xl">
        <div>
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            {icon}
            {title}
          </h3>
          <p className="text-xs text-gray-500 mt-1">{effectiveDescription}</p>
        </div>
        <span className="bg-white px-2 py-1 rounded-md text-xs font-medium border border-gray-200 shadow-sm">
          {count}
        </span>
      </div>

      {type === "probation" || type === "retirement" ? (
        <div className="p-3 border-b border-gray-100 bg-white space-y-2">
          <label className="text-xs text-gray-600 block">
            Search employee
            <div className="mt-1 flex items-center gap-2 rounded-md border border-gray-200 px-2 py-1.5">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Name or employee number"
                className="w-full text-sm outline-none"
              />

              {type === "probation" ? (
                <div className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 pl-2 pr-1 py-1 text-amber-700">
                  <Clock className="w-3.5 h-3.5" />
                  <span className="text-[11px] font-semibold">Days</span>
                  <select
                    value={dayFilter}
                    onChange={(e) => setDayFilter(e.target.value)}
                    className="bg-transparent text-[11px] font-semibold outline-none"
                    aria-label="Filter probation days"
                  >
                    {PROBATION_DAY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}d
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 pl-2 pr-1 py-1 text-blue-700">
                  <Clock className="w-3.5 h-3.5" />
                  <span className="text-[11px] font-semibold">Years</span>
                  <select
                    value={retirementYearFilter}
                    onChange={(e) => setRetirementYearFilter(e.target.value)}
                    className="bg-transparent text-[11px] font-semibold outline-none"
                    aria-label="Filter retirement years"
                  >
                    {RETIREMENT_YEAR_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}y
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </label>
        </div>
      ) : null}

      <div className="flex-1 overflow-auto max-h-[300px] p-0">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-500 uppercase bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-3 font-medium">Employee</th>
              <th className="px-4 py-3 font-medium text-right">
                {type === "probation"
                  ? "End Date"
                  : type === "retirement"
                  ? "Years Left"
                  : "Reason"}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-8 text-center text-gray-400">
                  No records found
                </td>
              </tr>
            ) : (
              rows.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{item.EMPLOYEE_FULL_NAME}</div>
                    <div className="text-xs text-gray-400">{item.EMPLOYEE_NUMBER || "N/A"}</div>
                    <div className="text-xs text-gray-500">{item.DEPARTMENT_NAME || "N/A"}</div>
                  </td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    {type === "probation" ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700">
                        {item.DATE_PROBATION_END
                          ? new Date(item.DATE_PROBATION_END).toLocaleDateString()
                          : "N/A"}
                      </span>
                    ) : type === "retirement" ? (
                      <div className="inline-flex flex-col items-end">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                          {getYearsUntilRetirement(item.DATE_OF_BIRTH) ?? "N/A"}
                          {getYearsUntilRetirement(item.DATE_OF_BIRTH) !== null ? "y left" : ""}
                        </span>
                        <span className="text-[11px] text-gray-500 mt-1">
                          {item.DATE_OF_BIRTH
                            ? new Date(item.DATE_OF_BIRTH).toLocaleDateString()
                            : "N/A"}
                        </span>
                      </div>
                    ) : (
                      <span
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 max-w-[120px] truncate"
                        title={item.ACTION_REASON}
                      >
                        {item.ACTION_REASON}
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="p-3 border-t border-gray-100 bg-gray-50/50 rounded-b-xl text-center">
        <Link
          href={type === "disciplinary" ? "/da-cases" : "/employees"}
          className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors block w-full h-full"
        >
          {type === "disciplinary" ? "View DA Dashboard" : "View All"}
        </Link>
      </div>
    </div>
  );
}

