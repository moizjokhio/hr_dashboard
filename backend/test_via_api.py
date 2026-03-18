"""Test NLP service via FastAPI endpoint (backend must be running on port 8001)"""
import requests
import json

API_URL = "http://localhost:8001/api/v1/ai/query"

test_queries = [
    {
        "query": "Show me all departments in UBL Head Office location",
        "expected_table": "odbc",
        "expected_column": "LOCATION_NAME"
    },
    {
        "query": "How many employees have grade AVP-I?",
        "expected_table": "employees",
        "expected_column": "grade_level"
    },
    {
        "query": "What is the average salary by department?",
        "expected_table": "employees",
        "expected_column": "total_monthly_salary"
    },
]

print("=" * 80)
print("TESTING NLP QUERIES VIA API (backend must be running)")
print("=" * 80)

for i, test in enumerate(test_queries, 1):
    print(f"\n[{i}] Query: {test['query']}")
    print(f"    Expected table: {test['expected_table']}, column: {test['expected_column']}")
    
    try:
        response = requests.post(
            API_URL,
            json={"query": test["query"]},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            sql = data.get("generated_sql", {}).get("raw_sql", "")
            row_count = data.get("row_count", 0)
            
            print(f"    ✓ Success: {success}")
            print(f"    SQL: {sql}")
            print(f"    Rows: {row_count}")
            
            # Validate expected table/column in SQL
            if test["expected_table"] in sql.lower():
                print(f"    ✓ Correct table: {test['expected_table']}")
            else:
                print(f"    ✗ WRONG TABLE - expected {test['expected_table']} in SQL")
                
        else:
            print(f"    ✗ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"    ✗ TIMEOUT - Ollama might be stuck")
    except Exception as e:
        print(f"    ✗ Error: {e}")

print("\n" + "=" * 80)
print("If backend is not running, start it with:")
print("  cd backend")
print("  py -3.11 -m uvicorn app.main:app --reload --port 8001")
print("=" * 80)
