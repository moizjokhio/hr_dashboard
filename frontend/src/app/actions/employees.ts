"use server";

import { Pool } from "pg";

const pool = new Pool({
  user: process.env.DB_USER || "postgres",
  host: process.env.DB_HOST || "localhost",
  database: process.env.DB_NAME || "hr_analytics",
  password: process.env.DB_PASSWORD || "postgres",
  port: parseInt(process.env.DB_PORT || "5432"),
});

interface GetEmployeesParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  filters?: {
    departments?: string[];
    grades?: string[];
    countries?: string[];
    statuses?: string[];
    search_term?: string;
  };
}

export async function getEmployees({
  page = 1,
  pageSize = 10,
  sortBy = "employee_id",
  sortOrder = "asc",
  filters = {},
}: GetEmployeesParams) {
  const offset = (page - 1) * pageSize;
  const conditions: string[] = [];
  const values: any[] = [];
  let paramIndex = 1;

  // Helper to add condition
  const addCondition = (condition: string, value?: any) => {
    if (value !== undefined) {
      conditions.push(condition.replace("$", `$${paramIndex}`));
      values.push(value);
      paramIndex++;
    } else {
      conditions.push(condition);
    }
  };

  // Apply filters
  if (filters.departments?.length) {
    const placeholders = filters.departments.map((_, i) => `$${paramIndex + i}`).join(", ");
    conditions.push(`"DEPARTMENT_NAME" IN (${placeholders})`);
    values.push(...filters.departments);
    paramIndex += filters.departments.length;
  }

  if (filters.grades?.length) {
    const placeholders = filters.grades.map((_, i) => `$${paramIndex + i}`).join(", ");
    conditions.push(`"GRADE" IN (${placeholders})`);
    values.push(...filters.grades);
    paramIndex += filters.grades.length;
  }

  if (filters.countries?.length) {
    const placeholders = filters.countries.map((_, i) => `$${paramIndex + i}`).join(", ");
    conditions.push(`"LOCATION_NAME" IN (${placeholders})`);
    values.push(...filters.countries);
    paramIndex += filters.countries.length;
  }

  if (filters.statuses?.length) {
    const placeholders = filters.statuses.map((_, i) => `$${paramIndex + i}`).join(", ");
    conditions.push(`"EMPLOYMENT_STATUS" IN (${placeholders})`);
    values.push(...filters.statuses);
    paramIndex += filters.statuses.length;
  }

  if (filters.search_term) {
    conditions.push(`(
      "EMPLOYEE_FULL_NAME" ILIKE $${paramIndex} OR 
      "EMPLOYEE_NUMBER" ILIKE $${paramIndex} OR 
      "EMAIL_ADDRESS" ILIKE $${paramIndex} OR
      "GRADE" ILIKE $${paramIndex} OR
      "DEPARTMENT_NAME" ILIKE $${paramIndex}
    )`);
    values.push(`%${filters.search_term}%`);
    paramIndex++;
  }

  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

  // Map frontend sort keys to DB columns
  const sortMap: Record<string, string> = {
    employee_id: '"EMPLOYEE_NUMBER"',
    full_name: '"EMPLOYEE_FULL_NAME"',
    department: '"DEPARTMENT_NAME"',
    grade_level: '"GRADE"',
    designation: '"POSITION_NAME"',
    branch_city: '"LOCATION_NAME"',
    branch_country: '"LOCATION_NAME"',
    total_monthly_salary: '"GROSS_SALARY"',
    performance_score: '"EMPLOYEE_NUMBER"', // Fallback
    status: '"EMPLOYMENT_STATUS"',
  };

  const dbSortColumn = sortMap[sortBy] || '"EMPLOYEE_NUMBER"';

  try {
    // Get total count
    const countQuery = `SELECT COUNT(*) FROM odbc ${whereClause}`;
    const countResult = await pool.query(countQuery, values);
    const total = parseInt(countResult.rows[0].count);

    // Get data
    const dataQuery = `
      SELECT 
        "EMPLOYEE_NUMBER" as employee_id,
        "EMPLOYEE_FULL_NAME" as full_name,
        "DEPARTMENT_NAME" as department,
        "GRADE" as grade_level,
        "POSITION_NAME" as designation,
        "LOCATION_NAME" as branch_city,
        "LOCATION_NAME" as branch_country,
        "GROSS_SALARY" as total_monthly_salary,
        0 as performance_score,
        "EMPLOYMENT_STATUS" as status,
        "EMAIL_ADDRESS" as email
      FROM odbc
      ${whereClause}
      ORDER BY ${dbSortColumn} ${sortOrder.toUpperCase()}
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    const dataResult = await pool.query(dataQuery, [...values, pageSize, offset]);

    return {
      data: dataResult.rows,
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize),
    };
  } catch (error) {
    console.error("Error fetching employees:", error);
    throw new Error("Failed to fetch employees");
  }
}

export async function getFilterOptions() {
  try {
    const queries = {
      departments: 'SELECT DISTINCT "DEPARTMENT_NAME" FROM odbc ORDER BY "DEPARTMENT_NAME"',
      grades: 'SELECT DISTINCT "GRADE" FROM odbc ORDER BY "GRADE"',
      countries: 'SELECT DISTINCT "LOCATION_NAME" FROM odbc ORDER BY "LOCATION_NAME"',
      statuses: 'SELECT DISTINCT "EMPLOYMENT_STATUS" FROM odbc ORDER BY "EMPLOYMENT_STATUS"',
    };

    const [deptRes, gradeRes, countryRes, statusRes] = await Promise.all([
      pool.query(queries.departments),
      pool.query(queries.grades),
      pool.query(queries.countries),
      pool.query(queries.statuses),
    ]);

    return {
      departments: deptRes.rows.map(r => r.DEPARTMENT_NAME).filter(Boolean),
      grades: gradeRes.rows.map(r => r.GRADE).filter(Boolean),
      countries: countryRes.rows.map(r => r.LOCATION_NAME).filter(Boolean),
      statuses: statusRes.rows.map(r => r.EMPLOYMENT_STATUS).filter(Boolean),
    };
  } catch (error) {
    console.error("Error fetching filter options:", error);
    return {
      departments: [],
      grades: [],
      countries: [],
      statuses: [],
    };
  }
}
