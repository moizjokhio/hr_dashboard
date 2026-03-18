"""
Quick test to compare model speeds
"""
import requests
import time

def test_model(model_name):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": "Generate SQL to get average salary by department. Return ONLY JSON: {\"is_data\": true, \"sql\": \"...\"}",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 200
        }
    }
    
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print('='*80)
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=90)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "")
            print(f"✅ Response received in {elapsed:.2f} seconds")
            print(f"Response preview: {result[:150]}...")
            
            if elapsed < 30:
                print(f"🚀 FAST - Under 30 seconds")
            elif elapsed < 45:
                print(f"⚠️  ACCEPTABLE - Under 45 seconds")
            elif elapsed < 60:
                print(f"⚠️  SLOW - May timeout in NLP service (45s limit)")
            else:
                print(f"❌ TOO SLOW - Will timeout")
                
            return elapsed
        else:
            print(f"❌ Failed with status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Timed out after 90 seconds")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("\n🔍 Model Speed Comparison")
    print("Testing with SQL generation prompt...\n")
    
    models = [
        "qwen2.5-coder:7b",
        "llama3.1:8b",
    ]
    
    results = {}
    for model in models:
        elapsed = test_model(model)
        if elapsed:
            results[model] = elapsed
        time.sleep(2)  # Brief pause between tests
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    if results:
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        print("\nModels ranked by speed:")
        for i, (model, time_taken) in enumerate(sorted_results, 1):
            status = "✅" if time_taken < 45 else "❌"
            print(f"{i}. {status} {model}: {time_taken:.2f}s")
        
        fastest = sorted_results[0]
        print(f"\n🏆 Fastest model: {fastest[0]} ({fastest[1]:.2f}s)")
        
        if fastest[1] < 45:
            print(f"\n✅ RECOMMENDATION: Use {fastest[0]} - it's fast enough!")
        else:
            print(f"\n⚠️  WARNING: Even the fastest model is too slow!")
            print("Consider:")
            print("  1. Downloading a smaller model (ollama pull qwen2.5-coder:3b)")
            print("  2. Increasing timeout values")
            print("  3. Using a more powerful machine")
