# Column Name Fix - Action Required

## Problem Identified
Your LLM is generating SQL with incorrect column names:
- Using `Department` instead of `department`
- Using `Salary` instead of `total_monthly_salary`  
- Using `Employees` instead of `employees`
- Adding verbose explanations instead of just JSON

## Root Cause
The system prompt wasn't explicit enough about:
1. Exact column name requirements
2. JSON-only output format
3. Concrete examples showing correct usage

## Changes Made

### 1. Improved System Prompt (`nlp_query_service.py`)
- Added explicit CRITICAL COLUMN MAPPINGS section
- Added concrete EXAMPLES showing exact column names
- Emphasized "NO markdown, NO explanations - ONLY JSON"
- Listed all column names in full at the top

### 2. Stricter LLM Settings (`llm_service.py`)
- Temperature: 0.1 → 0.0 (fully deterministic)
- num_predict: 2000 → 1000 (prevent verbose output)
- Added top_k: 1 (most likely token only)
- Added top_p: 0.1 (minimal sampling)

## How to Apply the Fix

**YOU MUST RESTART THE BACKEND SERVER:**

```powershell
# 1. Stop the current backend (Ctrl+C in the terminal running uvicorn)

# 2. Warm up Ollama (optional but recommended)
cd backend
python warmup_ollama.py

# 3. Restart backend with new code
cd backend
py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Expected Result After Restart

**Before (OLD):**
```
Response: "To calculate the average salary by department..."
SQL: SELECT Department, AVG(Salary) as AverageSalary FROM Employees...
```

**After (NEW):**
```
Response: {"is_data": true, "sql": "SELECT department, AVG(total_monthly_salary) as avg_salary FROM employees GROUP BY department"}
```

## Verification

Once you restart the backend, test with:
```
Query: "What is the average salary by department?"
Expected SQL: SELECT department, AVG(total_monthly_salary) as avg_salary FROM employees GROUP BY department
```

The response should:
✅ Use lowercase `department` (not `Department`)
✅ Use `total_monthly_salary` (not `Salary`)
✅ Use lowercase `employees` (not `Employees`)
✅ Be pure JSON (no markdown, no explanations)

## Important Notes

1. **Restart is REQUIRED** - Changes to Python code don't take effect until server restart
2. **Warm up first** - Run `python warmup_ollama.py` before starting backend
3. **Watch the logs** - The DEBUG lines will show if column names are correct
4. **Test thoroughly** - Try multiple queries to ensure consistent behavior

## Test Script

After restarting, you can run:
```powershell
cd backend
python test_column_names.py
```

This will test multiple queries and verify column name accuracy.

---

**Status**: ⚠️  **Changes made but NOT yet active** - Restart backend to apply!
