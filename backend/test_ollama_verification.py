"""
Test to verify Ollama is running and responding via LLM service
"""
import sys
from pathlib import Path

# Add the parent directory to the path to import from app
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.llm_service import llm_service


def test_ollama_response():
    """Test that Ollama is running and returns a response"""
    print("Testing Ollama connection via LLM service...")
    print(f"Using model: {llm_service.default_model}")
    print(f"Base URL: {llm_service.base_url}")

    # Simple test prompt
    test_prompt = "Say 'Hello, Ollama is working!' in exactly those words."

    try:
        print(f"\nSending prompt: {test_prompt}")
        response = llm_service.predict(prompt=test_prompt)

        print(f"\nResponse received: {response}")

        # Check if we got a response
        if response and not response.startswith("Error"):
            print("✅ SUCCESS: Ollama is running and responding!")
            return True
        else:
            print("❌ FAILURE: Ollama returned an error or empty response")
            return False

    except Exception as e:
        print(f"❌ FAILURE: Exception occurred: {e}")
        return False


if __name__ == "__main__":
    success = test_ollama_response()
    sys.exit(0 if success else 1)