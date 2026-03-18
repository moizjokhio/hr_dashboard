"""
Warm up Ollama by loading the model into memory
Run this before starting the backend to ensure fast first query
"""
import requests
import time

def warmup_model(model="qwen2.5-coder:7b"):
    print(f"🔥 Warming up model: {model}")
    print("This will load the model into memory for fast responses...\n")
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": "Say hello",
        "stream": False,
        "options": {
            "num_predict": 10
        }
    }
    
    try:
        print("Sending warmup request...")
        start = time.time()
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ Model loaded successfully in {elapsed:.2f} seconds")
            print(f"🚀 Subsequent queries should be much faster (~10-20s)")
            print("\nYou can now start your backend server!")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Warmup timed out - Ollama may not be running")
        print("Make sure 'ollama serve' is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Ollama Model Warmup Script")
    print("="*80 + "\n")
    
    success = warmup_model()
    
    if not success:
        print("\n⚠️  Make sure Ollama is running:")
        print("   ollama serve")
