"""
Quick test to verify LLM service is working
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.llm_service import llm_service


async def test_llm():
    system_prompt = """You are a SQL generator. Return ONLY valid JSON.
Format: {"is_data": true, "sql": "SELECT ..."}"""
    
    user_prompt = "What is the average salary by department?"
    
    print(f"System prompt: {system_prompt}")
    print(f"User prompt: {user_prompt}")
    print("\nCalling LLM...")
    
    try:
        response = await llm_service.predict(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model="llama3.1:8b"
        )
        
        print(f"\nLLM Response:\n{response}\n")
        print(f"Response type: {type(response)}")
        
        if isinstance(response, dict):
            print(f"Keys: {list(response.keys())}")
        
        return response
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_llm())
