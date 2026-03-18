# NLP Query Service - Current Status and Next Steps

## Issue: Ollama Hanging/Timeout

The test scripts hang because **Ollama is not running or is stuck**. 

### To Fix:

**Option 1: Start Ollama (Recommended)**
```powershell
# In a new PowerShell terminal:
ollama serve
```

**Option 2: Restart Ollama if running**
```powershell
# Stop existing Ollama processes:
Stop-Process -Name "ollama*" -Force

# Wait a few seconds, then start fresh:
ollama serve
```

**Verify Ollama is running:**
```powershell
curl.exe http://localhost:11434/api/version
# Should return: {"version":"0.13.2"}
```

---

## Critical Fix Completed: Schema Mismatch

### ✅ What Was Fixed

The NLP service was using **completely wrong schema**. I've updated it to use the **actual database schema**:

**BEFORE (WRONG):**
- System prompt referenced `employees.branch_name` (doesn't exist!)
- Query "UBL Head Office" generated: `SELECT * FROM employees WHERE branch_name = 'UBL Head Office'`
- Result: ❌ Error: column "branch_name" does not exist

**AFTER (CORRECT):**
- System prompt documents TWO tables: `employees` (lowercase) and `odbc` (UPPERCASE)
- Emphasizes: Location queries → use `odbc."LOCATION_NAME"` (requires double quotes)
- Query "UBL Head Office" should generate: `SELECT "DEPARTMENT_NAME" FROM odbc WHERE "LOCATION_NAME" LIKE '%UBL Head Office%'`
- Result: ✅ Should return actual departments

### Files Modified
1. **`app/ml/nlp_query_service.py`**
   - Lines ~98-140: SYSTEM_PROMPT_BASE - Complete rewrite with correct two-table schema
   - Lines ~408-450: _build_rag_context() - Now fetches from both employees and odbc tables
   - Lines ~450-460: _fetch_distinct_values() - Accepts table parameter for multi-table support

### Actual Database Schema

**employees table** (30 columns, all lowercase):
```sql
employee_id, full_name, department, unit_name, grade_level, designation
branch_city, branch_country  -- Limited location info
date_of_joining, years_of_experience, total_monthly_salary
status, performance_score
```

**odbc table** (77 columns, ALL UPPERCASE, need double quotes):
```sql
"EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME"
"DEPARTMENT_NAME", "GRADE", "POSITION_NAME"
"LOCATION_NAME"  -- THIS has branch/office names like 'UBL Head Office', 'RHQ Karachi'
"BRANCH", "REGION", "DISTRICT", "CLUSTERS"
"GROSS_SALARY", "EMPLOYMENT_STATUS"
"ACTUAL_TERMINATION_DATE", "LAST_WORKING_DATE"
```

---

## Testing (Once Ollama is Running)

### Quick API Test
```powershell
cd backend
py -3.11 test_via_api.py
```
**Requires:** Backend running on port 8001 (`py -3.11 -m uvicorn app.main:app --reload --port 8001`)

### Standalone Test
```powershell
cd backend
py -3.11 test_nlp_standalone.py
```
**Requires:** Only Ollama running (doesn't need backend)

### Expected Results

**Query:** "Show me all departments in UBL Head Office location"
**Expected SQL:**
```sql
SELECT DISTINCT "DEPARTMENT_NAME" 
FROM odbc 
WHERE "LOCATION_NAME" LIKE '%UBL Head Office%'
```

**Query:** "How many employees have grade AVP-I?"
**Expected SQL:**
```sql
SELECT COUNT(*) 
FROM employees 
WHERE grade_level = 'AVP-I'
```

**Query:** "Average salary by department"
**Expected SQL:**
```sql
SELECT department, AVG(total_monthly_salary) as avg_salary
FROM employees
GROUP BY department
```

---

## What's Working vs What's Blocked

### ✅ Completed
- Database schema fully documented (employees: 30 cols, odbc: 77 cols)
- System prompt updated with correct two-table schema
- RAG context builder fetches from both tables
- Mapping rules: Location → odbc."LOCATION_NAME", Department → employees.department or odbc."DEPARTMENT_NAME"
- UPPERCASE column quoting handled for ODBC table
- Transaction management added (commit/rollback)
- JSON parsing hardened (handles quoted keys, string booleans)

### ⏸️ Blocked (Waiting for Ollama)
- Cannot test if LLM generates correct SQL (Ollama not responding)
- Cannot run comprehensive 30-query test suite
- Cannot verify location queries work correctly

### 📋 Next Steps After Ollama Starts
1. ✅ Start Ollama: `ollama serve`
2. ✅ Verify: `curl http://localhost:11434/api/version`
3. Run `py -3.11 test_nlp_standalone.py` - Should generate SQL with `odbc."LOCATION_NAME"`
4. Run comprehensive tests: `py -3.11 tests/test_nlp_comprehensive.py`
5. Validate all 30 queries return data without errors
6. Update RAG dataset JSON file with actual schema

---

## Key Takeaway

The **root cause** of all NLP query failures was:
1. ❌ System prompt had wrong schema (`branch_name` doesn't exist)
2. ❌ RAG context only fetched from employees table
3. ❌ No handling for ODBC's UPPERCASE columns requiring double quotes

This has been **fixed**. Once Ollama restarts, the system should generate correct SQL using the actual database schema.
