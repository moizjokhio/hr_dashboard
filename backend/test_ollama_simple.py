"""Test Ollama API without format parameter"""
import requests
import json
import time

url = "http://localhost:11434/api/generate"

# Test without format parameter
payload = {
    "model": "llama3.1:8b",
    "prompt": "Say hello",
    "stream": False
}

print("Testing Ollama without format=json parameter")
print(f"Sending: {json.dumps(payload, indent=2)}")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=60)
    elapsed = time.time() - start
    print(f"Response received in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response text: {data.get('response', '')[:200]}")
    print(f"Full response keys: {data.keys()}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")
