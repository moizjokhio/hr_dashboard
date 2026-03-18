import requests
import json

# Direct test of Ollama with updated system prompt
url = "http://localhost:11434/api/generate"

system_prompt = """You are an HR database assistant. You have access to TWO tables:

TABLE 1: employees (lowercase column names)
- department, unit_name, grade_level, designation, branch_city, branch_country

TABLE 2: odbc (ALL UPPERCASE column names - must use double quotes in SQL!)
- "EMPLOYEE_NUMBER", "EMPLOYEE_FULL_NAME", "DEPARTMENT_NAME", "GRADE"
- "LOCATION_NAME" (branch/office name like 'UBL Head Office', 'RHQ Karachi')

CRITICAL: Location/Branch queries → Use odbc."LOCATION_NAME" NOT employees.branch_city

Rules:
- Output ONLY valid JSON
- For data questions: {"is_data": true, "sql": "SELECT ... FROM employees|odbc ..."}
- ODBC columns are UPPERCASE and need double quotes: SELECT "LOCATION_NAME" FROM odbc
"""

user_query = "Show me all departments in UBL Head Office location"

payload = {
    "model": "llama3.1:8b",
    "prompt": f"{system_prompt}\n\nUser: {user_query}\n\nAssistant:",
    "stream": False,
    "format": "json"
}

print(f"Testing query: {user_query}\n")
print("Expected SQL: SELECT DISTINCT \"DEPARTMENT_NAME\" FROM odbc WHERE \"LOCATION_NAME\" LIKE '%UBL Head Office%'\n")
print("Calling LLM...")

response = requests.post(url, json=payload, timeout=60)
result = response.json()
llm_output = result.get("response", "")

print(f"\nLLM Response:\n{llm_output}\n")

try:
    parsed = json.loads(llm_output)
    print(f"Parsed JSON:")
    print(f"  is_data: {parsed.get('is_data')}")
    print(f"  sql: {parsed.get('sql')}")
except Exception as e:
    print(f"Parse error: {e}")
