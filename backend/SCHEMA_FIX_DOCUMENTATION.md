# CRITICAL FIX: Database Schema Mismatch

## Problem Discovered
The NLP query service was using an **INCORRECT schema**. The actual database has a completely different structure than what the system prompt described.

## Actual Database Schema

### `employees` table (lowercase column names)
```
- id, employee_id, full_name, department, unit_name, grade_level, designation
- employment_type, status, branch_city, branch_country
- date_of_birth, date_of_joining, years_of_experience
- basic_salary, housing_allowance, transport_allowance, total_monthly_salary
- performance_score, reporting_manager_id
```

**MISSING from employees:** `branch_name`, `branch_region`, `branch_code` - These do NOT exist!

### `odbc` table (ALL UPPERCASE columns - requires double quotes in SQL!)
```sql
- "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "GENDER", "DATE_OF_BIRTH"
- "DEPARTMENT_NAME", "GRADE", "POSITION_NAME", "JOB_NAME"
- "LOCATION_NAME" -- THIS is where branch/office data lives!
- "BRANCH", "REGION", "DISTRICT", "CLUSTERS"
- "EMPLOYMENT_STATUS", "ACTUAL_TERMINATION_DATE", "GROSS_SALARY"
```

## Example Location Data from odbc."LOCATION_NAME"
```
- UBL Ameen, Gulberg Green Residencia Islamabad
- RHQ Karachi
- RHQ Lahore
- Clock Tower Sukkur
- Bahria Town Branch, Lahore
```

## Key Mapping Changes

| User Query | OLD (WRONG) | NEW (CORRECT) |
|------------|-------------|---------------|
| "UBL Head Office location" | `employees.branch_name = 'UBL Head Office'` | `odbc."LOCATION_NAME" LIKE '%UBL Head Office%'` |
| "departments in Lahore" | `employees.department WHERE branch_city = 'Lahore'` | Need to JOIN or use odbc table |
| "grade AVP-I employees" | `employees.grade_level = 'AVP-I'` | `employees.grade_level = 'AVP-I'` OR `odbc."GRADE" = 'AVP-I'` |

## What Was Fixed

### 1. Updated System Prompt (`nlp_query_service.py` lines ~98-140)
- ✅ Added TWO-table schema documentation
- ✅ Emphasized UPPERCASE columns in odbc require double quotes
- ✅ **CRITICAL RULE**: Location/branch queries → Use `odbc."LOCATION_NAME"`
- ✅ Removed non-existent columns (`branch_name`, `job_role`, `hire_date`)
- ✅ Added correct column names (`designation`, `date_of_joining`, `years_of_experience`)

### 2. Updated RAG Context Builder (`nlp_query_service.py` lines ~408-450)
- ✅ Now fetches from BOTH tables
- ✅ Correctly handles UPPERCASE odbc columns with quotes: `"LOCATION_NAME"`
- ✅ Provides actual location values from odbc to LLM

### 3. Updated `_fetch_distinct_values` method
- ✅ Now accepts `table` parameter (employees or odbc)
- ✅ Handles column name with quotes for ODBC

## Testing Status

### Completed:
- ✅ Verified actual database schema (employees has 30 columns, odbc has 77 columns)
- ✅ Confirmed `employees.branch_name` does NOT exist
- ✅ Confirmed `odbc."LOCATION_NAME"` exists with actual branch data
- ✅ Updated system prompt with correct two-table schema
- ✅ Updated RAG context to fetch from both tables

### Pending:
- ⏳ Run test_nlp_standalone.py to verify LLM generates correct SQL
- ⏳ Run comprehensive test suite with 30 queries
- ⏳ Verify location queries now work correctly

## Expected SQL Examples

### Query: "Show me all departments in UBL Head Office location"
**WRONG (old):**
```sql
SELECT department FROM employees WHERE branch_name = 'UBL Head Office'
-- FAILS: column "branch_name" does not exist
```

**CORRECT (new):**
```sql
SELECT DISTINCT "DEPARTMENT_NAME" FROM odbc WHERE "LOCATION_NAME" LIKE '%UBL Head Office%'
-- SUCCESS: Uses actual LOCATION_NAME column with proper quoting
```

### Query: "How many employees in RHQ Karachi?"
**CORRECT:**
```sql
SELECT COUNT(*) FROM odbc WHERE "LOCATION_NAME" LIKE '%RHQ Karachi%'
```

### Query: "Average salary by department"
**CORRECT (employees table has salary):**
```sql
SELECT department, AVG(total_monthly_salary) as avg_salary 
FROM employees 
GROUP BY department
```

## Next Steps

1. **Restart backend** to load updated NLPQueryService code
2. **Run test_nlp_standalone.py** - Should now generate SQL with `odbc."LOCATION_NAME"`
3. **Run comprehensive tests** - Validate all 30 queries work with correct schema
4. **Update RAG dataset** (rag_hr_schema_dataset.jsonl) to reflect actual schema

## Files Modified
- `backend/app/ml/nlp_query_service.py` - System prompt, RAG context, fetch methods
- `backend/test_nlp_standalone.py` - Test harness
- `backend/get_actual_schema.py` - Schema verification script (NEW)
- `backend/check_branch_data.py` - Data verification script (NEW)

## Critical Takeaway
The root cause of ALL query failures was **schema mismatch**. The system was generating SQL for columns that don't exist (`branch_name`) instead of the actual columns (`odbc."LOCATION_NAME"`). This fix aligns the NLP service with the actual PostgreSQL database structure.
