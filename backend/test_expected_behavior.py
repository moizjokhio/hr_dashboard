"""
Test the NLP Query Service with correct schema
This validates that queries now use the correct table and columns
"""

print("=" * 80)
print("NLP QUERY SERVICE - EXPECTED BEHAVIOR WITH CORRECTED SCHEMA")
print("=" * 80)

test_cases = [
    {
        "query": "Show me all departments in UBL Head Office location",
        "correct_sql": 'SELECT DISTINCT "DEPARTMENT_NAME" FROM odbc WHERE "LOCATION_NAME" ILIKE \'%UBL Head Office%\'',
        "wrong_sql": "SELECT department FROM employees WHERE branch_name = 'UBL Head Office'",
        "explanation": "Location queries must use odbc.LOCATION_NAME (UPPERCASE, needs quotes), NOT employees.branch_name (doesn't exist)"
    },
    {
        "query": "How many employees in RHQ Karachi?",
        "correct_sql": 'SELECT COUNT(*) FROM odbc WHERE "LOCATION_NAME" ILIKE \'%RHQ Karachi%\'',
        "wrong_sql": "SELECT COUNT(*) FROM employees WHERE branch_name = 'RHQ Karachi'",
        "explanation": "Branch/office names are in odbc.LOCATION_NAME"
    },
    {
        "query": "List all employees with grade AVP-I",
        "correct_sql": "SELECT employee_id, full_name FROM employees WHERE grade_level = 'AVP-I'",
        "wrong_sql": "N/A",
        "explanation": "Grade queries can use employees.grade_level (lowercase, no quotes needed)"
    },
    {
        "query": "What is the average salary by department?",
        "correct_sql": "SELECT department, AVG(total_monthly_salary) as avg_salary FROM employees GROUP BY department",
        "wrong_sql": "SELECT department, AVG(salary) FROM employees GROUP BY department",
        "explanation": "Salary column is total_monthly_salary, not just 'salary'"
    },
    {
        "query": "Show employees in Operations department",
        "correct_sql": "SELECT employee_id, full_name FROM employees WHERE department ILIKE '%Operations%'",
        "wrong_sql": "N/A",
        "explanation": "Department queries use employees.department (lowercase)"
    },
    {
        "query": "Find all terminated employees",
        "correct_sql": "SELECT employee_id, full_name FROM employees WHERE status = 'Terminated'",
        "wrong_sql": "N/A",
        "explanation": "Employment status in employees.status"
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. Query: \"{test['query']}\"")
    print(f"   Explanation: {test['explanation']}")
    print(f"   ✓ CORRECT SQL: {test['correct_sql']}")
    if test['wrong_sql'] != "N/A":
        print(f"   ✗ WRONG SQL:   {test['wrong_sql']}")

print("\n" + "=" * 80)
print("KEY SCHEMA FACTS:")
print("=" * 80)
print("1. Location/Branch data → odbc.\"LOCATION_NAME\" (UPPERCASE, needs double quotes)")
print("2. Department data → employees.department OR odbc.\"DEPARTMENT_NAME\"")
print("3. Grade data → employees.grade_level OR odbc.\"GRADE\"")
print("4. Salary → employees.total_monthly_salary (NOT just 'salary')")
print("5. employees.branch_name does NOT exist (this was the bug!)")
print("\n" + "=" * 80)
print("TO TEST WITH ACTUAL LLM:")
print("=" * 80)
print("1. Start backend: cd backend; python -m uvicorn app.main:app --reload --port 8001")
print("2. Run API test: python test_via_api.py")
print("3. Or use frontend AI chat and check the generated SQL in network tab")
print("=" * 80)
