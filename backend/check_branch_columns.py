"""
Check what's in BRANCH vs BRANCH_LEVEL columns
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://hr_admin:zbfXZpBPyxgEYEVm@localhost:5432/hr_analytics"
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def check_branch_columns():
    async with AsyncSessionLocal() as session:
        print("=== BRANCH vs BRANCH_LEVEL Comparison ===\n")
        
        # Check BRANCH_LEVEL distinct values
        result = await session.execute(
            text("""
                SELECT DISTINCT "BRANCH_LEVEL"
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH_LEVEL" IS NOT NULL
                ORDER BY "BRANCH_LEVEL"
            """)
        )
        branch_levels = [row[0] for row in result.fetchall()]
        print(f"BRANCH_LEVEL distinct values ({len(branch_levels)} total):")
        for bl in branch_levels:
            print(f"  - {bl}")
        
        # Check BRANCH distinct values (sample)
        print(f"\n=== BRANCH distinct values (first 30) ===")
        result = await session.execute(
            text("""
                SELECT DISTINCT "BRANCH", COUNT(*) as emp_count
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH" IS NOT NULL
                GROUP BY "BRANCH"
                ORDER BY emp_count DESC
                LIMIT 30
            """)
        )
        branches = result.fetchall()
        print(f"Total distinct BRANCH values: {len(branches)}")
        for branch, count in branches:
            print(f"  {branch}: {count} employees")
        
        # Count total distinct branches
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH")
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH" IS NOT NULL
            """)
        )
        total_branches = result.scalar()
        print(f"\n📊 Total distinct BRANCH values: {total_branches}")
        
        # Check LOCATION_NAME
        print(f"\n=== LOCATION_NAME distinct values (first 30) ===")
        result = await session.execute(
            text("""
                SELECT DISTINCT "LOCATION_NAME", COUNT(*) as emp_count
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "LOCATION_NAME" IS NOT NULL
                GROUP BY "LOCATION_NAME"
                ORDER BY emp_count DESC
                LIMIT 30
            """)
        )
        locations = result.fetchall()
        for location, count in locations:
            print(f"  {location}: {count} employees")
        
        # Count total distinct locations
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "LOCATION_NAME")
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "LOCATION_NAME" IS NOT NULL
            """)
        )
        total_locations = result.scalar()
        print(f"\n📊 Total distinct LOCATION_NAME values: {total_locations}")
        
        # Show sample with all three columns
        print(f"\n=== SAMPLE: BRANCH vs BRANCH_LEVEL vs LOCATION_NAME ===")
        result = await session.execute(
            text("""
                SELECT DISTINCT 
                    "BRANCH",
                    "BRANCH_LEVEL",
                    "LOCATION_NAME"
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH" IS NOT NULL
                LIMIT 20
            """)
        )
        samples = result.fetchall()
        print(f"{'BRANCH':<40} {'BRANCH_LEVEL':<20} {'LOCATION_NAME':<40}")
        print("-" * 100)
        for branch, level, location in samples:
            print(f"{str(branch):<40} {str(level):<20} {str(location):<40}")

    await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_branch_columns())
