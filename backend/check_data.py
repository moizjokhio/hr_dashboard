import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('''
            SELECT 
                COUNT(*) as total,
                COUNT(date_of_birth) as has_dob,
                COUNT(date_of_joining) as has_doj,
                COUNT(basic_salary) as has_salary,
                AVG(basic_salary) as avg_salary
            FROM employees
        '''))
        row = result.first()
        print(f"Total employees: {row[0]}")
        print(f"With date_of_birth: {row[1]}")
        print(f"With date_of_joining: {row[2]}")
        print(f"With basic_salary: {row[3]}")
        print(f"Average salary: {row[4]}")

asyncio.run(check())
