"""Check ODBC table schema for location data"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text


async def check_odbc():
    DATABASE_URL = "postgresql+asyncpg://postgres:Nadra%4012345@localhost:5432/hr_analytics"
    
    async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        # Check ODBC table columns
        result = await session.execute(
            text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'odbc' 
                ORDER BY ordinal_position
            """)
        )
        columns = result.fetchall()
        
        print("=== ODBC TABLE COLUMNS ===")
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")
        
        # Check total records
        result = await session.execute(text("SELECT COUNT(*) FROM odbc"))
        total = result.scalar()
        print(f"\nTotal ODBC records: {total}")
        
        # Check for location column
        has_location = any('location' in col[0].lower() for col in columns)
        
        if has_location:
            location_cols = [col[0] for col in columns if 'location' in col[0].lower()]
            print(f"\nLocation columns: {', '.join(location_cols)}")
            
            for loc_col in location_cols:
                result = await session.execute(
                    text(f"SELECT DISTINCT {loc_col} FROM odbc WHERE {loc_col} ILIKE '%head%office%' OR {loc_col} ILIKE '%ubl%' LIMIT 10")
                )
                values = [row[0] for row in result.fetchall()]
                print(f"\n{loc_col} (matching 'head office' or 'ubl'):")
                for v in values:
                    print(f"  - {v}")
    
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_odbc())
