"""Quick single query test"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.ml.nlp_query_service import NLPQueryService


async def test_single():
    async_engine = create_async_engine(
        settings.db.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    query = "Show me all departments in UBL Head Office location"
    print(f"Query: {query}\n")
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        try:
            nlp = NLPQueryService(session=session)
            response = await nlp.process_query(query=query)
            
            print(f"Success: {response.success}")
            print(f"SQL: {response.generated_sql.raw_sql}")
            print(f"Rows: {response.row_count}")
            
            if response.data:
                print(f"\nResults:")
                for i, row in enumerate(response.data[:10], 1):
                    print(f"  {i}. {row}")
            else:
                print(f"Error: {response.analysis}")
                
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_single())
