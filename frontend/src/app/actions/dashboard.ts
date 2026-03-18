'use server';

import pool from '@/lib/db';

export async function getDashboardMetrics() {
  const client = await pool.connect();
  try {
    // 1. Headcount
    const headcountRes = await client.query(
      `SELECT COUNT(*) as count FROM odbc WHERE "EMPLOYMENT_STATUS" LIKE 'Active%'`
    );
    const headcount = parseInt(headcountRes.rows[0].count, 10);

    // 2. Payroll Burn
    const payrollRes = await client.query(
      `SELECT SUM("GROSS_SALARY") as total FROM odbc`
    );
    const payrollBurn = parseFloat(payrollRes.rows[0].total || '0');

    // 3. Attrition Alert (Current Month)
    const attritionRes = await client.query(
      `SELECT COUNT(*) as count FROM odbc WHERE "ACTUAL_TERMINATION_DATE" >= date_trunc('month', current_date)`
    );
    const attrition = parseInt(attritionRes.rows[0].count, 10);

    // 4. Gender Ratio
    const genderRes = await client.query(
      `SELECT "GENDER", COUNT(*) as count FROM odbc GROUP BY "GENDER"`
    );
    const genderRatio = genderRes.rows.map(row => ({
      name: row.GENDER || 'Unknown',
      value: parseInt(row.count, 10)
    }));

    return {
      headcount,
      payrollBurn,
      attrition,
      genderRatio
    };
  } catch {
    return { headcount: 0, payrollBurn: 0, attrition: 0, genderRatio: [] };
  } finally {
    client.release();
  }
}

export async function getWorkflowWidgets() {
  const client = await pool.connect();
  try {
    // 1. Probation Cliff
    // Fetch probations ending in the next 30 days (Future only)
    const probationRes = await client.query(
      `SELECT "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "DATE_PROBATION_END", "DEPARTMENT_NAME" 
       FROM odbc 
       WHERE "DATE_PROBATION_END" >= CURRENT_DATE 
       AND "DATE_PROBATION_END" <= CURRENT_DATE + INTERVAL '30 days'
       AND "CONFIRMED_DATE" IS NULL 
       ORDER BY "DATE_PROBATION_END" ASC
       LIMIT 50`
    );

    // 2. Retirement Radar
    const retirementRes = await client.query(
      `SELECT "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "DATE_OF_BIRTH", "DEPARTMENT_NAME" 
       FROM odbc 
       WHERE "DATE_OF_BIRTH" <= NOW() - INTERVAL '60 years' 
       LIMIT 50`
    );

    // 3. Disciplinary Watch - Recent DA MIS Cases
    const disciplinaryRes = await client.query(
      `SELECT 
         emp_number as "EMPLOYEE_NUMBER",
         name_of_staff_reported as "EMPLOYEE_FULL_NAME",
         misconduct_category as "ACTION_REASON",
         branch_office as "DEPARTMENT_NAME"
       FROM da_mis_cases 
       ORDER BY created_at DESC
       LIMIT 10`
    );

    return {
      probationCliff: probationRes.rows,
      retirementRadar: retirementRes.rows,
      disciplinaryWatch: disciplinaryRes.rows
    };
  } catch {
    return { probationCliff: [], retirementRadar: [], disciplinaryWatch: [] };
  } finally {
    client.release();
  }
}

export async function getOrgStructureMetrics() {
  const client = await pool.connect();
  try {
    // 1. Span of Control
    const spanRes = await client.query(
      `SELECT "MANAGER_EMP_NAME", COUNT(*) as report_count 
       FROM odbc 
       WHERE "MANAGER_EMP_NAME" IS NOT NULL 
       GROUP BY "MANAGER_EMP_NAME" 
       ORDER BY report_count DESC 
       LIMIT 10`
    );

    // 2. Location Heatmap
    const locationRes = await client.query(
      `SELECT "LOCATION_NAME", COUNT(*) as count 
       FROM odbc 
       GROUP BY "LOCATION_NAME"`
    );

    return {
      spanOfControl: spanRes.rows.map(row => ({
        name: row.MANAGER_EMP_NAME,
        value: parseInt(row.report_count, 10)
      })),
      locationHeatmap: locationRes.rows.map(row => ({
        name: row.LOCATION_NAME,
        value: parseInt(row.count, 10)
      }))
    };
  } catch {
    return { spanOfControl: [], locationHeatmap: [] };
  } finally {
    client.release();
  }
}

export async function getCompensationMetrics() {
  const client = await pool.connect();
  try {
    // Salary Distribution by Grade
    // We fetch raw data and let frontend/chart library handle boxplot stats or aggregation
    const salaryRes = await client.query(
      `SELECT "GRADE", "GROSS_SALARY" 
       FROM odbc 
       WHERE "GROSS_SALARY" IS NOT NULL AND "GRADE" IS NOT NULL`
    );

    // Group by Grade for easier consumption
    const salaryByGrade: Record<string, number[]> = {};
    salaryRes.rows.forEach(row => {
      const grade = row.GRADE;
      const salary = parseFloat(row.GROSS_SALARY);
      if (!salaryByGrade[grade]) {
        salaryByGrade[grade] = [];
      }
      salaryByGrade[grade].push(salary);
    });

    return {
      salaryByGrade
    };
  } catch {
    return { salaryByGrade: {} };
  } finally {
    client.release();
  }
}
