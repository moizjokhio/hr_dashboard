"""
AI API endpoints
Natural language queries, AI search, and predictions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.cache import cache_service

# Handle optional ML imports gracefully
try:
    from app.ml.nlp_query_service import NLPQueryService
    from app.ml.prediction_service import PredictionService
    from app.ml.vector_db_service import VectorDBService
except ImportError:
    NLPQueryService = None
    PredictionService = None
    VectorDBService = None

from app.schemas.ai import (
    NLPQueryRequest, NLPQueryResponse,
    AISearchRequest, AISearchResponse,
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, ModelInfoResponse,
    AnalysisGenerationRequest, SHAPExplanationResponse,
    ChatRequest
)
from app.schemas.employee import EmployeeFilter

router = APIRouter()


@router.post("/query", response_model=NLPQueryResponse)
async def process_nlp_query(
    request: NLPQueryRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Process natural language query and return results
    """
    if not NLPQueryService:
        raise HTTPException(status_code=503, detail="NLP Service not available")

    service = NLPQueryService(session)

    try:
        return await service.process_query(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-search")
async def ai_semantic_search(
    request: AISearchRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Semantic search across employees using embeddings
    """
    if not VectorDBService:
        raise HTTPException(status_code=503, detail="Vector DB Service not available")

    vector_service = VectorDBService()
    
    try:
        results = await vector_service.search_employees(
            query=request.query,
            filters=request.filters.model_dump() if request.filters else None,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )


@router.get("/search/similar/{employee_id}")
async def find_similar_employees(
    employee_id: str,
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Find employees similar to a given employee
    """
    if not VectorDBService:
        raise HTTPException(status_code=503, detail="Vector DB Service not available")

    vector_service = VectorDBService()
    
    results = await vector_service.find_similar_employees(
        employee_id=employee_id,
        limit=limit
    )
    
    return {
        "employee_id": employee_id,
        "similar_employees": results
    }


@router.post("/predict/attrition")
async def predict_attrition(
    request: PredictionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Predict attrition risk for employees
    """
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    prediction_type = request.prediction_type or "attrition"
    
    result = await service.predict_attrition(
        employee_ids=request.employee_ids,
        include_shap=request.include_explanations
    )
    
    return {"prediction_type": prediction_type, **result}


@router.post("/predict/performance")
async def predict_performance(
    request: PredictionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Predict future performance for employees
    """
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    prediction_type = request.prediction_type or "performance"
    
    result = await service.predict_performance(
        employee_ids=request.employee_ids,
        include_shap=request.include_explanations
    )
    
    return {"prediction_type": prediction_type, **result}


@router.post("/predict/promotion")
async def predict_promotion(
    request: PredictionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Predict promotion readiness for employees
    """
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    prediction_type = request.prediction_type or "promotion"
    
    result = await service.predict_promotion(
        employee_ids=request.employee_ids,
        include_shap=request.include_explanations
    )
    
    return {"prediction_type": prediction_type, **result}


@router.post("/predict/batch")
async def batch_predictions(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Run batch predictions for all employees
    """
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    
    # If employee count is small, run synchronously
    employee_count = getattr(request, "employee_count", None) or (len(request.employee_ids) if request.employee_ids else 0)
    if employee_count and employee_count < 1000:
        result = await service.run_batch_predictions(
            filters=request.filters,
            prediction_types=request.prediction_types
        )
        return result
    
    # For large batches, run in background
    job_id = await service.create_batch_job(
        filters=request.filters,
        prediction_types=request.prediction_types
    )
    
    background_tasks.add_task(
        service.run_batch_predictions_async,
        job_id=job_id,
        filters=request.filters,
        prediction_types=request.prediction_types
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Batch prediction started. Check /predict/batch/{job_id} for results."
    }


@router.get("/predict/batch/{job_id}")
async def get_batch_prediction_results(
    job_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get results of a batch prediction job"""
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    
    result = await service.get_batch_results(job_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Batch job {job_id} not found"
        )
    
    return result


@router.get("/explain/{employee_id}/{prediction_type}")
async def get_prediction_explanation(
    employee_id: str,
    prediction_type: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get detailed SHAP explanation for a prediction
    """
    allowed_types = ["attrition", "performance", "promotion"]
    
    if prediction_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prediction_type. Allowed: {allowed_types}"
        )
    
    if not PredictionService:
        raise HTTPException(status_code=503, detail="Prediction Service not available")

    service = PredictionService(session)
    
    explanation = await service.get_detailed_explanation(
        employee_id=employee_id,
        prediction_type=prediction_type
    )
    
    if not explanation:
        raise HTTPException(
            status_code=404,
            detail=f"Employee {employee_id} not found"
        )
    
    return explanation


@router.post("/analyze")
async def generate_analysis(
    request: AnalysisGenerationRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Generate AI-powered analysis text
    """
    if not NLPQueryService:
        raise HTTPException(status_code=503, detail="NLP Service not available")

    service = NLPQueryService(session)
    
    if not hasattr(service, "generate_analysis"):
        raise HTTPException(status_code=501, detail="Analysis generation not implemented")
    
    analysis = await service.generate_analysis(
        data=request.data,
        analysis_type=request.analysis_type,
        focus_areas=request.focus_areas
    )
    
    return {
        "analysis_type": request.analysis_type,
        "analysis": analysis,
        "generated_at": "2024-01-01T00:00:00Z"  # Will use actual timestamp
    }


@router.get("/models/info")
async def get_models_info():
    """
    Get information about loaded AI models
    """
    return {
        "embedding_model": {
            "name": "BAAI/bge-large-en-v1.5",
            "status": "loaded",
            "embedding_dim": 1024,
            "device": "cuda"
        },
        "llm_model": {
            "name": "Qwen2-72B-Instruct-GGUF",
            "status": "loaded",
            "context_length": 32768,
            "device": "cuda"
        },
        "prediction_models": {
            "attrition": {"type": "xgboost", "status": "loaded"},
            "performance": {"type": "lightgbm", "status": "loaded"},
            "promotion": {"type": "catboost", "status": "loaded"}
        }
    }


@router.post("/chat")
async def chat_with_data(
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Chat interface for conversational data exploration
    """
    if not NLPQueryService:
        raise HTTPException(status_code=503, detail="NLP Service not available")

    service = NLPQueryService(session)
    
    response = await service.chat(
        message=request.message,
        conversation_id=request.conversation_id
    )
    
    return response


@router.get("/suggestions")
async def get_query_suggestions(
    partial_query: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get AI-powered query suggestions
    """
    if not VectorDBService:
        raise HTTPException(status_code=503, detail="Vector DB Service not available")

    vector_service = VectorDBService()
    
    suggestions = await vector_service.get_query_suggestions(
        partial_query=partial_query,
        limit=10
    )
    
    return {"suggestions": suggestions}


@router.get("/insights")
async def get_automatic_insights(
    departments: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get AI-generated automatic insights
    """
    if not NLPQueryService:
        raise HTTPException(status_code=503, detail="NLP Service not available")

    filters = EmployeeFilter(departments=departments)
    
    service = NLPQueryService(session)
    insights = await service.generate_automatic_insights(filters)
    
    return {
        "insights": insights,
        "generated_at": "2024-01-01T00:00:00Z"
    }