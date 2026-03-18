"""
Test with reduced RAG context to verify it's fast enough
"""
import requests
import time

def test_with_short_prompt():
    """Test with minimal system prompt"""
    print("="*80)
    print("Test 1: Minimal System Prompt (baseline)")
    print("="*80)
    
    system_prompt = """You are an HR SQL generator. Output ONLY JSON.

Format: {"is_data": true, "sql": "SELECT ..."}

Example: {"is_data": true, "sql": "SELECT department, AVG(total_monthly_salary) FROM employees GROUP BY department"}
"""
    
    user_prompt = "What is the average salary by department?"
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 200,
            "top_k": 1,
            "top_p": 0.1
        }
    }
    
    print(f"System prompt length: {len(system_prompt)} chars")
    print(f"Total prompt length: {len(payload['prompt'])} chars")
    print("\nSending request...")
    
    start = time.time()
    try:
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "")
            print(f"\n✅ Response in {elapsed:.2f} seconds")
            print(f"Response: {result[:200]}")
            return elapsed
        else:
            print(f"❌ Failed with status {response.status_code}")
            return None
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return None


def test_with_medium_prompt():
    """Test with medium-sized system prompt (like reduced RAG)"""
    print("\n" + "="*80)
    print("Test 2: Medium System Prompt (like reduced RAG - 10 values)")
    print("="*80)
    
    # Simulate RAG context with 10 values per field
    rag_context = """- grade_level: AVP-I, AVP-II, CON, OG-1, OG-2, OG-3, OG-4, RVP, SC-1, SEVP-I
- department: IT, HR, Finance, Sales, Operations, Marketing, Legal, Admin, Support, Engineering
- branch_city: Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad, Multan, Peshawar, Quetta, Sialkot, Gujranwala"""
    
    system_prompt = f"""You are an HR SQL generator. Output ONLY JSON, NO markdown.

DATABASE: employees table
Columns: department, total_monthly_salary, full_name, grade_level, branch_city

Format: {{"is_data": true, "sql": "SELECT ..."}}

Example: {{"is_data": true, "sql": "SELECT department, AVG(total_monthly_salary) FROM employees GROUP BY department"}}

Known values:
{rag_context}
"""
    
    user_prompt = "What is the average salary by department?"
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 200,
            "top_k": 1,
            "top_p": 0.1
        }
    }
    
    print(f"System prompt length: {len(system_prompt)} chars")
    print(f"RAG context length: {len(rag_context)} chars")
    print(f"Total prompt length: {len(payload['prompt'])} chars")
    print("\nSending request...")
    
    start = time.time()
    try:
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "")
            print(f"\n✅ Response in {elapsed:.2f} seconds")
            print(f"Response: {result[:200]}")
            return elapsed
        else:
            print(f"❌ Failed with status {response.status_code}")
            return None
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return None


if __name__ == "__main__":
    print("\n🔍 Testing Response Times with Reduced Context\n")
    
    time1 = test_with_short_prompt()
    time2 = test_with_medium_prompt()
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    if time1 and time2:
        print(f"\nMinimal prompt: {time1:.2f}s")
        print(f"Reduced RAG prompt: {time2:.2f}s")
        print(f"Difference: {time2 - time1:.2f}s")
        
        if time2 < 60:
            print(f"\n✅ GOOD: Reduced RAG prompt is under 60 seconds")
        elif time2 < 120:
            print(f"\n⚠️  ACCEPTABLE: Under 120 second timeout but slower than ideal")
        else:
            print(f"\n❌ TOO SLOW: Still exceeding 120 second timeout")
            print("Consider disabling RAG context entirely or using smaller model")
    else:
        print("\n❌ Some tests failed")
