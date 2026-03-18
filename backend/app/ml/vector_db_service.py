from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from typing import List, Dict, Any

# Lazy-load model to avoid DLL errors on startup
_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("BAAI/bge-m3")
    return _model

class VectorDBService:
    def __init__(self):
        self.client = None # Placeholder for health check

vector_db_service = VectorDBService()

async def search_employees(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a semantic search against the database using Cosine Similarity.
    """
    model = get_model()  # Lazy-load the model
    embedding = model.encode(query).tolist()
    
    async with AsyncSessionLocal() as session:
        # 1 - (embedding <=> :embedding) calculates cosine similarity
        # <=> is the cosine distance operator in pgvector
        result = await session.execute(
            text("""
                SELECT employee_id, first_name, last_name, department, job_role, 
                       1 - (embedding <=> :embedding) as similarity
                FROM employees
                ORDER BY similarity DESC
                LIMIT :limit
            """),
            {"embedding": str(embedding), "limit": limit}
        )
        
        # Convert to list of dicts
        return [dict(row) for row in result.mappings().all()]

