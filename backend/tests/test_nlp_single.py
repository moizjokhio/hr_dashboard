"""
Test that mimics actual NLP service flow
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.ml.nlp_query_service import NLPQueryService


async def test_nlp_service():
    print("Creating async DB session...")
    async_engine = create_async_engine(settings.db.DATABASE_URL)
    
    async with AsyncSession(async_engine) as session:
        print("Creating NLP service...")
        nlp = NLPQueryService(session=session)
        
        query = "What is the average salary by department?"
        print(f"\nQuery: {query}")
        print("\nProcessing...")
        
        try:
            response = await nlp.process_query(query=query)
            
            print(f"\nSuccess: {response.success}")
            print(f"Generated SQL: {response.generated_sql.raw_sql}")
            print(f"Row count: {response.row_count}")
            print(f"Analysis: {response.analysis}")
            
            if response.data:
                print(f"\nFirst 3 results:")
                for row in response.data[:3]:
                    print(f"  {row}")
                    
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_nlp_service())
