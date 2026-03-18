"""
Generate sample of Branch Manager Analytics data to see what user is viewing
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://hr_admin:zbfXZpBPyxgEYEVm@localhost:5432/hr_analytics"
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def check_bm_analytics():
    async with AsyncSessionLocal() as session:
        print("=== BRANCH MANAGER ANALYTICS DATA ===\n")
        
        # Total Branches
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH_LEVEL") as total_branches
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "BRANCH_LEVEL" IS NOT NULL
            """)
        )
        total_branches = result.scalar()
        print(f"Total Branches: {total_branches}")
        
        # Branches with BM
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH_LEVEL") as bm_branches
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "POSITION_NAME" LIKE '%Branch Manager%'
                  AND "BRANCH_LEVEL" IS NOT NULL
            """)
        )
        bm_branches = result.scalar()
        print(f"Branches with Branch Manager: {bm_branches}")
        
        # Branches with BOM
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH_LEVEL") as bom_branches
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "POSITION_NAME" LIKE '%Branch Operations Manager%'
                  AND "BRANCH_LEVEL" IS NOT NULL
            """)
        )
        bom_branches = result.scalar()
        print(f"Branches with Branch Operations Manager: {bom_branches}")
        
        print(f"\nBranches WITHOUT Branch Manager: {total_branches - bm_branches}")
        print(f"Branches WITHOUT Branch Operations Manager: {total_branches - bom_branches}")
        
        # Top 10 Clusters by BM count
        print("\n=== BRANCH MANAGERS BY CLUSTER (Top 10) ===")
        result = await session.execute(
            text("""
                SELECT 
                    REGEXP_REPLACE("CLUSTERS", '^\\d+\\.', '') as cluster,
                    COUNT(*) as bm_count
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "POSITION_NAME" LIKE '%Branch Manager%'
                  AND "CLUSTERS" IS NOT NULL
                GROUP BY cluster
                ORDER BY bm_count DESC
                LIMIT 10
            """)
        )
        clusters = result.fetchall()
        for cluster, count in clusters:
            print(f"  {cluster}: {count} BMs")
        
        # Top 10 Regions by BM count
        print("\n=== BRANCH MANAGERS BY REGION (Top 10) ===")
        result = await session.execute(
            text("""
                SELECT 
                    REGEXP_REPLACE(
                        REGEXP_REPLACE("REGION", '^\\d+\\.', ''),
                        ' - (Sales|Ops|Operations)$', '', 'i'
                    ) as region,
                    COUNT(*) as bm_count
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "POSITION_NAME" LIKE '%Branch Manager%'
                  AND "REGION" IS NOT NULL
                GROUP BY region
                ORDER BY bm_count DESC
                LIMIT 10
            """)
        )
        regions = result.fetchall()
        for region, count in regions:
            print(f"  {region}: {count} BMs")
        
        # Sample branches WITHOUT Branch Manager
        print("\n=== SAMPLE BRANCHES WITHOUT BRANCH MANAGER (First 20) ===")
        result = await session.execute(
            text("""
                SELECT DISTINCT "BRANCH_LEVEL"
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                  AND "BRANCH_LEVEL" IS NOT NULL
                  AND "BRANCH_LEVEL" NOT IN (
                      SELECT DISTINCT "BRANCH_LEVEL"
                      FROM odbc
                      WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible' 
                        AND "POSITION_NAME" LIKE '%Branch Manager%'
                        AND "BRANCH_LEVEL" IS NOT NULL
                  )
                ORDER BY "BRANCH_LEVEL"
                LIMIT 20
            """)
        )
        no_bm = result.fetchall()
        for (branch,) in no_bm:
            print(f"  - {branch}")
        
        # Check for data quality issues
        print("\n=== DATA QUALITY CHECKS ===")
        
        # Branches with NULL CLUSTERS
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH_LEVEL")
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH_LEVEL" IS NOT NULL
                  AND "CLUSTERS" IS NULL
            """)
        )
        null_clusters = result.scalar()
        print(f"Branches with NULL CLUSTERS: {null_clusters}")
        
        # Branches with NULL REGION
        result = await session.execute(
            text("""
                SELECT COUNT(DISTINCT "BRANCH_LEVEL")
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "BRANCH_LEVEL" IS NOT NULL
                  AND "REGION" IS NULL
            """)
        )
        null_regions = result.scalar()
        print(f"Branches with NULL REGION: {null_regions}")
        
        # Multiple BMs per branch
        result = await session.execute(
            text("""
                SELECT "BRANCH_LEVEL", COUNT(*) as bm_count
                FROM odbc
                WHERE "EMPLOYMENT_STATUS" = 'Active - Payroll Eligible'
                  AND "POSITION_NAME" LIKE '%Branch Manager%'
                  AND "BRANCH_LEVEL" IS NOT NULL
                GROUP BY "BRANCH_LEVEL"
                HAVING COUNT(*) > 1
                ORDER BY bm_count DESC
                LIMIT 10
            """)
        )
        multiple_bms = result.fetchall()
        if multiple_bms:
            print(f"\nBranches with MULTIPLE Branch Managers (Top 10):")
            for branch, count in multiple_bms:
                print(f"  {branch}: {count} BMs")
        else:
            print("\n✅ No branches have multiple Branch Managers")

    await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_bm_analytics())
