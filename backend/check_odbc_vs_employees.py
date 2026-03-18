"""
Check ODBC table vs Employees table data
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://hr_admin:zbfXZpBPyxgEYEVm@localhost:5432/hr_analytics"
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def check_tables():
    async with AsyncSessionLocal() as session:
        # Check ODBC table
        print("=== ODBC TABLE ===")
        result = await session.execute(
            text("SELECT COUNT(*) as total FROM odbc")
        )
        odbc_count = result.scalar()
        print(f"Total records: {odbc_count}")
        
        # Check for Branch Managers in ODBC
        result = await session.execute(
            text("""
                SELECT COUNT(*) as bm_count 
                FROM odbc 
                WHERE "POSITION_NAME" LIKE '%Branch Manager%' 
                  AND "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
            """)
        )
        odbc_bm = result.scalar()
        print(f"Branch Managers: {odbc_bm}")
        
        # Check ODBC columns
        result = await session.execute(
            text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'odbc' 
                ORDER BY ordinal_position
            """)
        )
        odbc_cols = [row[0] for row in result.fetchall()]
        print(f"Columns in ODBC: {', '.join(odbc_cols[:20])}...")
        
        print("\n=== EMPLOYEES TABLE ===")
        result = await session.execute(
            text("SELECT COUNT(*) as total FROM employees")
        )
        emp_count = result.scalar()
        print(f"Total records: {emp_count}")
        
        # Check if employees table has position_name
        result = await session.execute(
            text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees' 
                  AND column_name LIKE '%position%'
            """)
        )
        emp_pos_cols = [row[0] for row in result.fetchall()]
        print(f"Position-related columns in employees: {emp_pos_cols}")
        
        # Check if employees has designation
        result = await session.execute(
            text("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT designation) as distinct_designations
                FROM employees
                WHERE designation IS NOT NULL
            """)
        )
        row = result.fetchone()
        print(f"Employees with designation: {row[0]}")
        print(f"Distinct designations: {row[1]}")
        
        # Sample some designations
        result = await session.execute(
            text("""
                SELECT DISTINCT designation 
                FROM employees 
                WHERE designation LIKE '%Branch%Manager%'
                LIMIT 10
            """)
        )
        sample_desigs = [row[0] for row in result.fetchall()]
        if sample_desigs:
            print(f"Sample Branch Manager designations in employees:")
            for d in sample_desigs:
                print(f"  - {d}")
        else:
            print("⚠ No Branch Manager designations found in employees table")
        
        print("\n=== COMPARISON ===")
        print(f"ODBC has {odbc_count} records")
        print(f"Employees has {emp_count} records")
        print(f"Difference: {abs(odbc_count - emp_count)}")
        
        if odbc_bm > 0:
            print(f"\n✅ ODBC table has {odbc_bm} Branch Managers")
            print("📊 Branch Manager Analytics is using ODBC table")
        else:
            print("\n⚠ No Branch Managers found in ODBC table")

    await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
