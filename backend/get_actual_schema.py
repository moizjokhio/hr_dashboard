"""Get actual database schemas for RAG dataset correction"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text


async def get_schemas():
    DATABASE_URL = "postgresql+asyncpg://postgres:Nadra%4012345@localhost:5432/hr_analytics"
    
    async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        print("=" * 80)
        print("EMPLOYEES TABLE SCHEMA")
        print("=" * 80)
        result = await session.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'employees' 
                ORDER BY ordinal_position
            """)
        )
        for col_name, col_type, nullable in result.fetchall():
            print(f"  {col_name:35} {col_type:25} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        print("\n" + "=" * 80)
        print("ODBC TABLE SCHEMA")
        print("=" * 80)
        result = await session.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'odbc' 
                ORDER BY ordinal_position
            """)
        )
        for col_name, col_type, nullable in result.fetchall():
            print(f"  {col_name:35} {col_type:25} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        # Sample location data
        print("\n" + "=" * 80)
        print("SAMPLE LOCATION DATA FROM ODBC")
        print("=" * 80)
        result = await session.execute(
            text('SELECT DISTINCT "LOCATION_NAME" FROM odbc LIMIT 15')
        )
        for (loc,) in result.fetchall():
            print(f"  - {loc}")
    
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(get_schemas())
