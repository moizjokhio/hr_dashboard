import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

export function formatPercentage(value: number, fractionDigits: number = 1): string {
  const numeric = Number.isFinite(value) ? value : 0;
  return `${numeric.toFixed(fractionDigits)}%`;
}

export function getGradeColor(grade: string | null | undefined): string {
  const g = (grade || "").toLowerCase();
  if (!g) return "#6b7280"; // gray
  if (g.includes("og-1")) return "#60a5fa"; // blue-400
  if (g.includes("og-2")) return "#34d399"; // green-400
  if (g.includes("og-3")) return "#f59e0b"; // amber-500
  if (g.includes("og-4")) return "#ef4444"; // red-500
  if (g.includes("avp")) return "#8b5cf6"; // purple-500
  if (g.includes("vp")) return "#0891b2"; // teal-600
  return "#6b7280"; // default gray-500
}

export function getPerformanceColor(score: number | null | undefined): string {
  const s = Number(score || 0);
  if (s >= 4.0) return "#16a34a"; // green-600
  if (s >= 3.0) return "#f59e0b"; // amber-500
  if (s > 0) return "#ef4444"; // red-500
  return "#9ca3af"; // neutral gray
}
