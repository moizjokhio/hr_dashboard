import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from app.core.config import settings
import pandas as pd
import numpy as np

def generate_embeddings():
    print("Loading BGE-M3 model...")
    model = SentenceTransformer('BAAI/bge-m3')
    
    print("Connecting to database...")
    db_url = str(settings.db.DATABASE_URL).replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Fetch data
        print("Fetching employee data...")
        df = pd.read_sql("SELECT employee_id, first_name, last_name, department, job_role, skills FROM employees", conn)
        
        if df.empty:
            print("No employees found.")
            return
            
        # Create text for embedding
        # Combine relevant fields
        df['text'] = df.apply(lambda x: f"{x['first_name']} {x['last_name']} {x['department']} {x['job_role']} {x['skills'] if x['skills'] else ''}", axis=1)
        
        print(f"Generating embeddings for {len(df)} employees...")
        # Generate embeddings
        embeddings = model.encode(df['text'].tolist())
        
        print("Updating database...")
        # Update DB
        for idx, row in df.iterrows():
            embedding_list = embeddings[idx].tolist()
            # pgvector expects a string representation like '[0.1, 0.2, ...]'
            conn.execute(
                text("UPDATE employees SET embedding = :embedding WHERE employee_id = :eid"),
                {"embedding": str(embedding_list), "eid": row['employee_id']}
            )
        conn.commit()
        print("Embeddings updated successfully.")

if __name__ == "__main__":
    generate_embeddings()
