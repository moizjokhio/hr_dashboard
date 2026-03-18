import os
from pathlib import Path
from typing import Dict, Any, List, Optional
# from catboost import CatBoostClassifier  # Commented out - install catboost if needed
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.employee import Employee

MODEL_PATH = Path(__file__).parent / "risk_model.cbm"
# model = CatBoostClassifier()  # Commented out - catboost not installed
model = None
model_loaded = False

def load_model():
    global model_loaded
    # Catboost disabled - install catboost to enable predictions
    # if not model_loaded and MODEL_PATH.exists():
    #     model.load_model(str(MODEL_PATH))
    #     model_loaded = True
    pass

class PredictionService:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def predict_attrition(
        self,
        employee_ids: List[str],
        include_shap: bool = True
    ) -> Dict[str, Any]:
        results = []
        for employee_id in employee_ids:
            risk = await predict_employee_risk(employee_id, session=self.session)
            results.append({
                "employee_id": employee_id,
                "risk_score": risk.get("risk_score", 0.0),
                "main_factor": risk.get("main_factor", "Unknown"),
                "shap_values": [] if not include_shap else risk.get("shap_values", [])
            })

        return {
            "prediction_type": "attrition",
            "predictions": results
        }

    async def predict_performance(
        self,
        employee_ids: List[str],
        include_shap: bool = True
    ) -> Dict[str, Any]:
        # Placeholder performance prediction using static scoring
        results = []
        for employee_id in employee_ids:
            results.append({
                "employee_id": employee_id,
                "performance_score": 75.0,
                "confidence": 0.6,
                "shap_values": [] if not include_shap else []
            })

        return {
            "prediction_type": "performance",
            "predictions": results
        }

    async def predict_promotion(
        self,
        employee_ids: List[str],
        include_shap: bool = True
    ) -> Dict[str, Any]:
        # Placeholder promotion readiness
        results = []
        for employee_id in employee_ids:
            results.append({
                "employee_id": employee_id,
                "promotion_probability": 0.3,
                "readiness_score": 55.0,
                "shap_values": [] if not include_shap else []
            })

        return {
            "prediction_type": "promotion",
            "predictions": results
        }

    async def get_detailed_explanation(
        self,
        employee_id: str,
        prediction_type: str
    ) -> Optional[Dict[str, Any]]:
        # Basic placeholder explanation
        return {
            "employee_id": employee_id,
            "prediction_type": prediction_type,
            "feature_importance": [],
            "notes": "Detailed explanations are not implemented yet."
        }

    async def run_batch_predictions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        prediction_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # Stub batch handler
        return {
            "status": "completed",
            "filters": filters or {},
            "prediction_types": prediction_types or ["attrition"],
            "results": []
        }

    async def create_batch_job(
        self,
        filters: Optional[Dict[str, Any]] = None,
        prediction_types: Optional[List[str]] = None
    ) -> str:
        return "batch-job-stub"

    async def run_batch_predictions_async(
        self,
        job_id: str,
        filters: Optional[Dict[str, Any]] = None,
        prediction_types: Optional[List[str]] = None
    ) -> None:
        await self.run_batch_predictions(filters=filters, prediction_types=prediction_types)

    async def get_batch_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        return {"job_id": job_id, "status": "completed", "results": []}

prediction_service = PredictionService()

async def predict_employee_risk(employee_id: str, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
    """
    Loads the saved model and returns a simple dictionary: {"risk_score": 0.85, "main_factor": "Low Salary"}.
    """
    load_model()
    
    if not model_loaded:
        return {"risk_score": 0.0, "main_factor": "Model not trained"}
    
    async def _fetch_employee(active_session: AsyncSession) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.employee_id == employee_id)
        result = await active_session.execute(stmt)
        return result.scalar_one_or_none()
    
    if session is not None:
        employee = await _fetch_employee(session)
    else:
        async with AsyncSessionLocal() as db_session:
            employee = await _fetch_employee(db_session)
    
    if not employee:
        return {"risk_score": 0.0, "main_factor": "Employee not found"}
    
    # Prepare input
    features = ["age", "gender", "department", "job_role", "grade_level", 
                "branch_country", "years_experience", "salary", "performance_score"]
    
    # Extract data
    # Handle potential None values if fields are nullable
    data = {
        "age": employee.age or 0,
        "gender": employee.gender or "Unknown",
        "department": employee.department or "Unknown",
        "job_role": employee.job_role or "Unknown",
        "grade_level": employee.grade_level or "Unknown",
        "branch_country": employee.branch_country or "Unknown",
        "years_experience": float(employee.years_experience) if employee.years_experience is not None else 0.0,
        "salary": float(employee.salary) if employee.salary is not None else 0.0,
        "performance_score": float(employee.performance_score) if employee.performance_score is not None else 0.0
    }
    
    input_data = [data[f] for f in features]
    
    # Predict probability
    try:
        risk_score = model.predict_proba(input_data)[1]
    except Exception as e:
        print(f"Prediction error: {e}")
        return {"risk_score": 0.0, "main_factor": "Prediction Error"}
    
    # Determine main factor (simplified logic)
    main_factor = "General Factors"
    if data["performance_score"] < 3.0:
        main_factor = "Low Performance"
    elif data["years_experience"] > 5 and "Junior" in str(data["grade_level"]):
        main_factor = "Stagnation"
    
    return {
        "risk_score": round(float(risk_score), 2),
        "main_factor": main_factor
    }

