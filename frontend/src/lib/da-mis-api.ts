/**
 * DA MIS Cases API Client
 * Type-safe API functions for DA MIS Cases dashboard
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface DAMISCase {
  id: number;
  'Case #': string;
  'S #'?: string;
  'Emp. #'?: string;
  'Name of Staff Reported'?: string;
  'Grade'?: string;
  'FT'?: string;
  'Branch / Office'?: string;
  'Region'?: string;
  'Cluster'?: string;
  'Fixation of Responsibility'?: string;
  'Misconduct'?: string;
  'Misconduct Category'?: string;
  'Case Revieved'?: string;
  'Case Received from Audit'?: string;
  'Charge Sheeted Date'?: string;
  'DAC Decision'?: string;
  'Punishment Implementation'?: string;
  'Punishment Letter'?: string;
  'Year'?: number;
  'Quarter'?: string;
  'Month'?: string;
  created_at: string;
  updated_at: string;
}

export interface DAMISFilters {
  year?: number;
  quarter?: string;
  month?: string;
  cluster?: string;
  region?: string;
  branch_office?: string;
  grade?: string;
  misconduct_category?: string;
  dac_decision?: string;
  punishment_implementation?: string;
  ft?: string;
  search?: string;
}

export interface DAMISCaseList {
  total: number;
  cases: DAMISCase[];
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardSummary {
  total_cases: number;
  total_people_involved: number;
  cases_by_year: Record<number, number>;
  cases_by_cluster: Record<string, number>;
  cases_by_grade: Record<string, number>;
  top_misconduct_categories: Array<{ category: string; count: number }>;
  pending_decisions: number;
  completion_rate: number;
}

export interface LocationHierarchyData {
  level: string;
  data: Array<{ name: string; count: number }>;
  total: number;
}

export interface MisconductAnalysis {
  most_common_categories: Array<{ category: string; count: number }>;
  most_severe_misconducts: Array<{ misconduct: string; punishment: string; count: number }>;
  grade_breakdown: Record<string, number>;
  ft_breakdown: Record<string, number>;
  repeat_vs_first_time: Record<string, any>;
}

export interface ProcessFairness {
  lifecycle_funnel: Array<{ stage: string; count: number }>;
  sla_delays: Array<any>;
  pending_decisions: number;
  missing_punishment_letters: number;
}

export interface FilterOptions {
  years: number[];
  quarters: string[];
  months: string[];
  clusters: string[];
  regions: string[];
  grades: string[];
  misconduct_categories: string[];
  dac_decisions: string[];
}

/**
 * Get paginated list of DA MIS cases
 */
export async function getCases(
  page: number = 1,
  page_size: number = 50,
  filters?: DAMISFilters
): Promise<DAMISCaseList> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: page_size.toString(),
  });

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE_URL}/da-mis/cases?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch cases');
  }

  return response.json();
}

/**
 * Get specific case by ID
 */
export async function getCaseById(caseId: number): Promise<DAMISCase> {
  const response = await fetch(`${API_BASE_URL}/da-mis/cases/${caseId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch case');
  }

  return response.json();
}

/**
 * Get dashboard summary statistics
 */
export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await fetch(`${API_BASE_URL}/da-mis/summary`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch dashboard summary');
  }

  return response.json();
}

/**
 * Get location hierarchy data (cluster/region/branch)
 */
export async function getLocationHierarchy(
  level: 'cluster' | 'region' | 'branch',
  metric: 'case_count' | 'people_count' = 'case_count',
  filters?: {
    parent_cluster?: string;
    parent_region?: string;
    year?: number;
    quarter?: string;
  }
): Promise<LocationHierarchyData> {
  const params = new URLSearchParams({
    level,
    metric,
  });

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE_URL}/da-mis/location-hierarchy?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch location hierarchy');
  }

  return response.json();
}

/**
 * Get misconduct analysis
 */
export async function getMisconductAnalysis(
  filters?: { year?: number; cluster?: string }
): Promise<MisconductAnalysis> {
  const params = new URLSearchParams();

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
  }

  const response = await fetch(`${API_BASE_URL}/da-mis/misconduct-analysis?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch misconduct analysis');
  }

  return response.json();
}

/**
 * Get HR process fairness metrics
 */
export async function getProcessFairness(
  filters?: { year?: number }
): Promise<ProcessFairness> {
  const params = new URLSearchParams();

  if (filters?.year) {
    params.append('year', filters.year.toString());
  }

  const response = await fetch(`${API_BASE_URL}/da-mis/process-fairness?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch process fairness');
  }

  return response.json();
}

/**
 * Get available filter options
 */
export async function getFilterOptions(): Promise<FilterOptions> {
  const response = await fetch(`${API_BASE_URL}/da-mis/filters/options`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch filter options');
  }

  return response.json();
}
