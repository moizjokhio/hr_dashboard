import asyncio
import asyncpg
import sys

async def test_connect():
    try:
        # Try connecting as postgres with no password (trust)
        conn = await asyncpg.connect(user='postgres', host='localhost', port=5432, database='postgres')
        print("SUCCESS: Connected as postgres (trust auth works)")
        
        # Create user and db
        try:
            await conn.execute("CREATE USER hr_admin WITH PASSWORD 'zbfXZpBPyxgEYEVm';")
            print("Created user hr_admin")
        except asyncpg.DuplicateObjectError:
            print("User hr_admin already exists")
            
        try:
            await conn.execute("ALTER USER hr_admin WITH SUPERUSER;")
            print("Granted superuser to hr_admin")
        except Exception as e:
            print(f"Could not grant superuser: {e}")

        # Fix collation version mismatch
        try:
            await conn.execute("ALTER DATABASE postgres REFRESH COLLATION VERSION;")
            await conn.execute("ALTER DATABASE template1 REFRESH COLLATION VERSION;")
            print("Refreshed collation versions")
        except Exception as e:
            print(f"Warning refreshing collation: {e}")

        try:
            await conn.execute("CREATE DATABASE hr_analytics OWNER hr_admin;")
            print("Created database hr_analytics")
        except asyncpg.DuplicateDatabaseError:
            print("Database hr_analytics already exists")
            
        await conn.close()
        sys.exit(0)
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connect())
