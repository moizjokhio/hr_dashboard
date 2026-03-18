"""
Employee service - Business logic for employee operations
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date
import pandas as pd
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.analytics_repository import AuditLogRepository
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeFilter, EmployeeResponse
)
from app.core.cache import cache_service, cached


class EmployeeService:
    """
    Service layer for employee operations
    Implements business logic, caching, and audit logging
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = EmployeeRepository(session)
        self.audit_repo = AuditLogRepository(session)
    
    async def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get single employee by ID"""
        # Try cache first
        cache_key = f"employee:{employee_id}"
        cached = await cache_service.get(cache_key)
        if cached:
            return Employee(**cached)
        
        employee = await self.repository.get_by_employee_id(employee_id)
        
        if employee:
            # Cache for 5 minutes
            await cache_service.set(cache_key, employee.__dict__, ttl=300)
        
        return employee
    
    async def search_employees(
        self,
        filters: EmployeeFilter,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "employee_id",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Search employees with filters
        
        Returns dict with employees, pagination, and summary stats
        """
        employees, total = await self.repository.search(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get summary statistics
        summary = await self.repository.get_summary_stats(filters)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "employees": employees,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "summary": summary
        }
    
    async def create_employee(
        self,
        data: EmployeeCreate,
        created_by: str = None
    ) -> Employee:
        """Create new employee"""
        # Check for duplicate employee_id
        existing = await self.repository.get_by_employee_id(data.employee_id)
        if existing:
            raise ValueError(f"Employee ID {data.employee_id} already exists")
        
        # Check for duplicate email
        existing_email = await self.repository.get_by_field(
            "email_address", data.email_address
        )
        if existing_email:
            raise ValueError(f"Email {data.email_address} already exists")
        
        employee = await self.repository.create(data.model_dump())
        
        # Audit log
        await self.audit_repo.log_action(
            action="CREATE",
            resource_type="employee",
            resource_id=data.employee_id,
            username=created_by,
            changes=data.model_dump()
        )
        
        # Invalidate caches
        await cache_service.invalidate_analytics_cache()
        
        return employee
    
    async def update_employee(
        self,
        employee_id: str,
        data: EmployeeUpdate,
        updated_by: str = None
    ) -> Optional[Employee]:
        """Update employee"""
        employee = await self.repository.get_by_employee_id(employee_id)
        if not employee:
            return None
        
        # Get changes for audit
        update_data = data.model_dump(exclude_unset=True)
        changes = {}
        
        for field, new_value in update_data.items():
            old_value = getattr(employee, field, None)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                
                # Record history for important fields
                if field in ['department', 'grade_level', 'salary', 'status', 'manager_id']:
                    await self.repository.record_history(
                        employee_id=employee_id,
                        change_type="UPDATE",
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=updated_by
                    )
        
        # Update
        updated = await self.repository.update(employee.id, update_data)
        
        # Audit log
        if changes:
            await self.audit_repo.log_action(
                action="UPDATE",
                resource_type="employee",
                resource_id=employee_id,
                username=updated_by,
                changes=changes
            )
        
        # Invalidate caches
        await cache_service.invalidate_employee_cache(employee_id)
        
        return updated
    
    async def delete_employee(
        self,
        employee_id: str,
        deleted_by: str = None
    ) -> bool:
        """Delete employee (soft delete by changing status)"""
        employee = await self.repository.get_by_employee_id(employee_id)
        if not employee:
            return False
        
        # Soft delete - change status
        await self.repository.update(
            employee.id,
            {"status": "Terminated", "termination_date": date.today()}
        )
        
        # Audit log
        await self.audit_repo.log_action(
            action="DELETE",
            resource_type="employee",
            resource_id=employee_id,
            username=deleted_by
        )
        
        # Invalidate caches
        await cache_service.invalidate_employee_cache(employee_id)
        
        return True
    
    async def bulk_create(
        self,
        employees: List[EmployeeCreate],
        created_by: str = None
    ) -> Dict[str, Any]:
        """Bulk create employees"""
        created = 0
        errors = []
        
        for emp in employees:
            try:
                await self.create_employee(emp, created_by)
                created += 1
            except Exception as e:
                errors.append({
                    "employee_id": emp.employee_id,
                    "error": str(e)
                })
        
        return {
            "total": len(employees),
            "created": created,
            "failed": len(errors),
            "errors": errors
        }
    
    async def get_aggregations(
        self,
        filters: EmployeeFilter,
        group_by: str,
        metrics: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get aggregated data"""
        return await self.repository.get_aggregations(
            filters=filters,
            group_by=group_by,
            metrics=metrics
        )
    
    async def get_distribution(
        self,
        field: str,
        filters: EmployeeFilter = None
    ) -> List[Dict[str, Any]]:
        """Get value distribution"""
        return await self.repository.get_distribution(field, filters)
    
    async def export_employees(
        self,
        filters: EmployeeFilter,
        format: str = "csv",
        columns: List[str] = None
    ) -> bytes:
        """Export employees to file format"""
        employees, _ = await self.repository.search(
            filters=filters,
            page=1,
            page_size=100000  # Max export
        )
        
        # Convert to DataFrame
        data = [
            {
                "employee_id": e.employee_id,
                "first_name": e.first_name,
                "last_name": e.last_name,
                "email_address": e.email_address,
                "gender": e.gender,
                "age": e.age,
                "department": e.department,
                "unit_name": e.unit_name,
                "job_role": e.job_role,
                "grade_level": e.grade_level,
                "branch_country": e.branch_country,
                "branch_city": e.branch_city,
                "salary": float(e.salary),
                "performance_score": float(e.performance_score),
                "years_experience": float(e.years_experience),
                "status": e.status,
                "hire_date": e.hire_date.isoformat() if e.hire_date else None,
            }
            for e in employees
        ]
        
        df = pd.DataFrame(data)
        
        if columns:
            df = df[columns]
        
        buffer = io.BytesIO()
        
        if format == "csv":
            df.to_csv(buffer, index=False)
        elif format == "xlsx":
            df.to_excel(buffer, index=False, engine='openpyxl')
        elif format == "json":
            buffer.write(df.to_json(orient='records').encode())
        
        buffer.seek(0)
        return buffer.read()
    
    async def get_org_chart(
        self,
        root_employee_id: str = None,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """Get organizational chart data"""
        async def build_tree(emp_id: str, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return None
            
            employee = await self.repository.get_by_employee_id(emp_id)
            if not employee:
                return None
            
            reports = await self.repository.get_by_manager(emp_id)
            
            return {
                "employee_id": employee.employee_id,
                "name": f"{employee.first_name} {employee.last_name}",
                "title": employee.job_role,
                "department": employee.department,
                "grade": employee.grade_level,
                "children": [
                    await build_tree(r.employee_id, depth + 1)
                    for r in reports
                ]
            }
        
        if root_employee_id:
            return await build_tree(root_employee_id, 1)
        
        # Find top-level managers (no manager or self-managing)
        # This would need custom logic based on your data
        return {}
    
    async def get_team_analytics(
        self,
        manager_id: str
    ) -> Dict[str, Any]:
        """Get analytics for a manager's team"""
        reports = await self.repository.get_by_manager(manager_id)
        
        if not reports:
            return {"team_size": 0}
        
        salaries = [float(r.salary) for r in reports]
        performances = [float(r.performance_score) for r in reports]
        experiences = [float(r.years_experience) for r in reports]
        
        return {
            "team_size": len(reports),
            "avg_salary": sum(salaries) / len(salaries),
            "avg_performance": sum(performances) / len(performances),
            "avg_experience": sum(experiences) / len(experiences),
            "gender_distribution": self._calculate_distribution(reports, "gender"),
            "grade_distribution": self._calculate_distribution(reports, "grade_level"),
        }
    
    def _calculate_distribution(
        self,
        employees: List[Employee],
        field: str
    ) -> Dict[str, int]:
        """Calculate distribution of a field"""
        distribution = {}
        for emp in employees:
            value = getattr(emp, field, "Unknown")
            distribution[value] = distribution.get(value, 0) + 1
        return distribution
