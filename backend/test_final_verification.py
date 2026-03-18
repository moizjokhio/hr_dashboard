"""
Final verification test - simulates actual NLP query with new settings
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ml.llm_service import llm_service


def test_sql_generation():
    """Test SQL generation with the exact same prompt used in NLP service"""
    
    system_prompt = """You are an HR database assistant. You have access to TWO tables:

**Table 1: employees**
- Columns: employee_id, first_name, last_name, email, phone_number, hire_date, job_title, salary, department, manager_id, branch_city, grade_level, total_experience_years

**Table 2: odbc**
- Columns: PERSON_ID, FIRST_NAME, LAST_NAME, EMAIL, PHONE_NUMBER, HIRE_DATE, JOB_TITLE, SALARY, DEPARTMENT_NAME, MANAGER_ID, LOCATION_NAME, PERSON_TYPE_MEANING

**Instructions:**
1. Determine if the user's question requires database data or is conversational
2. Return ONLY valid JSON (no markdown, no extra text)

**Format:**
For data queries:
{
  "is_data": true,
  "sql": "SELECT ... FROM employees ..."
}

For conversational queries:
{
  "is_data": false,
  "answer": "Your conversational response here"
}"""

    user_prompt = "What is the average salary by department?"
    
    print("="*80)
    print("Testing NLP Query Flow with Fixed Settings")
    print("="*80)
    print(f"\nModel: qwen2.5-coder:7b")
    print(f"Timeout: 60 seconds (NLP service) + 90 seconds (HTTP)")
    print(f"\nQuery: {user_prompt}")
    print("\nSending request to Ollama...")
    
    try:
        start = time.time()
        response = llm_service.predict(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model="qwen2.5-coder:7b"
        )
        elapsed = time.time() - start
        
        print(f"\n✅ SUCCESS! Response received in {elapsed:.2f} seconds")
        print("\n" + "="*80)
        print("RESPONSE:")
        print("="*80)
        print(response)
        print("="*80)
        
        # Check if it's valid
        if "is_data" in response and "sql" in response:
            print("\n✅ Response contains expected fields (is_data, sql)")
        else:
            print("\n⚠️  Response may need JSON parsing")
        
        # Check timing
        if elapsed < 45:
            print(f"\n✅ Response time ({elapsed:.2f}s) is well under 60s timeout")
            print("🎉 System should work now!")
            return True
        else:
            print(f"\n⚠️  Response time ({elapsed:.2f}s) is close to timeout")
            print("May still work but could be unstable")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_queries():
    """Test a few different query types"""
    
    test_cases = [
        "How many employees are there?",
        "List employees in IT department",
        "Who has the highest salary?",
    ]
    
    print("\n\n" + "="*80)
    print("Testing Multiple Query Types")
    print("="*80)
    
    results = []
    for query in test_cases:
        print(f"\n🔍 Query: {query}")
        start = time.time()
        try:
            response = llm_service.predict(
                prompt=query,
                system_prompt="Generate SQL for this query. Return JSON: {\"is_data\": true, \"sql\": \"...\"}",
                model="qwen2.5-coder:7b"
            )
            elapsed = time.time() - start
            status = "✅" if elapsed < 45 else "⚠️"
            print(f"{status} Response in {elapsed:.2f}s")
            results.append((query, elapsed, True))
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append((query, 0, False))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    successful = sum(1 for _, _, success in results if success)
    avg_time = sum(t for _, t, success in results if success) / max(successful, 1)
    
    print(f"Successful queries: {successful}/{len(test_cases)}")
    print(f"Average response time: {avg_time:.2f}s")
    
    if successful == len(test_cases) and avg_time < 45:
        print("\n🎉 All tests passed! System is ready.")
        return True
    else:
        print("\n⚠️  Some tests failed or were slow")
        return False


if __name__ == "__main__":
    print("\n🔧 Final Verification Test\n")
    
    test1_passed = test_sql_generation()
    test2_passed = test_multiple_queries()
    
    print("\n\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if test1_passed and test2_passed:
        print("✅ All tests passed!")
        print("\n✅ Your system should now work correctly with:")
        print("   - Model: qwen2.5-coder:7b (fast)")
        print("   - Timeout: 60s (adequate)")
        print("   - Expected response time: ~30s")
        print("\n🚀 Try your query again in the frontend!")
    else:
        print("⚠️  Some issues remain:")
        print("   - Model may still be too slow for your hardware")
        print("   - Consider downloading a smaller model:")
        print("     ollama pull qwen2.5-coder:3b")
        print("   - Or use a more powerful machine")
    
    sys.exit(0 if (test1_passed and test2_passed) else 1)
