"""
Test the exact scenario that was failing - NLP query with timeout
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ml.nlp_query_service import NLPQueryService
from app.schemas.ai import NLPQueryRequest


async def test_exact_failing_query():
    """Test the exact query that was timing out"""
    
    print("="*80)
    print("Testing Exact Failing Scenario")
    print("="*80)
    print("\nQuery: 'What is the average salary by department?'")
    print("This was timing out before the fix.\n")
    
    # Create NLP service
    nlp_service = NLPQueryService()
    
    # Create request
    request = NLPQueryRequest(
        query="What is the average salary by department?"
    )
    
    print("Sending query to NLP service...")
    print("Using model: qwen2.5-coder:7b")
    print("Timeout: 70 seconds")
    print("\nPlease wait... (first query may take ~60s)\n")
    
    try:
        import time
        start = time.time()
        
        # Use the internal _process method to test just the LLM part
        response = await nlp_service._process(request.query)
        
        elapsed = time.time() - start
        
        print(f"✅ SUCCESS! Query completed in {elapsed:.2f} seconds")
        print("\nResponse:")
        print("="*80)
        sql = response.get('generated_sql', {}).get('raw_sql', 'N/A')
        print(f"SQL Generated: {sql[:200]}")
        print("="*80)
        
        if elapsed < 70:
            print(f"\n🎉 GREAT! Response time ({elapsed:.2f}s) is under the 70s timeout")
            print("Your system should now work correctly!")
            return True
        else:
            print(f"\n⚠️  Response took {elapsed:.2f}s (over 70s limit)")
            return False
            
    except asyncio.TimeoutError:
        print("\n❌ FAILED: Query still timing out")
        print("Check:")
        print("  1. Is Ollama running? (ollama serve)")
        print("  2. Try warmup script: python warmup_ollama.py")
        return False
    except RuntimeError as e:
        if "timeout" in str(e).lower():
            print(f"\n❌ FAILED: {e}")
            print("\nThis means the timeout is still too short for your system.")
            print("Options:")
            print("  1. Run warmup script before starting backend")
            print("  2. Use smaller model: ollama pull qwen2.5-coder:3b")
            return False
        raise
    except Exception as e:
        print(f"\n❌ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_subsequent_query():
    """Test a second query (should be much faster)"""
    
    print("\n\n" + "="*80)
    print("Testing Subsequent Query (Should Be Fast)")
    print("="*80)
    print("\nQuery: 'How many employees are there?'\n")
    
    nlp_service = NLPQueryService()
    request = NLPQueryRequest(query="How many employees are there?")
    
    try:
        import time
        start = time.time()
        
        response = await nlp_service._process(request.query)
        
        elapsed = time.time() - start
        
        print(f"✅ SUCCESS! Query completed in {elapsed:.2f} seconds")
        
        if elapsed < 30:
            print(f"\n🚀 EXCELLENT! Subsequent query is fast ({elapsed:.2f}s)")
            print("Model is loaded and responding quickly!")
            return True
        else:
            print(f"\n⚠️  Still slow ({elapsed:.2f}s) even for subsequent query")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False


async def main():
    print("\n🔍 Exact Scenario Test - Testing the fix\n")
    
    # Test 1: The failing query
    test1 = await test_exact_failing_query()
    
    # Test 2: A fast follow-up
    test2 = await test_subsequent_query()
    
    print("\n\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    
    if test1 and test2:
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎉 Your system is fixed and working correctly!")
        print("\nWhat to do next:")
        print("  1. Start your backend server")
        print("  2. Try the query in your frontend")
        print("  3. First query may take ~60s (be patient!)")
        print("  4. Subsequent queries will be fast (~15s)")
        return 0
    elif test1:
        print("\n⚠️  First query works but subsequent queries are slow")
        print("System should work but may be slow overall")
        return 1
    else:
        print("\n❌ Tests failed - system still has issues")
        print("\nTroubleshooting:")
        print("  1. Run warmup script: python warmup_ollama.py")
        print("  2. Check Ollama: ollama list")
        print("  3. Check system resources (RAM/CPU)")
        print("  4. Consider smaller model: ollama pull qwen2.5-coder:3b")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
