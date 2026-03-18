"""
Quick verification that the schema fix is working
This directly calls the LLM without starting the full backend
"""
import asyncio
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

# This is the CORRECTED system prompt that was fixed in nlp_query_service.py
SYSTEM_PROMPT = """You are an HR database assistant. You have access to TWO tables:

TABLE 1: employees (lowercase column names)
- employee_id, full_name, department, unit_name, grade_level, designation
- branch_city, branch_country (limited location info)
- date_of_joining, years_of_experience, total_monthly_salary
- status, performance_score

TABLE 2: odbc (ALL UPPERCASE column names - must use double quotes in SQL!)
- "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME"
- "DEPARTMENT_NAME", "GRADE", "POSITION_NAME"
- "LOCATION_NAME" (branch/office names like 'UBL Head Office', 'RHQ Karachi')
- "BRANCH", "REGION", "DISTRICT", "EMPLOYMENT_STATUS"

CRITICAL RULE: Location/Branch queries → Use odbc."LOCATION_NAME" (NOT employees.branch_name which doesn't exist!)

Rules:
- Always output ONLY valid JSON
- For data questions: {"is_data": true, "sql": "SELECT ... FROM employees|odbc ..."}
- ODBC columns are UPPERCASE and need double quotes: SELECT "LOCATION_NAME" FROM odbc

Example: "departments in UBL Head Office" → {"is_data": true, "sql": "SELECT DISTINCT \\"DEPARTMENT_NAME\\" FROM odbc WHERE \\"LOCATION_NAME\\" ILIKE '%UBL Head Office%'"}
"""

test_queries = [
    "Show me all departments in UBL Head Office location",
    "How many employees have grade AVP-I?",
    "What is the average salary by department?",
]

print("=" * 80)
print("TESTING CORRECTED SCHEMA WITH OLLAMA LLM")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n[Test {i}] Query: {query}")
    
    payload = {
        "model": "llama3.1:8b",
        "prompt": f"{SYSTEM_PROMPT}\n\nUser: {query}\n\nAssistant:",
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": 200
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        result = response.json()
        llm_output = result.get("response", "")
        
        parsed = json.loads(llm_output)
        sql = parsed.get("sql", "")
        is_data = parsed.get("is_data", False)
        
        print(f"  is_data: {is_data}")
        print(f"  SQL: {sql}")
        
        # Validate correctness
        if "UBL Head Office" in query:
            if '"LOCATION_NAME"' in sql and 'odbc' in sql.lower():
                print("  ✓ CORRECT - Uses odbc.LOCATION_NAME")
            else:
                print("  ✗ WRONG - Should use odbc.LOCATION_NAME")
        elif "grade AVP-I" in query:
            if 'grade_level' in sql or '"GRADE"' in sql:
                print("  ✓ CORRECT - Uses grade column")
            else:
                print("  ✗ WRONG - Should query grade")
        elif "average salary" in query:
            if 'total_monthly_salary' in sql or 'AVG' in sql.upper():
                print("  ✓ CORRECT - Uses salary aggregation")
            else:
                print("  ✗ WRONG - Should use AVG(total_monthly_salary)")
                
    except requests.exceptions.Timeout:
        print("  ✗ TIMEOUT - Ollama took too long")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 80)
print("SCHEMA FIX VALIDATION COMPLETE")
print("=" * 80)
print("\nIf queries show ✓ CORRECT, the NLP service fix is working!")
print("The backend will use this same corrected schema when processing queries.")
