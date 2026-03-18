"""Test Ollama API directly"""
import requests
import json
import time

url = "http://localhost:11434/api/generate"

# Test 1: Simple hello
payload1 = {
    "model": "llama3.1:8b",
    "prompt": "Say hello in one word",
    "stream": False,
    "format": "json",
    "options": {
        "temperature": 0.1,
        "num_predict": 50
    }
}

print("Test 1: Simple hello test")
print(f"Sending: {json.dumps(payload1, indent=2)}")
start = time.time()
try:
    response = requests.post(url, json=payload1, timeout=30)
    elapsed = time.time() - start
    print(f"Response received in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")

print("\n" + "="*80 + "\n")

# Test 2: SQL generation (like our actual use case)
payload2 = {
    "model": "llama3.1:8b",
    "prompt": "Generate SQL to count all rows in table employees",
    "stream": False,
    "format": "json",
    "options": {
        "temperature": 0.1,
        "num_predict": 200
    }
}

print("Test 2: SQL generation")
print(f"Sending: {json.dumps(payload2, indent=2)}")
start = time.time()
try:
    response = requests.post(url, json=payload2, timeout=30)
    elapsed = time.time() - start
    print(f"Response received in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")
