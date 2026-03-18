"""Minimal test - direct database query to verify schema"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:Nadra%4012345@localhost:5432/hr_analytics"

async def test_odbc_location():
    """Test that LOCATION_NAME exists and has UBL data"""
    
    async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        # Test 1: Check if LOCATION_NAME column exists
        print("Test 1: Checking if odbc.LOCATION_NAME exists...")
        try:
            result = await session.execute(
                text('SELECT COUNT(*) FROM odbc WHERE "LOCATION_NAME" IS NOT NULL')
            )
            count = result.scalar()
            print(f"✓ SUCCESS: Found {count} records with LOCATION_NAME\n")
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
            await async_engine.dispose()
            return
        
        # Test 2: Find UBL Head Office or similar
        print("Test 2: Finding locations with 'UBL' or 'Head Office'...")
        try:
            result = await session.execute(
                text('SELECT DISTINCT "LOCATION_NAME" FROM odbc WHERE "LOCATION_NAME" ILIKE \'%UBL%\' OR "LOCATION_NAME" ILIKE \'%Head%Office%\' LIMIT 10')
            )
            locations = [row[0] for row in result.fetchall()]
            print(f"✓ Found {len(locations)} matching locations:")
            for loc in locations:
                print(f"  - {loc}")
            print()
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
        
        # Test 3: Get departments for a specific location
        print("Test 3: Getting departments from ODBC table...")
        try:
            result = await session.execute(
                text('SELECT DISTINCT "DEPARTMENT_NAME" FROM odbc WHERE "DEPARTMENT_NAME" IS NOT NULL LIMIT 10')
            )
            depts = [row[0] for row in result.fetchall()]
            print(f"✓ Found {len(depts)} departments in ODBC:")
            for dept in depts[:5]:
                print(f"  - {dept}")
            print()
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
        
        # Test 4: Compare with employees table
        print("Test 4: Comparing with employees table...")
        try:
            result = await session.execute(
                text('SELECT COUNT(*) FROM employees')
            )
            emp_count = result.scalar()
            
            result = await session.execute(
                text('SELECT COUNT(*) FROM odbc')
            )
            odbc_count = result.scalar()
            
            print(f"✓ Employees table: {emp_count} records")
            print(f"✓ ODBC table: {odbc_count} records")
            print()
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
    
    await async_engine.dispose()
    print("=" * 60)
    print("CONCLUSION:")
    print("The ODBC table has LOCATION_NAME column (UPPERCASE)")
    print("Use this for branch/office queries, NOT employees.branch_name")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_odbc_location())
