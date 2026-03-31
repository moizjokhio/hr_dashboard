'use server';

import pool from '@/lib/db';

function normalizeEmployeeNumber(value: unknown): string {
  const raw = String(value ?? '').trim();
  if (!raw) return '';
  return raw.replace(/\.0+$/, '');
}

function normalizeDepartmentName(value: unknown): string {
  const raw = String(value ?? '').trim();
  if (!raw) return 'Unknown';
  // Remove branch/department numeric prefix like 015219.
  const cleaned = raw.replace(/^\d+\./, '').trim();
  return cleaned || 'Unknown';
}
export async function getDashboardMetrics() {
  let client;
  try {
    client = await pool.connect();
    // 1. Headcount (Active only)
    const headcountRes = await client.query(
      `SELECT COUNT(*) as count FROM odbc WHERE "EMPLOYMENT_STATUS" LIKE 'Active%'`
    );
    const headcount = parseInt(headcountRes.rows[0].count, 10);

    // 1b. Total Headcount (Active + Inactive)
    const totalHeadcountRes = await client.query(
      `SELECT COUNT(*) as count FROM odbc`
    );
    const totalHeadcount = parseInt(totalHeadcountRes.rows[0].count, 10);

    // 2. Payroll Burn (Active only)
    const activePayrollRes = await client.query(
      `SELECT SUM("GROSS_SALARY") as total FROM odbc WHERE "EMPLOYMENT_STATUS" LIKE 'Active%'`
    );
    const activePayrollBurn = parseFloat(activePayrollRes.rows[0].total || '0');

    // 2b. Payroll Burn (All employees)
    const totalPayrollRes = await client.query(
      `SELECT SUM("GROSS_SALARY") as total FROM odbc`
    );
    const totalPayrollBurn = parseFloat(totalPayrollRes.rows[0].total || '0');

    // 3. Attrition Alert (Current Month)
    const attritionRes = await client.query(
      `SELECT COUNT(*) as count FROM odbc WHERE "ACTUAL_TERMINATION_DATE" >= date_trunc('month', current_date)`
    );
    const attrition = parseInt(attritionRes.rows[0].count, 10);

    // 4. Gender Ratio (Active only)
    const activeGenderRes = await client.query(
      `SELECT "GENDER", COUNT(*) as count FROM odbc WHERE "EMPLOYMENT_STATUS" LIKE 'Active%' GROUP BY "GENDER"`
    );
    const activeGenderRatio = activeGenderRes.rows.map(row => ({
      name: row.GENDER || 'Unknown',
      value: parseInt(row.count, 10)
    }));

    // 4b. Gender Ratio (All employees)
    const allGenderRes = await client.query(
      `SELECT "GENDER", COUNT(*) as count FROM odbc GROUP BY "GENDER"`
    );
    const allGenderRatio = allGenderRes.rows.map(row => ({
      name: row.GENDER || 'Unknown',
      value: parseInt(row.count, 10)
    }));

    return {
      headcount,
      totalHeadcount,
      activePayrollBurn,
      totalPayrollBurn,
      attrition,
      activeGenderRatio,
      allGenderRatio
    };
  } catch (error) {
    console.error("Error fetching dashboard metrics:", error);
    if (error instanceof Error) {
      console.error("  Root cause:", error.message);
      if ((error as { code?: string }).code === 'SELF_SIGNED_CERT_IN_CHAIN') {
        console.error("  ⚠️  SSL Certificate validation failed - check frontend database connection settings");
      }
    }
    return {
      headcount: 0,
      totalHeadcount: 0,
      activePayrollBurn: 0,
      totalPayrollBurn: 0,
      attrition: 0,
      activeGenderRatio: [],
      allGenderRatio: []
    };
  } finally {
    if (client) client.release();
  }
}

export async function getWorkflowWidgets() {
  let client;
  try {
    client = await pool.connect();
     // 1. Probation Cliff
     // Fetch probations ending in the next 90 days so UI filters can switch
    const probationRes = await client.query(
      `SELECT "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "DATE_PROBATION_END", "DEPARTMENT_NAME", "EMPLOYMENT_STATUS"
       FROM odbc
       WHERE "CONFIRMED_DATE" IS NULL
       AND LOWER(BTRIM("EMPLOYMENT_STATUS")) = 'active - payroll eligible'
       ORDER BY "DATE_PROBATION_END" ASC NULLS LAST`
    );

    // 2. Retirement Radar
    // Active payroll-eligible employees with DOB for years-left calculations
    const retirementRes = await client.query(
      `SELECT "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "DATE_OF_BIRTH", "DEPARTMENT_NAME", "EMPLOYMENT_STATUS"
       FROM odbc
       WHERE "DATE_OF_BIRTH" IS NOT NULL
       AND LOWER(BTRIM("EMPLOYMENT_STATUS")) = 'active - payroll eligible'
       AND ("DATE_OF_BIRTH" + INTERVAL '60 years') >= CURRENT_DATE
       ORDER BY ("DATE_OF_BIRTH" + INTERVAL '60 years') ASC`
    );

    // 3. Contract Expires
    // Active payroll-eligible employees identified as contract via grade/cadre/type
    const contractExpiresRes = await client.query(
      `SELECT "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "CONTRACT_END_DATE", "DEPARTMENT_NAME", "EMPLOYMENT_STATUS"
       FROM odbc
       WHERE LOWER(BTRIM("EMPLOYMENT_STATUS")) = 'active - payroll eligible'
       AND (
         UPPER(BTRIM(COALESCE("GRADE", ''))) = 'CON'
         OR UPPER(BTRIM(COALESCE("CADRE", ''))) = 'CON'
         OR UPPER(BTRIM(COALESCE("CONTRACT_TYPE", ''))) LIKE 'CON%'
       )
       ORDER BY "CONTRACT_END_DATE" ASC NULLS LAST`
    );

    return {
      probationCliff: probationRes.rows,
      retirementRadar: retirementRes.rows,
      contractExpires: contractExpiresRes.rows
    };
  } catch (error) {
    console.error("Error fetching workflow widgets:", error);
    if (error instanceof Error) {
      console.error("  Root cause:", error.message);
      if ((error as { code?: string }).code === 'SELF_SIGNED_CERT_IN_CHAIN') {
        console.error("  ⚠️  SSL Certificate validation failed - check frontend database connection settings");
      }
    }
    return { probationCliff: [], retirementRadar: [], contractExpires: [] };
  } finally {
    if (client) client.release();
  }
}

export async function getOrgStructureMetrics() {
  let client;
  try {
    client = await pool.connect();
    // 1. Span of Control
    const spanRes = await client.query(
      `WITH manager_counts AS (
         SELECT
           BTRIM(o."MANAGER_EMP_NAME") as manager_name,
           NULLIF(BTRIM(CAST(o."MANAGER_EMP_NO" AS TEXT)), '') as manager_emp_no,
           COUNT(*) as report_count,
           MIN(NULLIF(BTRIM(o."DEPARTMENT_NAME"), '')) as fallback_department
         FROM odbc o
         WHERE NULLIF(BTRIM(o."MANAGER_EMP_NAME"), '') IS NOT NULL
           AND LOWER(BTRIM(o."MANAGER_EMP_NAME")) <> 'nan'
           AND LOWER(BTRIM(o."EMPLOYMENT_STATUS")) = 'active - payroll eligible'
         GROUP BY BTRIM(o."MANAGER_EMP_NAME"), NULLIF(BTRIM(CAST(o."MANAGER_EMP_NO" AS TEXT)), '')
       )
       SELECT
         mc.manager_name as "MANAGER_EMP_NAME",
         mc.manager_emp_no as "MANAGER_EMP_NO",
         mc.report_count,
         COALESCE(NULLIF(BTRIM(mgr."DEPARTMENT_NAME"), ''), mc.fallback_department) as "MANAGER_DEPARTMENT_NAME"
       FROM manager_counts mc
       LEFT JOIN odbc mgr
         ON BTRIM(mgr."EMPLOYEE_NUMBER") = BTRIM(mc.manager_emp_no)
       ORDER BY mc.report_count DESC`
    );

    // 2. Cluster Headcount (Active only, excluding NaN/blank)
    const clusterRes = await client.query(
      `SELECT BTRIM("CLUSTERS") as "CLUSTER_NAME", COUNT(*) as count
       FROM odbc
       WHERE LOWER(BTRIM("EMPLOYMENT_STATUS")) LIKE 'active%'
         AND NULLIF(BTRIM("CLUSTERS"), '') IS NOT NULL
         AND LOWER(BTRIM("CLUSTERS")) <> 'nan'
       GROUP BY BTRIM("CLUSTERS")
       ORDER BY count DESC`
    );

    return {
      spanOfControl: spanRes.rows.map(row => ({
        name: row.MANAGER_EMP_NAME,
        value: parseInt(row.report_count, 10),
        employeeNumber: normalizeEmployeeNumber(row.MANAGER_EMP_NO),
        departmentName: normalizeDepartmentName(row.MANAGER_DEPARTMENT_NAME)
      })),
      locationHeatmap: clusterRes.rows.map(row => ({
        name: row.CLUSTER_NAME,
        value: parseInt(row.count, 10)
      }))
    };
  } catch (error) {
    console.error("Error fetching org structure metrics:", error);
    if (error instanceof Error) {
      console.error("  Root cause:", error.message);
      if ((error as { code?: string }).code === 'SELF_SIGNED_CERT_IN_CHAIN') {
        console.error("  ⚠️  SSL Certificate validation failed - check frontend database connection settings");
      }
    }
    return { spanOfControl: [], locationHeatmap: [] };
  } finally {
    if (client) client.release();
  }
}

export async function getCompensationMetrics() {
  let client;
  try {
    client = await pool.connect();
    // Salary Distribution by Grade
    // We fetch raw data and let frontend/chart library handle boxplot stats or aggregation
    const salaryRes = await client.query(
      `SELECT
         COALESCE(NULLIF(BTRIM("GRADE"), ''), NULLIF(BTRIM("CADRE"), '')) as "GRADE",
         "GROSS_SALARY"
       FROM odbc
       WHERE "GROSS_SALARY" IS NOT NULL
         AND LOWER(BTRIM("EMPLOYMENT_STATUS")) LIKE 'active%'
         AND COALESCE(NULLIF(BTRIM("GRADE"), ''), NULLIF(BTRIM("CADRE"), '')) IS NOT NULL
         AND LOWER(COALESCE(NULLIF(BTRIM("GRADE"), ''), NULLIF(BTRIM("CADRE"), ''))) <> 'nan'`
    );

    // Group by Grade for easier consumption
    const salaryByGrade: Record<string, number[]> = {};
    salaryRes.rows.forEach(row => {
      const grade = String(row.GRADE).trim();
      const salary = parseFloat(row.GROSS_SALARY);
      if (!Number.isFinite(salary)) {
        return;
      }
      if (!salaryByGrade[grade]) {
        salaryByGrade[grade] = [];
      }
      salaryByGrade[grade].push(salary);
    });

    return {
      salaryByGrade
    };
  } catch (error) {
    console.error("Error fetching compensation metrics:", error);
    if (error instanceof Error) {
      console.error("  Root cause:", error.message);
      if ((error as { code?: string }).code === 'SELF_SIGNED_CERT_IN_CHAIN') {
        console.error("  ⚠️  SSL Certificate validation failed - check frontend database connection settings");
      }
    }
    return { salaryByGrade: {} };
  } finally {
    if (client) client.release();
  }
}






