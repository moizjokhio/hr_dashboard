"""
Data loader script to populate database from CSV
"""

import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.models.employee import Employee


async def load_employees_from_csv(csv_path: str, batch_size: int = 5000):
    """
    Load employees from CSV file into database
    
    Args:
        csv_path: Path to CSV file
        batch_size: Number of records to insert per batch
    """
    logger.info(f"Loading employees from {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path, low_memory=False)
    logger.info(f"Loaded {len(df)} records from CSV")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Column mapping from CSV to database
    column_mapping = {
        'employee_id': 'employee_id',
        'full_name': 'full_name',
        'department': 'department',
        'unit_name': 'unit_name',
        'grade_level': 'grade_level',
        'designation': 'designation',
        'employment_type': 'employment_type',
        'branch_city': 'branch_city',
        'branch_country': 'branch_country',
        'date_of_birth': 'date_of_birth',
        'date_of_joining': 'date_of_joining',
        'years_of_experience': 'years_of_experience',
        'gender': 'gender',
        'marital_status': 'marital_status',
        'religion': 'religion',
        'education_level': 'education_level',
        'disability_status': 'disability_status',
        'basic_salary': 'basic_salary',
        'housing_allowance': 'housing_allowance',
        'transport_allowance': 'transport_allowance',
        'other_allowances': 'other_allowances',
        'total_monthly_salary': 'total_monthly_salary',
        'performance_score': 'performance_score',
        'reporting_manager_id': 'reporting_manager_id',
        'status': 'status'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Parse dates
    date_columns = ['date_of_birth', 'date_of_joining']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Clean numeric columns
    numeric_columns = [
        'years_of_experience', 'basic_salary', 'housing_allowance',
        'transport_allowance', 'other_allowances', 'total_monthly_salary',
        'performance_score'
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill missing status with 'Active'
    if 'status' in df.columns:
        df['status'] = df['status'].fillna('Active')
    
    # Create database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Insert in batches
    total_inserted = 0
    
    async with async_session() as session:
        # Clear existing data
        logger.info("Clearing existing employee data...")
        await session.execute(text("TRUNCATE TABLE employees CASCADE"))
        await session.commit()
        
        # Insert new data
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            employees = []
            for _, row in batch.iterrows():
                emp_data = {
                    'employee_id': str(row.get('employee_id', '')),
                    'full_name': str(row.get('full_name', '')),
                    'department': str(row.get('department', '')),
                    'unit_name': str(row.get('unit_name', '')) if pd.notna(row.get('unit_name')) else None,
                    'grade_level': str(row.get('grade_level', '')),
                    'designation': str(row.get('designation', '')) if pd.notna(row.get('designation')) else None,
                    'employment_type': str(row.get('employment_type', '')) if pd.notna(row.get('employment_type')) else None,
                    'branch_city': str(row.get('branch_city', '')) if pd.notna(row.get('branch_city')) else None,
                    'branch_country': str(row.get('branch_country', '')) if pd.notna(row.get('branch_country')) else None,
                    'date_of_birth': row.get('date_of_birth') if pd.notna(row.get('date_of_birth')) else None,
                    'date_of_joining': row.get('date_of_joining') if pd.notna(row.get('date_of_joining')) else None,
                    'years_of_experience': float(row.get('years_of_experience')) if pd.notna(row.get('years_of_experience')) else None,
                    'gender': str(row.get('gender', '')) if pd.notna(row.get('gender')) else None,
                    'marital_status': str(row.get('marital_status', '')) if pd.notna(row.get('marital_status')) else None,
                    'religion': str(row.get('religion', '')) if pd.notna(row.get('religion')) else None,
                    'education_level': str(row.get('education_level', '')) if pd.notna(row.get('education_level')) else None,
                    'disability_status': str(row.get('disability_status', '')) if pd.notna(row.get('disability_status')) else None,
                    'basic_salary': float(row.get('basic_salary')) if pd.notna(row.get('basic_salary')) else None,
                    'housing_allowance': float(row.get('housing_allowance')) if pd.notna(row.get('housing_allowance')) else None,
                    'transport_allowance': float(row.get('transport_allowance')) if pd.notna(row.get('transport_allowance')) else None,
                    'other_allowances': float(row.get('other_allowances')) if pd.notna(row.get('other_allowances')) else None,
                    'total_monthly_salary': float(row.get('total_monthly_salary')) if pd.notna(row.get('total_monthly_salary')) else None,
                    'performance_score': float(row.get('performance_score')) if pd.notna(row.get('performance_score')) else None,
                    'reporting_manager_id': str(row.get('reporting_manager_id', '')) if pd.notna(row.get('reporting_manager_id')) else None,
                    'status': str(row.get('status', 'Active')) if pd.notna(row.get('status')) else 'Active',
                }
                employees.append(Employee(**emp_data))
            
            session.add_all(employees)
            await session.commit()
            
            total_inserted += len(employees)
            logger.info(f"Inserted {total_inserted}/{len(df)} records")
    
    await engine.dispose()
    logger.info(f"Data loading complete. Total records: {total_inserted}")


async def generate_embeddings():
    """
    Generate embeddings for all employees and store in Qdrant
    """
    logger.info("Generating employee embeddings...")
    
    from app.ml.embedding_service import EmbeddingService
    from app.ml.vector_db_service import VectorDBService
    
    embedding_service = EmbeddingService()
    vector_service = VectorDBService()
    
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    batch_size = 100
    
    async with async_session() as session:
        # Get total count
        result = await session.execute(text("SELECT COUNT(*) FROM employees"))
        total = result.scalar()
        logger.info(f"Total employees to embed: {total}")
        
        # Process in batches
        offset = 0
        while offset < total:
            # Fetch batch
            result = await session.execute(
                text(f"""
                    SELECT employee_id, full_name, department, grade_level, 
                           designation, branch_city, branch_country
                    FROM employees
                    ORDER BY id
                    LIMIT {batch_size} OFFSET {offset}
                """)
            )
            rows = result.fetchall()
            
            # Create text for embedding
            texts = []
            employee_ids = []
            for row in rows:
                text_repr = f"{row.full_name}, {row.designation or 'Employee'} in {row.department}, "
                text_repr += f"Grade: {row.grade_level}, Location: {row.branch_city}, {row.branch_country}"
                texts.append(text_repr)
                employee_ids.append(row.employee_id)
            
            # Generate embeddings
            embeddings = embedding_service.encode_batch(texts)
            
            # Store in Qdrant
            await vector_service.upsert_employees(
                employee_ids=employee_ids,
                embeddings=embeddings,
                metadata=[{"text": t} for t in texts]
            )
            
            offset += batch_size
            logger.info(f"Embedded {min(offset, total)}/{total} employees")
    
    await engine.dispose()
    logger.info("Embedding generation complete")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load data into HR Analytics database")
    parser.add_argument("--csv", type=str, help="Path to CSV file")
    parser.add_argument("--embeddings", action="store_true", help="Generate embeddings")
    parser.add_argument("--all", action="store_true", help="Load CSV and generate embeddings")
    
    args = parser.parse_args()
    
    if args.all or args.csv:
        csv_path = args.csv or "../../pak_bank_employees_100k.csv"
        await load_employees_from_csv(csv_path)
    
    if args.all or args.embeddings:
        await generate_embeddings()


if __name__ == "__main__":
    asyncio.run(main())
