"""
Analytics repository for precomputed metrics and predictions
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import (
    AnalyticsSnapshot, PredictionResult, AuditLog, SavedQuery, Report
)
from app.repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository[AnalyticsSnapshot]):
    """Repository for analytics data"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AnalyticsSnapshot, session)
    
    async def get_latest_snapshot(
        self,
        metric_name: str,
        dimension: str = None
    ) -> List[AnalyticsSnapshot]:
        """Get latest snapshot for a metric"""
        subquery = (
            select(func.max(AnalyticsSnapshot.snapshot_date))
            .where(AnalyticsSnapshot.metric_name == metric_name)
        )
        
        if dimension:
            subquery = subquery.where(AnalyticsSnapshot.dimension == dimension)
        
        query = (
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.metric_name == metric_name)
            .where(AnalyticsSnapshot.snapshot_date == subquery.scalar_subquery())
        )
        
        if dimension:
            query = query.where(AnalyticsSnapshot.dimension == dimension)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_snapshots_in_range(
        self,
        metric_name: str,
        dimension: str,
        start_date: date,
        end_date: date
    ) -> List[AnalyticsSnapshot]:
        """Get snapshots within date range for trend analysis"""
        query = (
            select(AnalyticsSnapshot)
            .where(
                and_(
                    AnalyticsSnapshot.metric_name == metric_name,
                    AnalyticsSnapshot.dimension == dimension,
                    AnalyticsSnapshot.snapshot_date >= start_date,
                    AnalyticsSnapshot.snapshot_date <= end_date
                )
            )
            .order_by(AnalyticsSnapshot.snapshot_date)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def save_snapshot(
        self,
        metric_name: str,
        dimension: str,
        dimension_value: str,
        value: float,
        count: int = None,
        breakdown: Dict = None,
        snapshot_type: str = "daily"
    ) -> AnalyticsSnapshot:
        """Save new analytics snapshot"""
        snapshot = AnalyticsSnapshot(
            snapshot_date=date.today(),
            snapshot_type=snapshot_type,
            metric_name=metric_name,
            dimension=dimension,
            dimension_value=dimension_value,
            metric_value=value,
            metric_count=count,
            breakdown=breakdown
        )
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot


class PredictionRepository(BaseRepository[PredictionResult]):
    """Repository for ML predictions"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(PredictionResult, session)
    
    async def get_latest_predictions(
        self,
        employee_id: str = None,
        prediction_type: str = None,
        limit: int = 100
    ) -> List[PredictionResult]:
        """Get latest predictions"""
        query = select(PredictionResult)
        
        conditions = []
        if employee_id:
            conditions.append(PredictionResult.employee_id == employee_id)
        if prediction_type:
            conditions.append(PredictionResult.prediction_type == prediction_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PredictionResult.prediction_date.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_high_risk_employees(
        self,
        prediction_type: str,
        threshold: float,
        limit: int = 100
    ) -> List[PredictionResult]:
        """Get employees with high risk scores"""
        # Subquery to get latest prediction per employee
        latest_subq = (
            select(
                PredictionResult.employee_id,
                func.max(PredictionResult.prediction_date).label("max_date")
            )
            .where(PredictionResult.prediction_type == prediction_type)
            .group_by(PredictionResult.employee_id)
            .subquery()
        )
        
        query = (
            select(PredictionResult)
            .join(
                latest_subq,
                and_(
                    PredictionResult.employee_id == latest_subq.c.employee_id,
                    PredictionResult.prediction_date == latest_subq.c.max_date
                )
            )
            .where(
                and_(
                    PredictionResult.prediction_type == prediction_type,
                    PredictionResult.prediction_score >= threshold
                )
            )
            .order_by(PredictionResult.prediction_score.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def save_prediction(
        self,
        employee_id: str,
        prediction_type: str,
        score: float,
        model_version: str,
        label: str = None,
        confidence: float = None,
        feature_importance: Dict = None,
        shap_values: Dict = None,
        recommendations: List[Dict] = None,
        input_features: Dict = None
    ) -> PredictionResult:
        """Save new prediction result"""
        prediction = PredictionResult(
            employee_id=employee_id,
            prediction_type=prediction_type,
            model_version=model_version,
            prediction_score=score,
            prediction_label=label,
            confidence=confidence,
            feature_importance=feature_importance,
            shap_values=shap_values,
            recommendations=recommendations,
            input_features=input_features
        )
        self.session.add(prediction)
        await self.session.flush()
        return prediction
    
    async def save_predictions_batch(
        self,
        predictions: List[Dict[str, Any]]
    ) -> int:
        """Save multiple predictions"""
        objs = [PredictionResult(**p) for p in predictions]
        self.session.add_all(objs)
        await self.session.flush()
        return len(objs)


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit logs"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)
    
    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str = None,
        user_id: UUID = None,
        username: str = None,
        ip_address: str = None,
        user_agent: str = None,
        request_method: str = None,
        request_path: str = None,
        request_body: Dict = None,
        changes: Dict = None,
        status_code: int = None,
        error_message: str = None
    ) -> AuditLog:
        """Log an audit event"""
        log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            request_body=request_body,
            changes=changes,
            status_code=status_code,
            error_message=error_message
        )
        self.session.add(log)
        await self.session.flush()
        return log
    
    async def get_user_activity(
        self,
        user_id: UUID,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a user"""
        query = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
        )
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit history for a resource"""
        query = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id
                )
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SavedQueryRepository(BaseRepository[SavedQuery]):
    """Repository for saved queries"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(SavedQuery, session)
    
    async def get_user_queries(
        self,
        user_id: UUID,
        query_type: str = None
    ) -> List[SavedQuery]:
        """Get all saved queries for a user"""
        query = select(SavedQuery).where(SavedQuery.user_id == user_id)
        
        if query_type:
            query = query.where(SavedQuery.query_type == query_type)
        
        query = query.order_by(SavedQuery.updated_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_public_queries(self) -> List[SavedQuery]:
        """Get all public queries"""
        result = await self.session.execute(
            select(SavedQuery)
            .where(SavedQuery.is_public == True)
            .order_by(SavedQuery.name)
        )
        return list(result.scalars().all())


class ReportRepository(BaseRepository[Report]):
    """Repository for generated reports"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)
    
    async def get_user_reports(
        self,
        user_id: UUID,
        status: str = None,
        limit: int = 50
    ) -> List[Report]:
        """Get reports for a user"""
        query = select(Report).where(Report.user_id == user_id)
        
        if status:
            query = query.where(Report.status == status)
        
        query = query.order_by(Report.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        report_id: UUID,
        status: str,
        file_path: str = None,
        file_size: int = None,
        error_message: str = None
    ) -> Optional[Report]:
        """Update report status"""
        update_data = {"status": status}
        
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
            if file_path:
                update_data["file_path"] = file_path
            if file_size:
                update_data["file_size"] = file_size
        elif status == "failed" and error_message:
            update_data["error_message"] = error_message
        
        return await self.update(report_id, update_data)
