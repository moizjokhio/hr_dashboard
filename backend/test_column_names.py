"""
Test the improved system prompt for correct column name generation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ml.llm_service import llm_service


def test_salary_query():
    """Test that the model uses correct column names"""
    
    system_prompt = """You are an HR database SQL generator. Generate ONLY valid JSON, NO explanations, NO markdown, NO extra text.

DATABASE SCHEMA:

TABLE: employees (use lowercase column names without quotes)
Columns: id, employee_id, full_name, department, unit_name, grade_level, designation, employment_type, status, branch_city, branch_country, date_of_birth, date_of_joining, years_of_experience, gender, marital_status, religion, education_level, basic_salary, housing_allowance, transport_allowance, other_allowances, total_monthly_salary, performance_score, reporting_manager_id, email, phone, created_at, updated_at

CRITICAL COLUMN MAPPINGS (use EXACT names):
- Salary → employees.total_monthly_salary OR employees.basic_salary
- Department → employees.department
- Employee Name → employees.full_name

OUTPUT FORMAT (respond with ONLY this JSON, nothing else):
For data queries: {"is_data": true, "sql": "SELECT exact_column_name FROM table_name WHERE ..."}

EXAMPLES:
Q: "average salary by department"
A: {"is_data": true, "sql": "SELECT department, AVG(total_monthly_salary) as avg_salary FROM employees GROUP BY department"}

Q: "count employees in IT"
A: {"is_data": true, "sql": "SELECT COUNT(*) as count FROM employees WHERE department = 'IT'"}

RULES:
- Use EXACT column names from schema (total_monthly_salary NOT salary, department NOT Department)
- NO markdown, NO code blocks, NO explanations - ONLY JSON
- For employees table: lowercase without quotes
"""

    test_cases = [
        ("What is the average salary by department?", "total_monthly_salary", "department"),
        ("Count employees in each department", "COUNT", "department"),
        ("List all employees with their salaries", "full_name", "total_monthly_salary"),
        ("Show me the highest paid employee", "total_monthly_salary", "full_name"),
    ]
    
    print("="*80)
    print("Testing Column Name Accuracy")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for query, expected_col1, expected_col2 in test_cases:
        print(f"\n🔍 Query: {query}")
        print(f"   Expected columns: {expected_col1}, {expected_col2}")
        
        try:
            response = llm_service.predict(
                prompt=query,
                system_prompt=system_prompt,
                model="qwen2.5-coder:7b"
            )
            
            print(f"   Response: {response[:200]}")
            
            # Check for correct column names (case-insensitive)
            response_lower = response.lower()
            has_col1 = expected_col1.lower() in response_lower
            has_col2 = expected_col2.lower() in response_lower
            
            # Check for WRONG column names
            has_wrong_salary = "salary" in response_lower and "total_monthly_salary" not in response_lower
            has_capitalized = "Department" in response or "Salary" in response
            has_markdown = "```" in response
            has_explanation = len(response) > 300 or "To calculate" in response or "This query" in response
            
            if has_markdown:
                print("   ⚠️  WARNING: Response contains markdown code blocks")
            if has_explanation:
                print("   ⚠️  WARNING: Response contains explanations (too verbose)")
            if has_wrong_salary:
                print("   ❌ ERROR: Using 'Salary' instead of 'total_monthly_salary'")
            if has_capitalized:
                print("   ❌ ERROR: Using capitalized column names")
            
            if has_col1 and has_col2 and not has_wrong_salary and not has_capitalized:
                print("   ✅ PASS: Correct column names used")
                passed += 1
            else:
                print("   ❌ FAIL: Incorrect column names")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    
    if passed == len(test_cases):
        print("\n✅ All tests passed! Column names are correct.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Model needs more specific instructions.")
        return False


if __name__ == "__main__":
    success = test_salary_query()
    sys.exit(0 if success else 1)
