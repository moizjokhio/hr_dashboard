"""
Test Ollama response timing to diagnose timeout issues
"""
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ml.llm_service import llm_service


def test_ollama_timing():
    """Test Ollama response time with different prompts"""
    
    # Test 1: Simple prompt (should be very fast)
    print("=" * 80)
    print("Test 1: Simple prompt (should be fast)")
    print("=" * 80)
    start = time.time()
    response = llm_service.predict(prompt="Say hello in one word")
    elapsed = time.time() - start
    print(f"Response: {response[:100]}")
    print(f"⏱️  Time taken: {elapsed:.2f} seconds")
    
    if elapsed > 30:
        print("⚠️  WARNING: Simple prompt took > 30 seconds!")
    elif elapsed > 10:
        print("⚠️  WARNING: Simple prompt took > 10 seconds (should be < 5s)")
    else:
        print("✅ Response time is acceptable")
    
    # Test 2: Complex SQL generation prompt (mimics actual use case)
    print("\n" + "=" * 80)
    print("Test 2: SQL generation prompt (like actual query)")
    print("=" * 80)
    
    system_prompt = """You are an HR database assistant. You have access to TWO tables:

**Table 1: employees**
- Columns: employee_id, first_name, last_name, email, phone_number, hire_date, job_title, salary, department, manager_id, branch_city, grade_level, total_experience_years

**Table 2: odbc**
- Columns: PERSON_ID, FIRST_NAME, LAST_NAME, EMAIL, PHONE_NUMBER, HIRE_DATE, JOB_TITLE, SALARY, DEPARTMENT_NAME, MANAGER_ID, LOCATION_NAME, PERSON_TYPE_MEANING

Return ONLY valid JSON with no markdown or extra text:
{
  "is_data": true,
  "sql": "SELECT ... FROM employees ..."
}"""

    user_prompt = "What is the average salary by department?"
    
    start = time.time()
    response = llm_service.predict(
        prompt=user_prompt, 
        system_prompt=system_prompt,
        model="llama3.1:8b"
    )
    elapsed = time.time() - start
    
    print(f"Response: {response[:200]}")
    print(f"⏱️  Time taken: {elapsed:.2f} seconds")
    
    if elapsed > 60:
        print("❌ FAILURE: Response took > 60 seconds (exceeds timeout)")
        return False
    elif elapsed > 45:
        print("⚠️  WARNING: Response took > 45 seconds (may timeout in NLP service)")
    elif elapsed > 30:
        print("⚠️  WARNING: Response took > 30 seconds (slower than expected)")
    else:
        print("✅ Response time is acceptable")
        return True
    
    # Test 3: Check if model is loaded in memory
    print("\n" + "=" * 80)
    print("Test 3: Quick repeat test (should be faster if model is loaded)")
    print("=" * 80)
    
    start = time.time()
    response = llm_service.predict(prompt="Count to 3")
    elapsed = time.time() - start
    print(f"Response: {response[:100]}")
    print(f"⏱️  Time taken: {elapsed:.2f} seconds")
    
    if elapsed < 5:
        print("✅ Model is loaded and responding quickly")
        return True
    else:
        print("⚠️  Model is still slow even when loaded")
        return False


def test_direct_ollama_api():
    """Test Ollama API directly to isolate any Python client issues"""
    print("\n" + "=" * 80)
    print("Test 4: Direct API call (bypassing Python client)")
    print("=" * 80)
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": "Say hello in one word",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 50
        }
    }
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "")
            print(f"Response: {result[:100]}")
            print(f"⏱️  Time taken: {elapsed:.2f} seconds")
            
            if elapsed < 10:
                print("✅ Direct API call is fast")
                return True
            else:
                print("⚠️  Direct API call is slow")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Direct API call timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🔍 Ollama Timing Diagnostic Test\n")
    
    try:
        test_ollama_timing()
        test_direct_ollama_api()
        
        print("\n" + "=" * 80)
        print("DIAGNOSIS SUMMARY")
        print("=" * 80)
        print("If tests are timing out or taking > 30 seconds:")
        print("1. Model may not be fully loaded in memory")
        print("2. Ollama may be running out of resources (check RAM/CPU)")
        print("3. Model may be too large for your hardware")
        print("\nRecommendations:")
        print("- Try a smaller model: ollama pull qwen2.5-coder:3b")
        print("- Restart Ollama: Stop and restart 'ollama serve'")
        print("- Check system resources: Task Manager -> Performance")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
