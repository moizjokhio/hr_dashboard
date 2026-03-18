"""
Analytics service - Dashboard metrics and visualizations
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.analytics_repository import (
    AnalyticsRepository, PredictionRepository
)
from app.schemas.employee import EmployeeFilter
from app.schemas.analytics import (
    DashboardMetric, DashboardMetrics, ChartData, ChartDataPoint,
    ChartSeries, ChartType, AnalyticsRequest, AnalyticsResponse
)
from app.core.cache import cache_service, cached


class AnalyticsService:
    """
    Service for computing and caching analytics
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.analytics_repo = AnalyticsRepository(session)
        self.prediction_repo = PredictionRepository(session)
    
    async def get_summary_metrics(self) -> Dict[str, Any]:
        """Get high-level summary metrics for dashboard header"""
        from sqlalchemy import text, func
        
        # Get summary stats using raw SQL for performance
        result = await self.session.execute(text('''
            SELECT 
                COUNT(*) as total_employees,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_employees,
                AVG(basic_salary) as avg_salary,
                AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))) as avg_age,
                AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_joining))) as avg_tenure,
                SUM(CASE WHEN date_of_joining >= CURRENT_DATE - INTERVAL '365 days' THEN 1 ELSE 0 END) as hired_2025,
                SUM(CASE WHEN status != 'Active' AND updated_at >= CURRENT_DATE - INTERVAL '365 days' THEN 1 ELSE 0 END) as terminations_2025,
                SUM(CASE WHEN date_of_joining >= CURRENT_DATE - INTERVAL '30 days' THEN 1 ELSE 0 END) as recent_hires
            FROM employees
        '''))
        
        row = result.first()
        
        total = row[0] or 0
        active = row[1] or 0
        
        return {
            "total_employees": total,
            "active_employees": active,
            "inactive_employees": total - active,
            "hired_2025": row[5] or 0,
            "terminations_2025": row[6] or 0,
            "net_headcount_2025": (row[5] or 0) - (row[6] or 0),
            "avg_salary": round(float(row[2]) if row[2] else 0, 0),
            "avg_age": round(float(row[3]) if row[3] else 0, 1),
            "avg_tenure": round(float(row[4]) if row[4] else 0, 1),
            "recent_hires_30days": row[7] or 0,
        }
    
    async def get_dashboard_metrics(
        self,
        filters: EmployeeFilter = None
    ) -> DashboardMetrics:
        """Get main dashboard KPIs"""
        # Check cache
        cache_key = f"dashboard:metrics:{hash(str(filters)) if filters else 'all'}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            return DashboardMetrics(**cached_data)
        
        # Get summary stats
        stats = await self.employee_repo.get_summary_stats(filters)
        
        # Calculate metrics
        total = stats.get("total_count", 0)
        active = stats.get("active_count", 0)
        
        metrics = DashboardMetrics(
            total_employees=DashboardMetric(
                name="Total Employees",
                value=total,
                format="number"
            ),
            active_employees=DashboardMetric(
                name="Active Employees",
                value=active,
                format="number"
            ),
            avg_salary=DashboardMetric(
                name="Average Salary",
                value=round(float(stats.get("avg_salary", 0)), 0),
                format="currency",
                unit="PKR"
            ),
            avg_tenure=DashboardMetric(
                name="Average Tenure",
                value=round(float(stats.get("avg_experience", 0)), 1),
                format="number",
                unit="years"
            ),
            avg_performance=DashboardMetric(
                name="Average Performance",
                value=round(float(stats.get("avg_performance", 0)), 2),
                format="number"
            ),
            attrition_rate=DashboardMetric(
                name="Attrition Rate",
                value=round((total - active) / total * 100 if total > 0 else 0, 1),
                format="percentage"
            ),
            diversity_ratio=await self._calculate_diversity_ratio(filters),
            high_performers=DashboardMetric(
                name="High Performers",
                value=await self._count_high_performers(filters),
                format="number"
            )
        )
        
        # Cache for 5 minutes
        await cache_service.set(cache_key, metrics.model_dump(), ttl=300)
        
        return metrics
    
    async def _calculate_diversity_ratio(
        self,
        filters: EmployeeFilter = None
    ) -> DashboardMetric:
        """Calculate gender diversity ratio"""
        distribution = await self.employee_repo.get_distribution("gender", filters)
        
        total = sum(d["count"] for d in distribution)
        female_count = next(
            (d["count"] for d in distribution if d["value"] == "F"), 0
        )
        
        ratio = round(female_count / total * 100 if total > 0 else 0, 1)
        
        return DashboardMetric(
            name="Gender Diversity",
            value=ratio,
            format="percentage",
            unit="%"
        )
    
    async def _count_high_performers(
        self,
        filters: EmployeeFilter = None
    ) -> int:
        """Count employees with performance >= 4.0"""
        if filters is None:
            filters = EmployeeFilter()
        
        filters.performance_min = 4.0
        _, count = await self.employee_repo.search(filters, page=1, page_size=1)
        return count
    
    async def get_headcount_by_dimension(
        self,
        dimension: str,
        filters: EmployeeFilter = None
    ) -> ChartData:
        """Get headcount grouped by dimension"""
        data = await self.employee_repo.get_aggregations(
            filters=filters or EmployeeFilter(),
            group_by=dimension,
            metrics=["count"]
        )
        
        series = ChartSeries(
            name="Headcount",
            data=[
                ChartDataPoint(
                    label=str(d["dimension"]),
                    value=d["count"]
                )
                for d in data[:20]  # Top 20
            ]
        )
        
        return ChartData(
            chart_type=ChartType.BAR,
            title=f"Headcount by {dimension.replace('_', ' ').title()}",
            series=[series],
            categories=[str(d["dimension"]) for d in data[:20]]
        )
    
    async def get_salary_distribution(
        self,
        filters: EmployeeFilter = None,
        group_by: str = "department"
    ) -> ChartData:
        """Get salary distribution by dimension"""
        data = await self.employee_repo.get_aggregations(
            filters=filters or EmployeeFilter(),
            group_by=group_by,
            metrics=["avg_salary", "min_salary", "max_salary", "count"]
        )
        
        series = ChartSeries(
            name="Average Salary",
            data=[
                ChartDataPoint(
                    label=str(d["dimension"]),
                    value=round(float(d["avg_salary"]), 0),
                    metadata={
                        "min": float(d["min_salary"]),
                        "max": float(d["max_salary"]),
                        "count": d["count"]
                    }
                )
                for d in data[:15]
            ]
        )
        
        return ChartData(
            chart_type=ChartType.BAR,
            title=f"Average Salary by {group_by.replace('_', ' ').title()}",
            series=[series],
            y_axis_label="Salary (PKR)"
        )
    
    async def get_performance_distribution(
        self,
        filters: EmployeeFilter = None
    ) -> ChartData:
        """Get performance score distribution"""
        # Create performance bands
        employees, _ = await self.employee_repo.search(
            filters=filters or EmployeeFilter(),
            page=1,
            page_size=100000
        )
        
        bands = {
            "Outstanding (4.5-5.0)": 0,
            "Exceeds (4.0-4.5)": 0,
            "Meets (3.0-4.0)": 0,
            "Needs Improvement (2.0-3.0)": 0,
            "Unsatisfactory (<2.0)": 0
        }
        
        for emp in employees:
            score = float(emp.performance_score)
            if score >= 4.5:
                bands["Outstanding (4.5-5.0)"] += 1
            elif score >= 4.0:
                bands["Exceeds (4.0-4.5)"] += 1
            elif score >= 3.0:
                bands["Meets (3.0-4.0)"] += 1
            elif score >= 2.0:
                bands["Needs Improvement (2.0-3.0)"] += 1
            else:
                bands["Unsatisfactory (<2.0)"] += 1
        
        series = ChartSeries(
            name="Employees",
            data=[
                ChartDataPoint(label=band, value=count)
                for band, count in bands.items()
            ]
        )
        
        return ChartData(
            chart_type=ChartType.PIE,
            title="Performance Distribution",
            series=[series]
        )
    
    async def get_diversity_metrics(
        self,
        filters: EmployeeFilter = None
    ) -> Dict[str, Any]:
        """Get comprehensive diversity metrics"""
        gender_dist = await self.employee_repo.get_distribution("gender", filters)
        religion_dist = await self.employee_repo.get_distribution("religion", filters)
        education_dist = await self.employee_repo.get_distribution("education_level", filters)
        marital_dist = await self.employee_repo.get_distribution("marital_status", filters)
        
        # Age distribution
        employees, _ = await self.employee_repo.search(
            filters or EmployeeFilter(), page=1, page_size=100000
        )
        
        age_bands = {
            "18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56+": 0
        }
        
        for emp in employees:
            if emp.age <= 25:
                age_bands["18-25"] += 1
            elif emp.age <= 35:
                age_bands["26-35"] += 1
            elif emp.age <= 45:
                age_bands["36-45"] += 1
            elif emp.age <= 55:
                age_bands["46-55"] += 1
            else:
                age_bands["56+"] += 1
        
        return {
            "gender": {d["value"]: d["count"] for d in gender_dist},
            "religion": {d["value"]: d["count"] for d in religion_dist},
            "education": {d["value"]: d["count"] for d in education_dist},
            "marital_status": {d["value"]: d["count"] for d in marital_dist},
            "age_groups": age_bands,
            "charts": {
                "gender": await self._create_pie_chart(
                    gender_dist, "Gender Distribution"
                ),
                "religion": await self._create_pie_chart(
                    religion_dist, "Religion Distribution"
                ),
                "age": await self._create_bar_chart(
                    [{"dimension": k, "count": v} for k, v in age_bands.items()],
                    "Age Distribution"
                )
            }
        }
    
    async def _create_pie_chart(
        self,
        data: List[Dict],
        title: str
    ) -> ChartData:
        """Create pie chart from distribution data"""
        series = ChartSeries(
            name="Distribution",
            data=[
                ChartDataPoint(label=str(d["value"]), value=d["count"])
                for d in data
            ]
        )
        return ChartData(
            chart_type=ChartType.PIE,
            title=title,
            series=[series]
        )
    
    async def _create_bar_chart(
        self,
        data: List[Dict],
        title: str
    ) -> ChartData:
        """Create bar chart from aggregated data"""
        series = ChartSeries(
            name="Count",
            data=[
                ChartDataPoint(label=str(d["dimension"]), value=d["count"])
                for d in data
            ]
        )
        return ChartData(
            chart_type=ChartType.BAR,
            title=title,
            series=[series],
            categories=[str(d["dimension"]) for d in data]
        )
    
    async def compare_groups(
        self,
        group_a_filters: Dict[str, Any],
        group_b_filters: Dict[str, Any],
        group_a_name: str = "Group A",
        group_b_name: str = "Group B"
    ) -> Dict[str, Any]:
        """Compare two employee groups"""
        # Build filter objects
        filter_a = EmployeeFilter(**group_a_filters)
        filter_b = EmployeeFilter(**group_b_filters)
        
        # Get stats for both groups
        stats_a = await self.employee_repo.get_summary_stats(filter_a)
        stats_b = await self.employee_repo.get_summary_stats(filter_b)
        
        # Compare
        comparison = {
            "headcount": {
                group_a_name: stats_a.get("total_count", 0),
                group_b_name: stats_b.get("total_count", 0),
                "difference": stats_a.get("total_count", 0) - stats_b.get("total_count", 0)
            },
            "avg_salary": {
                group_a_name: float(stats_a.get("avg_salary", 0)),
                group_b_name: float(stats_b.get("avg_salary", 0)),
                "difference": float(stats_a.get("avg_salary", 0)) - float(stats_b.get("avg_salary", 0)),
                "percentage_diff": self._percentage_diff(
                    float(stats_a.get("avg_salary", 0)),
                    float(stats_b.get("avg_salary", 0))
                )
            },
            "avg_performance": {
                group_a_name: float(stats_a.get("avg_performance", 0)),
                group_b_name: float(stats_b.get("avg_performance", 0)),
                "difference": float(stats_a.get("avg_performance", 0)) - float(stats_b.get("avg_performance", 0))
            },
            "avg_experience": {
                group_a_name: float(stats_a.get("avg_experience", 0)),
                group_b_name: float(stats_b.get("avg_experience", 0)),
                "difference": float(stats_a.get("avg_experience", 0)) - float(stats_b.get("avg_experience", 0))
            }
        }
        
        # Get diversity comparison
        gender_a = await self.employee_repo.get_distribution("gender", filter_a)
        gender_b = await self.employee_repo.get_distribution("gender", filter_b)
        
        comparison["gender_diversity"] = {
            group_a_name: {d["value"]: d["count"] for d in gender_a},
            group_b_name: {d["value"]: d["count"] for d in gender_b}
        }
        
        # Create comparison chart
        chart = ChartData(
            chart_type=ChartType.BAR,
            title=f"Comparison: {group_a_name} vs {group_b_name}",
            series=[
                ChartSeries(
                    name=group_a_name,
                    data=[
                        ChartDataPoint(label="Avg Salary (K)", value=round(float(stats_a.get("avg_salary", 0))/1000, 1)),
                        ChartDataPoint(label="Avg Performance", value=round(float(stats_a.get("avg_performance", 0)), 2)),
                        ChartDataPoint(label="Avg Experience", value=round(float(stats_a.get("avg_experience", 0)), 1)),
                    ]
                ),
                ChartSeries(
                    name=group_b_name,
                    data=[
                        ChartDataPoint(label="Avg Salary (K)", value=round(float(stats_b.get("avg_salary", 0))/1000, 1)),
                        ChartDataPoint(label="Avg Performance", value=round(float(stats_b.get("avg_performance", 0)), 2)),
                        ChartDataPoint(label="Avg Experience", value=round(float(stats_b.get("avg_experience", 0)), 1)),
                    ]
                )
            ],
            categories=["Avg Salary (K)", "Avg Performance", "Avg Experience"]
        )
        
        return {
            "group_a": {
                "name": group_a_name,
                "filters": group_a_filters,
                "stats": stats_a
            },
            "group_b": {
                "name": group_b_name,
                "filters": group_b_filters,
                "stats": stats_b
            },
            "comparison": comparison,
            "chart": chart.model_dump()
        }
    
    def _percentage_diff(self, a: float, b: float) -> float:
        """Calculate percentage difference"""
        if b == 0:
            return 0 if a == 0 else 100
        return round((a - b) / b * 100, 2)
    
    async def compute_and_save_snapshot(
        self,
        metric_name: str,
        dimension: str
    ):
        """Compute and save analytics snapshot for caching"""
        data = await self.employee_repo.get_aggregations(
            filters=EmployeeFilter(),
            group_by=dimension,
            metrics=["count", "avg_salary", "avg_performance"]
        )
        
        for row in data:
            await self.analytics_repo.save_snapshot(
                metric_name=metric_name,
                dimension=dimension,
                dimension_value=str(row["dimension"]),
                value=row["count"],
                count=row["count"],
                breakdown={
                    "avg_salary": float(row.get("avg_salary", 0)),
                    "avg_performance": float(row.get("avg_performance", 0))
                }
            )
