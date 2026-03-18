import asyncio
import asyncpg
import sys

async def enable_extensions():
    try:
        # Connect to the hr_analytics database
        conn = await asyncpg.connect(user='hr_admin', password='zbfXZpBPyxgEYEVm', host='localhost', port=5432, database='hr_analytics')
        print("Connected to hr_analytics")
        
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Enabled vector extension")
        except Exception as e:
            print(f"Error enabling vector extension: {e}")

        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            print("Enabled uuid-ossp extension")
        except Exception as e:
            print(f"Error enabling uuid-ossp extension: {e}")
            
        await conn.close()
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(enable_extensions())
