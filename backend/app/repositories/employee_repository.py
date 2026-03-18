"""
Employee repository with advanced filtering capabilities
"""

from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import date

from sqlalchemy import select, func, and_, or_, text, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee, EmployeeHistory
from app.repositories.base_repository import BaseRepository
from app.schemas.employee import (
    EmployeeFilter, FilterBlock, FilterCondition, FilterOperator, FilterLogic
)


class EmployeeRepository(BaseRepository[Employee]):
    """
    Employee repository with advanced query capabilities
    Supports complex filtering, aggregations, and dynamic SQL generation
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Employee, session)
    
    async def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by business ID"""
        return await self.get_by_field("employee_id", employee_id)
    
    async def get_with_history(self, employee_id: str) -> Optional[Employee]:
        """Get employee with change history"""
        result = await self.session.execute(
            select(Employee)
            .options(selectinload(Employee.history))
            .where(Employee.employee_id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_manager(self, manager_id: str) -> List[Employee]:
        """Get all direct reports for a manager"""
        return await self.get_many_by_field("manager_id", manager_id, limit=1000)
    
    def _build_filter_condition(self, condition: FilterCondition):
        """Build SQLAlchemy filter from FilterCondition"""
        column = getattr(Employee, condition.field)
        op = condition.operator
        value = condition.value
        
        if op == FilterOperator.EQUALS:
            return column == value
        elif op == FilterOperator.NOT_EQUALS:
            return column != value
        elif op == FilterOperator.GREATER_THAN:
            return column > value
        elif op == FilterOperator.GREATER_THAN_OR_EQUAL:
            return column >= value
        elif op == FilterOperator.LESS_THAN:
            return column < value
        elif op == FilterOperator.LESS_THAN_OR_EQUAL:
            return column <= value
        elif op == FilterOperator.IN:
            return column.in_(value if isinstance(value, list) else [value])
        elif op == FilterOperator.NOT_IN:
            return column.notin_(value if isinstance(value, list) else [value])
        elif op == FilterOperator.CONTAINS:
            return column.ilike(f"%{value}%")
        elif op == FilterOperator.STARTS_WITH:
            return column.ilike(f"{value}%")
        elif op == FilterOperator.ENDS_WITH:
            return column.ilike(f"%{value}")
        elif op == FilterOperator.BETWEEN:
            return column.between(value, condition.value_end)
        elif op == FilterOperator.IS_NULL:
            return column.is_(None)
        elif op == FilterOperator.IS_NOT_NULL:
            return column.isnot(None)
        else:
            return column == value
    
    def _build_filter_block(self, block: FilterBlock):
        """Build SQLAlchemy filter from FilterBlock"""
        conditions = [
            self._build_filter_condition(cond) 
            for cond in block.conditions
        ]
        
        if block.logic == FilterLogic.AND:
            return and_(*conditions)
        else:
            return or_(*conditions)
    
    def _build_filters(self, filters: EmployeeFilter):
        """Build all filters from EmployeeFilter schema"""
        all_conditions = []
        
        # Process filter blocks
        for block in filters.filter_blocks:
            all_conditions.append(self._build_filter_block(block))
        
        # Quick filters
        if filters.departments:
            all_conditions.append(Employee.department.in_(filters.departments))
        if filters.grades:
            all_conditions.append(Employee.grade_level.in_(filters.grades))
        if filters.countries:
            all_conditions.append(Employee.branch_country.in_(filters.countries))
        if filters.cities:
            all_conditions.append(Employee.branch_city.in_(filters.cities))
        if filters.statuses:
            all_conditions.append(Employee.status.in_(filters.statuses))
        if filters.religions:
            all_conditions.append(Employee.religion.in_(filters.religions))
        if filters.marital_statuses:
            all_conditions.append(Employee.marital_status.in_(filters.marital_statuses))
        if filters.employment_types:
            all_conditions.append(Employee.employment_type.in_(filters.employment_types))
        if filters.units:
            all_conditions.append(Employee.unit_name.in_(filters.units))
        
        # Range filters
        if filters.salary_min is not None:
            all_conditions.append(Employee.salary >= filters.salary_min)
        if filters.salary_max is not None:
            all_conditions.append(Employee.salary <= filters.salary_max)
        if filters.age_min is not None:
            all_conditions.append(Employee.age >= filters.age_min)
        if filters.age_max is not None:
            all_conditions.append(Employee.age <= filters.age_max)
        if filters.experience_min is not None:
            all_conditions.append(Employee.years_experience >= filters.experience_min)
        if filters.experience_max is not None:
            all_conditions.append(Employee.years_experience <= filters.experience_max)
        if filters.performance_min is not None:
            all_conditions.append(Employee.performance_score >= filters.performance_min)
        if filters.performance_max is not None:
            all_conditions.append(Employee.performance_score <= filters.performance_max)
        
        # Date filters
        if filters.hire_date_from:
            all_conditions.append(Employee.hire_date >= filters.hire_date_from)
        if filters.hire_date_to:
            all_conditions.append(Employee.hire_date <= filters.hire_date_to)
        
        # Text search
        if filters.search_term:
            search = f"%{filters.search_term}%"
            all_conditions.append(
                or_(
                    Employee.first_name.ilike(search),
                    Employee.last_name.ilike(search),
                    Employee.employee_id.ilike(search),
                    Employee.email_address.ilike(search),
                )
            )
        
        # Manager filter
        if filters.manager_id:
            all_conditions.append(Employee.manager_id == filters.manager_id)
        
        return and_(*all_conditions) if all_conditions else None
    
    async def search(
        self,
        filters: EmployeeFilter,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "employee_id",
        sort_order: str = "asc"
    ) -> Tuple[List[Employee], int]:
        """
        Search employees with advanced filters
        
        Returns tuple of (employees, total_count)
        """
        # Base query
        query = select(Employee)
        count_query = select(func.count()).select_from(Employee)
        
        # Apply filters
        filter_conditions = self._build_filters(filters)
        if filter_conditions is not None:
            query = query.where(filter_conditions)
            count_query = count_query.where(filter_conditions)
        
        # Get total count
        total = await self.session.execute(count_query)
        total_count = total.scalar()
        
        # Apply sorting
        if hasattr(Employee, sort_by):
            order_col = getattr(Employee, sort_by)
            query = query.order_by(
                order_col.desc() if sort_order == "desc" else order_col
            )
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute
        result = await self.session.execute(query)
        employees = list(result.scalars().all())
        
        return employees, total_count
    
    async def get_aggregations(
        self,
        filters: EmployeeFilter,
        group_by: str,
        metrics: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated metrics grouped by dimension
        
        Args:
            filters: Filters to apply
            group_by: Field to group by
            metrics: List of metrics to compute (count, avg_salary, etc.)
        """
        if not hasattr(Employee, group_by):
            raise ValueError(f"Invalid group_by field: {group_by}")
        
        group_col = getattr(Employee, group_by)
        
        # Default metrics
        if not metrics:
            metrics = ["count", "avg_salary", "avg_performance"]
        
        # Build aggregation columns
        agg_columns = [group_col.label("dimension")]
        
        if "count" in metrics:
            agg_columns.append(func.count().label("count"))
        if "avg_salary" in metrics:
            agg_columns.append(func.avg(Employee.salary).label("avg_salary"))
        if "sum_salary" in metrics:
            agg_columns.append(func.sum(Employee.salary).label("sum_salary"))
        if "avg_performance" in metrics:
            agg_columns.append(func.avg(Employee.performance_score).label("avg_performance"))
        if "avg_experience" in metrics:
            agg_columns.append(func.avg(Employee.years_experience).label("avg_experience"))
        if "avg_age" in metrics:
            agg_columns.append(func.avg(Employee.age).label("avg_age"))
        if "min_salary" in metrics:
            agg_columns.append(func.min(Employee.salary).label("min_salary"))
        if "max_salary" in metrics:
            agg_columns.append(func.max(Employee.salary).label("max_salary"))
        
        query = select(*agg_columns)
        
        # Apply filters
        filter_conditions = self._build_filters(filters)
        if filter_conditions is not None:
            query = query.where(filter_conditions)
        
        # Group and order
        query = query.group_by(group_col).order_by(func.count().desc())
        
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [dict(row._mapping) for row in rows]
    
    async def get_summary_stats(
        self,
        filters: EmployeeFilter = None
    ) -> Dict[str, Any]:
        """Get summary statistics for filtered employees"""
        query = select(
            func.count().label("total_count"),
            func.count().filter(Employee.status == "Active").label("active_count"),
            func.avg(Employee.salary).label("avg_salary"),
            func.avg(Employee.performance_score).label("avg_performance"),
            func.avg(Employee.years_experience).label("avg_experience"),
            func.avg(Employee.age).label("avg_age"),
            func.sum(Employee.salary).label("total_salary"),
        )
        
        if filters:
            filter_conditions = self._build_filters(filters)
            if filter_conditions is not None:
                query = query.where(filter_conditions)
        
        result = await self.session.execute(query)
        row = result.fetchone()
        
        return dict(row._mapping) if row else {}
    
    async def get_distribution(
        self,
        field: str,
        filters: EmployeeFilter = None
    ) -> List[Dict[str, Any]]:
        """Get value distribution for a field"""
        if not hasattr(Employee, field):
            raise ValueError(f"Invalid field: {field}")
        
        col = getattr(Employee, field)
        query = select(
            col.label("value"),
            func.count().label("count")
        ).group_by(col).order_by(func.count().desc())
        
        if filters:
            filter_conditions = self._build_filters(filters)
            if filter_conditions is not None:
                query = query.where(filter_conditions)
        
        result = await self.session.execute(query)
        return [dict(row._mapping) for row in result.fetchall()]
    
    async def generate_sql_from_filters(self, filters: EmployeeFilter) -> str:
        """Generate SQL string from filters (for debugging/logging)"""
        query = select(Employee)
        filter_conditions = self._build_filters(filters)
        if filter_conditions is not None:
            query = query.where(filter_conditions)
        
        return str(query.compile(compile_kwargs={"literal_binds": True}))
    
    async def bulk_upsert(self, employees: List[Dict[str, Any]]) -> int:
        """Bulk upsert employees"""
        from sqlalchemy.dialects.postgresql import insert
        
        stmt = insert(Employee).values(employees)
        stmt = stmt.on_conflict_do_update(
            index_elements=['employee_id'],
            set_={
                col.name: col for col in stmt.excluded
                if col.name not in ('id', 'employee_id', 'created_at')
            }
        )
        
        result = await self.session.execute(stmt)
        return result.rowcount
    
    async def record_history(
        self,
        employee_id: str,
        change_type: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        changed_by: str = None,
        reason: str = None
    ):
        """Record employee change in history"""
        history = EmployeeHistory(
            employee_id=employee_id,
            change_type=change_type,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            effective_date=date.today(),
            changed_by=changed_by,
            reason=reason
        )
        self.session.add(history)
        await self.session.flush()
