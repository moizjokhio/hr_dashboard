"""Check actual branch names in database"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text


async def check_branches():
    DATABASE_URL = "postgresql+asyncpg://postgres:Nadra%4012345@localhost:5432/hr_analytics"
    
    async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        # First check if employees table exists and what columns it has
        result = await session.execute(
            text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'employees' 
                ORDER BY ordinal_position
            """)
        )
        columns = result.fetchall()
        
        print("=== EMPLOYEES TABLE COLUMNS ===")
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")
        
        # Check total employees
        result = await session.execute(text("SELECT COUNT(*) FROM employees"))
        total = result.scalar()
        print(f"\nTotal employees: {total}")
        
        # Check if branch_name column exists
        has_branch_name = any(col[0] == 'branch_name' for col in columns)
        
        if has_branch_name:
            # Check branch_name values
            result = await session.execute(
                text("SELECT DISTINCT branch_name FROM employees WHERE branch_name ILIKE '%head%office%' OR branch_name ILIKE '%ubl%' LIMIT 20")
            )
            branches = [row[0] for row in result.fetchall()]
            
            print("\nBranch names containing 'head office' or 'ubl':")
            for b in branches:
                print(f"  - {b}")
        else:
            print("\n⚠ branch_name column does NOT exist in employees table!")
        
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_branches())
