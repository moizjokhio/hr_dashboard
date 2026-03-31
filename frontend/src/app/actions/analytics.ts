'use server';

import pool from '@/lib/db';

// Utility function to normalize names by removing number prefixes
function normalizeName(name: string | null): string {
  if (!name) return '';
  // Remove patterns like "012800." or "039038." from the beginning
  return name.replace(/^\d+\./g, '').trim();
}

export async function getHeadcountAnalytics() {
  const client = await pool.connect();
  try {
    // Headcount by Group (normalized names)
    const byGroup = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as name,
         COUNT(*) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DEPT_GROUP" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC`
    );

    // Headcount by Sub-Group (top 15, normalized names)
    const bySubGroup = await client.query(
      `SELECT 
         REGEXP_REPLACE("SUB_GROUP", '^\\d+\\.', '') as name,
         COUNT(*) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "SUB_GROUP" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 15`
    );

    const byGrade = await client.query(
      `SELECT "GRADE" as name, COUNT(*) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
       GROUP BY "GRADE" 
       ORDER BY value DESC`
    );

    const byLocation = await client.query(
      `SELECT "LOCATION_NAME" as name, COUNT(*) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
       GROUP BY "LOCATION_NAME" 
       ORDER BY value DESC`
    );

    return {
      byGroup: byGroup.rows,
      bySubGroup: bySubGroup.rows,
      byGrade: byGrade.rows,
      byLocation: byLocation.rows,
    };
  } finally {
    client.release();
  }
}

export async function getDiversityAnalytics() {
  const client = await pool.connect();
  try {
    const gender = await client.query(
      `SELECT "GENDER" as name, COUNT(*) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
       GROUP BY "GENDER"`
    );

    // Age Distribution
    const age = await client.query(
      `SELECT 
         CASE 
           WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_BIRTH"::date)) < 25 THEN 'Under 25'
           WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_BIRTH"::date)) BETWEEN 25 AND 34 THEN '25-34'
           WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_BIRTH"::date)) BETWEEN 35 AND 44 THEN '35-44'
           WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_BIRTH"::date)) BETWEEN 45 AND 54 THEN '45-54'
           ELSE '55+' 
         END as name,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DATE_OF_BIRTH" IS NOT NULL
       GROUP BY 1
       ORDER BY 1`
    );

    return {
      gender: gender.rows,
      age: age.rows,
    };
  } finally {
    client.release();
  }
}

export async function getCompensationAnalytics() {
  const client = await pool.connect();
  try {
    // Average salary by Group (normalized names)
    const avgByGroup = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as name,
         AVG(0::numeric) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1 AND "DEPT_GROUP" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC`
    );

    const avgByGrade = await client.query(
      `SELECT "GRADE" as name, AVG(0::numeric) as value 
       FROM odbc 
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1
       GROUP BY "GRADE" 
       ORDER BY value DESC`
    );

    return {
      avgByGroup: avgByGroup.rows.map(r => ({ ...r, value: parseFloat(r.value) })),
      avgByGrade: avgByGrade.rows.map(r => ({ ...r, value: parseFloat(r.value) })),
    };
  } finally {
    client.release();
  }
}

export async function getAttritionAnalytics() {
  const client = await pool.connect();
  try {
    // Terminations in the last 12 months
    const trend = await client.query(
      `SELECT TO_CHAR("ACTUAL_TERMINATION_DATE"::date, 'YYYY-MM') as name, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE"::date >= NOW() - INTERVAL '12 months'
       GROUP BY 1
       ORDER BY 1`
    );

    const byReason = await client.query(
      `SELECT "ACTION_REASON" as name, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL
       GROUP BY "ACTION_REASON"
       ORDER BY value DESC
       LIMIT 10`
    );

    return {
      trend: trend.rows,
      byReason: byReason.rows,
    };
  } finally {
    client.release();
  }
}

// ===== NEW DETAILED INSIGHTS =====

export async function getHiringInsights(year: number = 2025) {
  const client = await pool.connect();
  try {
    // Hires by year
    const hiringByYear = await client.query(
      `SELECT EXTRACT(YEAR FROM "DATE_OF_JOIN"::date)::int as year, COUNT(*) as value
       FROM odbc
       WHERE "DATE_OF_JOIN" IS NOT NULL
       GROUP BY 1
       ORDER BY 1 DESC
       LIMIT 10`
    );

    // Hires in selected year
    const hiresInYear = await client.query(
      `SELECT COUNT(*) as total
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1`,
      [year]
    );

    // Hires by month in selected year
    const hiresByMonth = await client.query(
      `SELECT TO_CHAR("DATE_OF_JOIN"::date, 'Mon') as month, 
              EXTRACT(MONTH FROM "DATE_OF_JOIN"::date)::int as month_num,
              COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1
       GROUP BY 1, 2
       ORDER BY 2`,
      [year]
    );

    // Gender breakdown for selected year hires
    const genderHires = await client.query(
      `SELECT "GENDER" as name, COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1
       GROUP BY "GENDER"`,
      [year]
    );

    // Hires by group in selected year
    const groupHires = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as name,
         COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1 AND "DEPT_GROUP" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 10`,
      [year]
    );

    // Hires by grade in selected year
    const gradeHires = await client.query(
      `SELECT "GRADE" as name, COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1
       GROUP BY "GRADE"
       ORDER BY value DESC`,
      [year]
    );

    // Hires by location/region in selected year (normalized)
    const regionHires = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as name,
         COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1 AND "REGION" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 10`,
      [year]
    );

    // Hires by contract type (Permanent/CON) in selected year
    const contractTypeHires = await client.query(
      `SELECT "CONTRACT_TYPE" as name, COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1 AND "CONTRACT_TYPE" IS NOT NULL
       GROUP BY "CONTRACT_TYPE"
       ORDER BY value DESC`,
      [year]
    );

    // Hires by cadre in selected year
    const cadreHires = await client.query(
      `SELECT "CADRE" as name, COUNT(*) as value
       FROM odbc
       WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = $1 AND "CADRE" IS NOT NULL
       GROUP BY "CADRE"
       ORDER BY value DESC`,
      [year]
    );

    // Year-over-Year comparison - Order from oldest to newest (left to right)
    const yoyComparison = await client.query(
      `SELECT 
         EXTRACT(YEAR FROM "DATE_OF_JOIN"::date)::int as year,
         COUNT(*) as total_hires,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_hires,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_hires
       FROM odbc
       WHERE "DATE_OF_JOIN" IS NOT NULL AND EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) >= 2020
       GROUP BY 1
       ORDER BY 1 ASC`
    );

    return {
      hiringByYear: hiringByYear.rows,
      selectedYear: year,
      totalHires2025: parseInt(hiresInYear.rows[0]?.total || '0'),
      hires2025ByMonth: hiresByMonth.rows,
      genderHires2025: genderHires.rows,
      groupHires2025: groupHires.rows,
      gradeHires2025: gradeHires.rows,
      regionHires2025: regionHires.rows,
      contractTypeHires: contractTypeHires.rows,
      cadreHires: cadreHires.rows,
      yoyComparison: yoyComparison.rows,
    };
  } finally {
    client.release();
  }
}

export async function getWorkforceInsights() {
  const client = await pool.connect();
  try {
    // Total active employees
    const totalActive = await client.query(
      `SELECT COUNT(*) as total FROM odbc WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'`
    );

    // Employment status breakdown
    const statusBreakdown = await client.query(
      `SELECT "EMPLOYMENT_STATUS" as name, COUNT(*) as value
       FROM odbc
       GROUP BY "EMPLOYMENT_STATUS"
       ORDER BY value DESC`
    );

    // Contract type breakdown
    const contractType = await client.query(
      `SELECT "CONTRACT_TYPE" as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CONTRACT_TYPE" IS NOT NULL
       GROUP BY "CONTRACT_TYPE"
       ORDER BY value DESC`
    );

    // Tenure distribution (years of service)
    const tenureDistribution = await client.query(
      `SELECT name, value FROM (
         SELECT 
           CASE 
             WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) < 1 THEN 'Less than 1 year'
             WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) BETWEEN 1 AND 2 THEN '1-2 years'
             WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) BETWEEN 3 AND 5 THEN '3-5 years'
             WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) BETWEEN 6 AND 10 THEN '6-10 years'
             WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) BETWEEN 11 AND 20 THEN '11-20 years'
             ELSE '20+ years'
           END as name,
           COUNT(*) as value
         FROM odbc
         WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DATE_OF_JOIN" IS NOT NULL
         GROUP BY 1
       ) sub
       ORDER BY 
         CASE name
           WHEN 'Less than 1 year' THEN 1
           WHEN '1-2 years' THEN 2
           WHEN '3-5 years' THEN 3
           WHEN '6-10 years' THEN 4
           WHEN '11-20 years' THEN 5
           ELSE 6
         END`
    );

    // Average tenure by department
    const avgTenureByDept = await client.query(
      `SELECT "DEPARTMENT_NAME" as name, 
              ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)))::numeric, 1) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DATE_OF_JOIN" IS NOT NULL
       GROUP BY "DEPARTMENT_NAME"
       ORDER BY value DESC
       LIMIT 10`
    );

    // Cadre distribution
    const cadreDistribution = await client.query(
      `SELECT "CADRE" as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CADRE" IS NOT NULL
       GROUP BY "CADRE"
       ORDER BY value DESC`
    );

    // Division breakdown
    const divisionBreakdown = await client.query(
      `SELECT NULL::text as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY NULL::text
       ORDER BY value DESC
       LIMIT 10`
    );

    // Nationality distribution
    const nationalityDistribution = await client.query(
      `SELECT "NATIONALITY" as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "NATIONALITY" IS NOT NULL
       GROUP BY "NATIONALITY"
       ORDER BY value DESC
       LIMIT 10`
    );

    // Religion distribution
    const religionDistribution = await client.query(
      `SELECT NULL::text as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY NULL::text
       ORDER BY value DESC`
    );

    // Marital status distribution
    const maritalStatus = await client.query(
      `SELECT "MARITAL_STATUS" as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "MARITAL_STATUS" IS NOT NULL
       GROUP BY "MARITAL_STATUS"
       ORDER BY value DESC`
    );

    return {
      totalActive: parseInt(totalActive.rows[0]?.total || '0'),
      statusBreakdown: statusBreakdown.rows,
      contractType: contractType.rows,
      tenureDistribution: tenureDistribution.rows,
      avgTenureByDept: avgTenureByDept.rows.map(r => ({ ...r, value: parseFloat(r.value) })),
      cadreDistribution: cadreDistribution.rows,
      divisionBreakdown: divisionBreakdown.rows,
      nationalityDistribution: nationalityDistribution.rows,
      religionDistribution: religionDistribution.rows,
      maritalStatus: maritalStatus.rows,
    };
  } finally {
    client.release();
  }
}

export async function getGeographicInsights() {
  const client = await pool.connect();
  try {
    // By Region - Normalize region names (remove number prefixes and - Sales/Ops suffixes)
    const byRegion = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as name,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "REGION" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC`
    );

    // By District - Normalize names
    const byDistrict = await client.query(
      `SELECT 
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as name,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 15`
    );

    // By Cluster - Normalize names
    const byCluster = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE(
             REGEXP_REPLACE(
               REGEXP_REPLACE(
                 REGEXP_REPLACE(
                   REGEXP_REPLACE(
                     REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', ''),
                     ' -\\s*(Ops|Sales|Operations)$', '', 'i'
                   ),
                   '^(UBL Ameen Cluster|Cluster)\\s+(Sales|Operations)\\s+Office\\s*-\\s*', '\\1 ', 'i'
                 ),
                 '^Cluster\\s+Office\\s*-\\s*', 'Cluster ', 'i'
               ),
               '^Cluster\\s+Rural\\s+Office\\s*-\\s*', 'Cluster Rural ', 'i'
             ),
             '^Cluster\\s+Trade\\s+Business\\s+Office\\s*-\\s*', 'Cluster Trade Business ', 'i'
           ),
           '\\s+', ' ', 'g'
         ) as name,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CLUSTERS" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 10`
    );

    // Branch Level breakdown - Normalize names
    const branchLevel = await client.query(
      `SELECT 
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as name,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY name
       ORDER BY value DESC`
    );

    // Flagship branches
    const flagshipBranches = await client.query(
      `SELECT NULL::text as name, COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY NULL::text
       ORDER BY value DESC`
    );

    // Gender distribution by region (normalized)
    const genderByRegion = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as region,
         "GENDER" as gender,
         COUNT(*) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "REGION" IS NOT NULL
       GROUP BY region, "GENDER"
       ORDER BY region, "GENDER"`
    );

    return {
      byRegion: byRegion.rows,
      byDistrict: byDistrict.rows,
      byCluster: byCluster.rows,
      branchLevel: branchLevel.rows,
      flagshipBranches: flagshipBranches.rows,
      genderByRegion: genderByRegion.rows,
    };
  } finally {
    client.release();
  }
}

export async function getTerminationInsights() {
  const client = await pool.connect();
  try {
    // Terminations by year
    const terminationsByYear = await client.query(
      `SELECT EXTRACT(YEAR FROM "ACTUAL_TERMINATION_DATE"::date)::int as year, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL
       GROUP BY 1
       ORDER BY 1 DESC
       LIMIT 5`
    );

    // Terminations in 2025
    const terminations2025 = await client.query(
      `SELECT COUNT(*) as total
       FROM odbc
       WHERE EXTRACT(YEAR FROM "ACTUAL_TERMINATION_DATE"::date) = 2025`
    );

    // Terminations by group (instead of department) - normalized
    const terminationsByGroup = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as name,
         COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL AND "DEPT_GROUP" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 10`
    );

    // Terminations by reason (detailed)
    const terminationsByReason = await client.query(
      `SELECT "ACTION_REASON" as name, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL AND "ACTION_REASON" IS NOT NULL
       GROUP BY "ACTION_REASON"
       ORDER BY value DESC`
    );

    // Terminations by gender
    const terminationsByGender = await client.query(
      `SELECT "GENDER" as name, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL
       GROUP BY "GENDER"`
    );

    // Average tenure at termination
    const avgTenureAtTermination = await client.query(
      `SELECT 
         ROUND(AVG(EXTRACT(YEAR FROM AGE("ACTUAL_TERMINATION_DATE"::date, "DATE_OF_JOIN"::date)))::numeric, 1) as avg_tenure
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL AND "DATE_OF_JOIN" IS NOT NULL`
    );

    // Terminations by tenure bucket
    const terminationsByTenure = await client.query(
      `SELECT 
         CASE 
           WHEN EXTRACT(YEAR FROM AGE("ACTUAL_TERMINATION_DATE"::date, "DATE_OF_JOIN"::date)) < 1 THEN 'Less than 1 year'
           WHEN EXTRACT(YEAR FROM AGE("ACTUAL_TERMINATION_DATE"::date, "DATE_OF_JOIN"::date)) BETWEEN 1 AND 2 THEN '1-2 years'
           WHEN EXTRACT(YEAR FROM AGE("ACTUAL_TERMINATION_DATE"::date, "DATE_OF_JOIN"::date)) BETWEEN 3 AND 5 THEN '3-5 years'
           WHEN EXTRACT(YEAR FROM AGE("ACTUAL_TERMINATION_DATE"::date, "DATE_OF_JOIN"::date)) BETWEEN 6 AND 10 THEN '6-10 years'
           ELSE '10+ years'
         END as name,
         COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL AND "DATE_OF_JOIN" IS NOT NULL
       GROUP BY 1
       ORDER BY value DESC`
    );

    // Monthly termination trend (last 24 months)
    const monthlyTrend = await client.query(
      `SELECT TO_CHAR("ACTUAL_TERMINATION_DATE"::date, 'YYYY-MM') as name, COUNT(*) as value
       FROM odbc
       WHERE "ACTUAL_TERMINATION_DATE"::date >= NOW() - INTERVAL '24 months'
       GROUP BY 1
       ORDER BY 1`
    );

    return {
      terminationsByYear: terminationsByYear.rows,
      totalTerminations2025: parseInt(terminations2025.rows[0]?.total || '0'),
      terminationsByGroup: terminationsByGroup.rows,
      terminationsByReason: terminationsByReason.rows,
      terminationsByGender: terminationsByGender.rows,
      avgTenureAtTermination: parseFloat(avgTenureAtTermination.rows[0]?.avg_tenure || '0'),
      terminationsByTenure: terminationsByTenure.rows,
      monthlyTrend: monthlyTrend.rows,
    };
  } finally {
    client.release();
  }
}

export async function getCompensationInsights() {
  const client = await pool.connect();
  try {
    // Total payroll
    const totalPayroll = await client.query(
      `SELECT SUM(0::numeric) as total
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1`
    );

    // Average salary
    const avgSalary = await client.query(
      `SELECT AVG(0::numeric) as avg
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1`
    );

    // Salary by gender
    const salaryByGender = await client.query(
      `SELECT "GENDER" as name, 
              AVG(0::numeric) as avg_salary,
              MIN(0::numeric) as min_salary,
              MAX(0::numeric) as max_salary,
              COUNT(*) as count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1
       GROUP BY "GENDER"`
    );

    // Salary distribution buckets
    const salaryDistribution = await client.query(
      `SELECT name, value FROM (
         SELECT 
           CASE 
             WHEN 0::numeric < 50000 THEN 'Under 50K'
             WHEN 0::numeric BETWEEN 50000 AND 100000 THEN '50K-100K'
             WHEN 0::numeric BETWEEN 100001 AND 200000 THEN '100K-200K'
             WHEN 0::numeric BETWEEN 200001 AND 500000 THEN '200K-500K'
             WHEN 0::numeric BETWEEN 500001 AND 1000000 THEN '500K-1M'
             ELSE 'Above 1M'
           END as name,
           COUNT(*) as value
         FROM odbc
         WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1
         GROUP BY 1
       ) sub
       ORDER BY 
         CASE name
           WHEN 'Under 50K' THEN 1
           WHEN '50K-100K' THEN 2
           WHEN '100K-200K' THEN 3
           WHEN '200K-500K' THEN 4
           WHEN '500K-1M' THEN 5
           ELSE 6
         END`
    );

    // Salary by region - normalized
    const salaryByRegion = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as name,
         AVG(0::numeric) as value
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND 1=1 AND "REGION" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
       LIMIT 10`
    );

    // Gratuity and benefits summary
    const benefitsSummary = await client.query(
      `SELECT 
         COUNT(*) FILTER (WHERE "GRATUITY" IS NOT NULL AND "GRATUITY" != '0') as with_gratuity,
         COUNT(*) FILTER (WHERE "PF" IS NOT NULL AND "PF" != '0') as with_pf,
         COUNT(*) FILTER (WHERE "PENSION" IS NOT NULL AND "PENSION" != '0') as with_pension,
         COUNT(*) as total
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'`
    );

    return {
      totalPayroll: parseFloat(totalPayroll.rows[0]?.total || '0'),
      avgSalary: parseFloat(avgSalary.rows[0]?.avg || '0'),
      salaryByGender: salaryByGender.rows.map(r => ({
        ...r,
        avg_salary: parseFloat(r.avg_salary),
        min_salary: parseFloat(r.min_salary),
        max_salary: parseFloat(r.max_salary),
      })),
      salaryDistribution: salaryDistribution.rows,
      salaryByRegion: salaryByRegion.rows.map(r => ({ ...r, value: parseFloat(r.value) })),
      benefitsSummary: benefitsSummary.rows[0],
    };
  } finally {
    client.release();
  }
}

export async function getDeptGroupHierarchy() {
  const client = await pool.connect();
  try {
    // Department Groups with sub-groups (normalized names)
    const deptGroups = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as dept_group,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DEPT_GROUP" IS NOT NULL
       GROUP BY dept_group
       ORDER BY total_count DESC`
    );

    // Sub-groups for each department group (normalized names)
    const subGroups = await client.query(
      `SELECT 
         REGEXP_REPLACE("DEPT_GROUP", '^\\d+\\.', '') as dept_group,
         REGEXP_REPLACE("SUB_GROUP", '^\\d+\\.', '') as sub_group,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "DEPT_GROUP" IS NOT NULL AND "SUB_GROUP" IS NOT NULL
       GROUP BY dept_group, sub_group
       ORDER BY dept_group, total_count DESC`
    );

    return {
      deptGroups: deptGroups.rows,
      subGroups: subGroups.rows,
    };
  } finally {
    client.release();
  }
}

export async function getClusterHierarchy() {
  const client = await pool.connect();
  try {
    const clusters = await client.query(
      `SELECT 
         REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', '') as cluster,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_count,
         COUNT(DISTINCT "BRANCH_LEVEL") as branch_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary,
         ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)))::numeric, 1) as avg_tenure
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CLUSTERS" IS NOT NULL
       GROUP BY cluster
       ORDER BY total_count DESC`
    );

    // Get branch details for each cluster (normalized names)
    const clusterBranches = await client.query(
      `SELECT 
         REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', '') as cluster,
         REGEXP_REPLACE("BRANCH_LEVEL", '^\\d+\\.', '') as branch,
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as branch_level,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CLUSTERS" IS NOT NULL AND "BRANCH_LEVEL" IS NOT NULL
       GROUP BY cluster, branch, branch_level
       ORDER BY cluster, total_count DESC`
    );

    return {
      clusters: clusters.rows,
      clusterBranches: clusterBranches.rows,
    };
  } finally {
    client.release();
  }
}

export async function getRegionHierarchy() {
  const client = await pool.connect();
  try {
    const regions = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as region,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_count,
         COUNT(DISTINCT NULL::text) as district_count,
         COUNT(DISTINCT "BRANCH_LEVEL") as branch_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "REGION" IS NOT NULL
       GROUP BY region
       ORDER BY total_count DESC`
    );

    // Districts within each region (normalized names)
    const regionDistricts = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as region,
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as district,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(DISTINCT "BRANCH_LEVEL") as branch_count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "REGION" IS NOT NULL AND NULL::text IS NOT NULL
       GROUP BY region, district
       ORDER BY region, total_count DESC`
    );

    return {
      regions: regions.rows,
      regionDistricts: regionDistricts.rows,
    };
  } finally {
    client.release();
  }
}

export async function getDivisionHierarchy() {
  const client = await pool.connect();
  try {
    const divisions = await client.query(
      `SELECT 
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as division,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Male' OR "GENDER" = 'M') as male_count,
         COUNT(DISTINCT "DEPARTMENT_NAME") as dept_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary,
         ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)))::numeric, 1) as avg_tenure
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL
       GROUP BY division
       ORDER BY total_count DESC`
    );

    // Departments within each division (normalized names)
    const divisionDepts = await client.query(
      `SELECT 
         REGEXP_REPLACE(NULL::text, '^\\d+\\.', '') as division,
         REGEXP_REPLACE("DEPARTMENT_NAME", '^\\d+\\.', '') as department,
         COUNT(*) as total_count,
         COUNT(*) FILTER (WHERE "GENDER" = 'Female' OR "GENDER" = 'F') as female_count,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND NULL::text IS NOT NULL AND "DEPARTMENT_NAME" IS NOT NULL
       GROUP BY division, department
       ORDER BY division, total_count DESC`
    );

    return {
      divisions: divisions.rows,
      divisionDepts: divisionDepts.rows,
    };
  } finally {
    client.release();
  }
}

export async function getEmployeesBySubGroup(deptGroup: string, subGroup: string) {
  const client = await pool.connect();
  try {
    const employees = await client.query(
      `SELECT 
         "EMPLOYEE_NUMBER",
         "GENDER",
         "DATE_OF_BIRTH",
         "DATE_OF_JOIN",
         "DEPARTMENT_NAME",
         "GRADE",
         "LOCATION_NAME",
         "CONTRACT_TYPE",
         "CADRE",
         0 as "GROSS_SALARY",
         "REGION",
         NULL::text,
         "BRANCH_LEVEL",
         EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_JOIN"::date)) as tenure_years
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
         AND "DEPT_GROUP" = $1 
         AND "SUB_GROUP" = $2
       ORDER BY "DATE_OF_JOIN" DESC`,
      [deptGroup, subGroup]
    );

    return employees.rows;
  } finally {
    client.release();
  }
}

export async function getExecutiveSummary() {
  const client = await pool.connect();
  try {
    // Key metrics - split into separate queries for complex calculations
    const countMetrics = await client.query(
      `SELECT 
         COUNT(*) FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible') as active_employees,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = 2025) as hires_2025,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = 2025 AND ("GENDER" = 'Female' OR "GENDER" = 'F')) as female_hires_2025,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "ACTUAL_TERMINATION_DATE"::date) = 2025) as terminations_2025,
         COUNT(*) FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND ("GENDER" = 'Female' OR "GENDER" = 'F')) as active_females,
         COUNT(*) FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND ("GENDER" = 'Male' OR "GENDER" = 'M')) as active_males,
         COUNT(DISTINCT "DEPT_GROUP") FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible') as groups,
         COUNT(DISTINCT REGEXP_REPLACE(REGEXP_REPLACE("REGION", '^\\d+\\.', ''), ' - (Sales|Ops|Operations)$', '', 'i')) FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "REGION" IS NOT NULL) as regions,
         COUNT(DISTINCT "BRANCH_LEVEL") FILTER (WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible') as branches
       FROM odbc`
    );

    // Average calculations for active employees only
    const avgMetrics = await client.query(
      `SELECT 
         ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, "DATE_OF_BIRTH"::date)))::numeric, 1) as avg_age,
         ROUND(
           AVG(
             GREATEST(0, (CURRENT_DATE - "DATE_OF_JOIN"::date))::numeric / 365.25
           )::numeric,
           1
         ) as avg_tenure,
         ROUND(AVG(0::numeric)::numeric, 0) as avg_salary
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
         AND "DATE_OF_JOIN" IS NOT NULL
         AND "DATE_OF_JOIN"::date <= CURRENT_DATE`
    );

    // Count distinct normalized clusters
    const clustersCount = await client.query(
      `SELECT COUNT(DISTINCT 
         REGEXP_REPLACE(
           REGEXP_REPLACE(
             REGEXP_REPLACE(
               REGEXP_REPLACE(
                 REGEXP_REPLACE(
                   REGEXP_REPLACE(
                     REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', ''),
                     ' -\\s*(Ops|Sales|Operations)$', '', 'i'
                   ),
                   '^(UBL Ameen Cluster|Cluster)\\s+(Sales|Operations)\\s+Office\\s*-\\s*', '\\1 ', 'i'
                 ),
                 '^Cluster\\s+Office\\s*-\\s*', 'Cluster ', 'i'
               ),
               '^Cluster\\s+Rural\\s+Office\\s*-\\s*', 'Cluster Rural ', 'i'
             ),
             '^Cluster\\s+Trade\\s+Business\\s+Office\\s*-\\s*', 'Cluster Trade Business ', 'i'
           ),
           '\\s+', ' ', 'g'
         ) 
       ) as cluster_count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "CLUSTERS" IS NOT NULL`
    );

    // Recent hires (last 30 days)
    const recentHires = await client.query(
      `SELECT COUNT(*) as count
       FROM odbc
       WHERE "DATE_OF_JOIN"::date >= CURRENT_DATE - INTERVAL '30 days'`
    );

    // Headcount change year over year
    const headcountChange = await client.query(
      `SELECT 
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = 2025) as hires_2025,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "DATE_OF_JOIN"::date) = 2024) as hires_2024,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "ACTUAL_TERMINATION_DATE"::date) = 2025) as terms_2025,
         COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM "ACTUAL_TERMINATION_DATE"::date) = 2024) as terms_2024
       FROM odbc`
    );

    const m = countMetrics.rows[0];
    const avg = avgMetrics.rows[0];
    const hc = headcountChange.rows[0];
    const c = clustersCount.rows[0];
    
    return {
      activeEmployees: parseInt(m.active_employees || '0'),
      hires2025: parseInt(m.hires_2025 || '0'),
      femaleHires2025: parseInt(m.female_hires_2025 || '0'),
      terminations2025: parseInt(m.terminations_2025 || '0'),
      activeFemales: parseInt(m.active_females || '0'),
      activeMales: parseInt(m.active_males || '0'),
      avgAge: parseFloat(avg.avg_age || '0'),
      avgTenure: parseFloat(avg.avg_tenure || '0'),
      avgSalary: parseFloat(avg.avg_salary || '0'),
      groups: parseInt(m.groups || '0'),
      regions: parseInt(m.regions || '0'),
      branches: parseInt(m.branches || '0'),
      clusters: parseInt(c.cluster_count || '0'),
      recentHires: parseInt(recentHires.rows[0]?.count || '0'),
      netHeadcount2025: parseInt(hc.hires_2025 || '0') - parseInt(hc.terms_2025 || '0'),
      netHeadcount2024: parseInt(hc.hires_2024 || '0') - parseInt(hc.terms_2024 || '0'),
      hireGrowthRate: hc.hires_2024 > 0 ? ((parseInt(hc.hires_2025 || '0') - parseInt(hc.hires_2024 || '0')) / parseInt(hc.hires_2024 || '1') * 100).toFixed(1) : '0',
    };
  } finally {
    client.release();
  }
}

export async function getBranchManagerAnalytics() {
  const client = await pool.connect();
  try {
    // Get all active branches (using LOCATION_NAME as it's most reliable)
    const allBranches = await client.query(
      `SELECT DISTINCT "LOCATION_NAME" as branch
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' AND "LOCATION_NAME" IS NOT NULL
       ORDER BY "LOCATION_NAME"`
    );

    // Get branches with Branch Managers (BM)
    const branchesWithBM = await client.query(
      `SELECT DISTINCT "LOCATION_NAME" as branch
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
         AND "POSITION_NAME" LIKE '%Branch Manager%'
         AND "LOCATION_NAME" IS NOT NULL`
    );

    // Get branches with Branch Operations Manager (BOM)
    const branchesWithBOM = await client.query(
      `SELECT DISTINCT "LOCATION_NAME" as branch
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
         AND "POSITION_NAME" LIKE '%Branch Operations Manager%'
         AND "LOCATION_NAME" IS NOT NULL`
    );

    const allBranchSet = new Set(allBranches.rows.map(r => r.branch));
    const bmBranchSet = new Set(branchesWithBM.rows.map(r => r.branch));
    const bomBranchSet = new Set(branchesWithBOM.rows.map(r => r.branch));

    // Calculate branches without BM, without BOM, and without both
    const branchesWithoutBM = Array.from(allBranchSet).filter(b => !bmBranchSet.has(b));
    const branchesWithoutBOM = Array.from(allBranchSet).filter(b => !bomBranchSet.has(b));
    const branchesWithoutBoth = branchesWithoutBM.filter(b => !bomBranchSet.has(b));

    // Get BM count by cluster
    const bmByCluster = await client.query(
      `SELECT 
         REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', '') as cluster,
         COUNT(*) as bm_count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
         AND "POSITION_NAME" LIKE '%Branch Manager%'
         AND "CLUSTERS" IS NOT NULL
       GROUP BY cluster
       ORDER BY bm_count DESC`
    );

    // Get BM count by region (normalized)
    const bmByRegion = await client.query(
      `SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
           ' - (Sales|Ops|Operations)$', '', 'i'
         ) as region,
         COUNT(*) as bm_count
       FROM odbc
       WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
         AND "POSITION_NAME" LIKE '%Branch Manager%'
         AND "REGION" IS NOT NULL
       GROUP BY region
       ORDER BY bm_count DESC`
    );

    return {
      totalBranches: allBranches.rows.length,
      branchesWithBM: branchesWithBM.rows.length,
      branchesWithBOM: branchesWithBOM.rows.length,
      branchesWithoutBM: branchesWithoutBM.length,
      branchesWithoutBOM: branchesWithoutBOM.length,
      branchesWithoutBoth: branchesWithoutBoth.length,
      branchesWithoutBMList: branchesWithoutBM.slice(0, 20), // Top 20 for display
      branchesWithoutBOMList: branchesWithoutBOM.slice(0, 20),
      branchesWithoutBothList: branchesWithoutBoth.slice(0, 20),
      bmByCluster: bmByCluster.rows,
      bmByRegion: bmByRegion.rows,
    };
  } finally {
    client.release();
  }
}
