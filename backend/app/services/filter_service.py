"""
Dynamic SQL filter builder service
Converts structured filters to SQL queries safely
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re

from app.schemas.employee import (
    EmployeeFilter, FilterBlock, FilterCondition, FilterOperator, FilterLogic
)


@dataclass
class SQLQuery:
    """Structured SQL query with parameters"""
    sql: str
    parameters: Dict[str, Any]
    tables: List[str]
    
    def to_raw(self) -> str:
        """Convert to raw SQL with parameters substituted (for debugging only)"""
        result = self.sql
        for key, value in self.parameters.items():
            placeholder = f":{key}"
            if isinstance(value, str):
                result = result.replace(placeholder, f"'{value}'")
            elif isinstance(value, (list, tuple)):
                values = ", ".join(
                    f"'{v}'" if isinstance(v, str) else str(v) 
                    for v in value
                )
                result = result.replace(placeholder, f"({values})")
            else:
                result = result.replace(placeholder, str(value))
        return result


class FilterService:
    """
    Service for building SQL queries from filter specifications
    Provides safe parameterized queries to prevent SQL injection
    """
    
    # Mapping of fields to their SQL column names
    FIELD_MAPPING = {
        "employee_id": "e.employee_id",
        "first_name": "e.first_name",
        "last_name": "e.last_name",
        "email_address": "e.email_address",
        "gender": "e.gender",
        "date_of_birth": "e.date_of_birth",
        "age": "e.age",
        "religion": "e.religion",
        "marital_status": "e.marital_status",
        "education_level": "e.education_level",
        "department": "e.department",
        "unit_name": "e.unit_name",
        "job_role": "e.job_role",
        "grade_level": "e.grade_level",
        "job_level_category": "e.job_level_category",
        "branch_country": "e.branch_country",
        "branch_city": "e.branch_city",
        "branch_name": "e.branch_name",
        "branch_region": "e.branch_region",
        "manager_id": "e.manager_id",
        "hire_date": "e.hire_date",
        "years_experience": "e.years_experience",
        "employment_type": "e.employment_type",
        "status": "e.status",
        "salary": "e.basic_salary",
        "total_monthly_salary": "e.total_monthly_salary",
        "basic_salary": "e.basic_salary",
        "performance_score": "e.performance_score",
        "attrition_risk_score": "e.attrition_risk_score",
        "promotion_likelihood": "e.promotion_likelihood",
    }
    
    # Operator mappings
    OPERATOR_SQL = {
        FilterOperator.EQUALS: "=",
        FilterOperator.NOT_EQUALS: "!=",
        FilterOperator.GREATER_THAN: ">",
        FilterOperator.GREATER_THAN_OR_EQUAL: ">=",
        FilterOperator.LESS_THAN: "<",
        FilterOperator.LESS_THAN_OR_EQUAL: "<=",
        FilterOperator.IN: "IN",
        FilterOperator.NOT_IN: "NOT IN",
        FilterOperator.CONTAINS: "ILIKE",
        FilterOperator.STARTS_WITH: "ILIKE",
        FilterOperator.ENDS_WITH: "ILIKE",
        FilterOperator.BETWEEN: "BETWEEN",
        FilterOperator.IS_NULL: "IS NULL",
        FilterOperator.IS_NOT_NULL: "IS NOT NULL",
    }
    
    def __init__(self):
        self.param_counter = 0
    
    def _get_param_name(self) -> str:
        """Generate unique parameter name"""
        self.param_counter += 1
        return f"p{self.param_counter}"
    
    def _get_column(self, field: str) -> str:
        """Get SQL column name for field"""
        if field not in self.FIELD_MAPPING:
            raise ValueError(f"Invalid field: {field}")
        return self.FIELD_MAPPING[field]
    
    def _build_condition(
        self,
        condition: FilterCondition
    ) -> Tuple[str, Dict[str, Any]]:
        """Build single SQL condition with parameters"""
        column = self._get_column(condition.field)
        op = condition.operator
        params = {}
        
        if op in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            return f"{column} {self.OPERATOR_SQL[op]}", params
        
        param_name = self._get_param_name()
        
        if op == FilterOperator.IN:
            values = condition.value if isinstance(condition.value, list) else [condition.value]
            placeholders = ", ".join([f":{param_name}_{i}" for i in range(len(values))])
            for i, v in enumerate(values):
                params[f"{param_name}_{i}"] = v
            return f"{column} IN ({placeholders})", params
        
        elif op == FilterOperator.NOT_IN:
            values = condition.value if isinstance(condition.value, list) else [condition.value]
            placeholders = ", ".join([f":{param_name}_{i}" for i in range(len(values))])
            for i, v in enumerate(values):
                params[f"{param_name}_{i}"] = v
            return f"{column} NOT IN ({placeholders})", params
        
        elif op == FilterOperator.CONTAINS:
            params[param_name] = f"%{condition.value}%"
            return f"{column} ILIKE :{param_name}", params
        
        elif op == FilterOperator.STARTS_WITH:
            params[param_name] = f"{condition.value}%"
            return f"{column} ILIKE :{param_name}", params
        
        elif op == FilterOperator.ENDS_WITH:
            params[param_name] = f"%{condition.value}"
            return f"{column} ILIKE :{param_name}", params
        
        elif op == FilterOperator.BETWEEN:
            param_name_end = self._get_param_name()
            params[param_name] = condition.value
            params[param_name_end] = condition.value_end
            return f"{column} BETWEEN :{param_name} AND :{param_name_end}", params
        
        else:
            params[param_name] = condition.value
            return f"{column} {self.OPERATOR_SQL[op]} :{param_name}", params
    
    def _build_filter_block(
        self,
        block: FilterBlock
    ) -> Tuple[str, Dict[str, Any]]:
        """Build SQL for a filter block"""
        conditions = []
        params = {}
        
        for cond in block.conditions:
            sql, cond_params = self._build_condition(cond)
            conditions.append(sql)
            params.update(cond_params)
        
        logic = " AND " if block.logic == FilterLogic.AND else " OR "
        block_sql = f"({logic.join(conditions)})"
        
        return block_sql, params
    
    def build_where_clause(
        self,
        filters: EmployeeFilter
    ) -> Tuple[str, Dict[str, Any]]:
        """Build complete WHERE clause from filters"""
        self.param_counter = 0
        conditions = []
        all_params = {}
        
        # Process filter blocks
        for block in filters.filter_blocks:
            block_sql, params = self._build_filter_block(block)
            conditions.append(block_sql)
            all_params.update(params)
        
        # Quick filters
        if filters.departments:
            param = self._get_param_name()
            placeholders = ", ".join([f":{param}_{i}" for i in range(len(filters.departments))])
            conditions.append(f"e.department IN ({placeholders})")
            for i, v in enumerate(filters.departments):
                all_params[f"{param}_{i}"] = v
        
        if filters.grades:
            param = self._get_param_name()
            placeholders = ", ".join([f":{param}_{i}" for i in range(len(filters.grades))])
            conditions.append(f"e.grade_level IN ({placeholders})")
            for i, v in enumerate(filters.grades):
                all_params[f"{param}_{i}"] = v
        
        if filters.countries:
            param = self._get_param_name()
            placeholders = ", ".join([f":{param}_{i}" for i in range(len(filters.countries))])
            conditions.append(f"e.branch_country IN ({placeholders})")
            for i, v in enumerate(filters.countries):
                all_params[f"{param}_{i}"] = v
        
        if filters.cities:
            param = self._get_param_name()
            placeholders = ", ".join([f":{param}_{i}" for i in range(len(filters.cities))])
            conditions.append(f"e.branch_city IN ({placeholders})")
            for i, v in enumerate(filters.cities):
                all_params[f"{param}_{i}"] = v
        
        if filters.statuses:
            param = self._get_param_name()
            placeholders = ", ".join([f":{param}_{i}" for i in range(len(filters.statuses))])
            conditions.append(f"e.status IN ({placeholders})")
            for i, v in enumerate(filters.statuses):
                all_params[f"{param}_{i}"] = v
        
        # Range filters
        if filters.salary_min is not None:
            param = self._get_param_name()
            conditions.append(f"e.salary >= :{param}")
            all_params[param] = float(filters.salary_min)
        
        if filters.salary_max is not None:
            param = self._get_param_name()
            conditions.append(f"e.salary <= :{param}")
            all_params[param] = float(filters.salary_max)
        
        if filters.age_min is not None:
            param = self._get_param_name()
            conditions.append(f"e.age >= :{param}")
            all_params[param] = filters.age_min
        
        if filters.age_max is not None:
            param = self._get_param_name()
            conditions.append(f"e.age <= :{param}")
            all_params[param] = filters.age_max
        
        if filters.experience_min is not None:
            param = self._get_param_name()
            conditions.append(f"e.years_experience >= :{param}")
            all_params[param] = filters.experience_min
        
        if filters.experience_max is not None:
            param = self._get_param_name()
            conditions.append(f"e.years_experience <= :{param}")
            all_params[param] = filters.experience_max
        
        if filters.performance_min is not None:
            param = self._get_param_name()
            conditions.append(f"e.performance_score >= :{param}")
            all_params[param] = filters.performance_min
        
        if filters.performance_max is not None:
            param = self._get_param_name()
            conditions.append(f"e.performance_score <= :{param}")
            all_params[param] = filters.performance_max
        
        # Date filters
        if filters.hire_date_from:
            param = self._get_param_name()
            conditions.append(f"e.hire_date >= :{param}")
            all_params[param] = filters.hire_date_from
        
        if filters.hire_date_to:
            param = self._get_param_name()
            conditions.append(f"e.hire_date <= :{param}")
            all_params[param] = filters.hire_date_to
        
        # Text search
        if filters.search_term:
            param = self._get_param_name()
            search_pattern = f"%{filters.search_term}%"
            conditions.append(
                f"(e.first_name ILIKE :{param} OR "
                f"e.last_name ILIKE :{param} OR "
                f"e.employee_id ILIKE :{param} OR "
                f"e.email_address ILIKE :{param})"
            )
            all_params[param] = search_pattern
        
        # Manager filter
        if filters.manager_id:
            param = self._get_param_name()
            conditions.append(f"e.manager_id = :{param}")
            all_params[param] = filters.manager_id
        
        if conditions:
            where_clause = " AND ".join(conditions)
            return f"WHERE {where_clause}", all_params
        
        return "", {}
    
    def build_select_query(
        self,
        filters: EmployeeFilter,
        columns: List[str] = None,
        order_by: str = "employee_id",
        order_dir: str = "ASC",
        limit: int = None,
        offset: int = None
    ) -> SQLQuery:
        """Build complete SELECT query"""
        # Default columns
        if not columns:
            columns = ["*"]
        
        cols = ", ".join([
            self._get_column(c) if c != "*" else "e.*"
            for c in columns
        ])
        
        where_clause, params = self.build_where_clause(filters)
        
        sql = f"SELECT {cols} FROM employees e {where_clause}"
        
        # Ordering
        if order_by:
            order_col = self._get_column(order_by) if order_by in self.FIELD_MAPPING else "e.employee_id"
            sql += f" ORDER BY {order_col} {order_dir}"
        
        # Pagination
        if limit:
            sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"
        
        return SQLQuery(
            sql=sql,
            parameters=params,
            tables=["employees"]
        )
    
    def build_aggregate_query(
        self,
        filters: EmployeeFilter,
        group_by: str,
        aggregations: List[str] = None
    ) -> SQLQuery:
        """Build aggregate query"""
        where_clause, params = self.build_where_clause(filters)
        
        group_col = self._get_column(group_by)
        
        # Default aggregations
        if not aggregations:
            aggregations = ["COUNT(*) as count"]
        
        agg_str = ", ".join(aggregations)
        
        sql = f"""
            SELECT {group_col} as dimension, {agg_str}
            FROM employees e
            {where_clause}
            GROUP BY {group_col}
            ORDER BY count DESC
        """
        
        return SQLQuery(
            sql=sql,
            parameters=params,
            tables=["employees"]
        )
    
    def validate_filters(self, filters: EmployeeFilter) -> List[str]:
        """Validate filters and return any errors"""
        errors = []
        
        # Validate filter blocks
        for i, block in enumerate(filters.filter_blocks):
            for j, condition in enumerate(block.conditions):
                if condition.field not in self.FIELD_MAPPING:
                    errors.append(
                        f"Block {i+1}, Condition {j+1}: Invalid field '{condition.field}'"
                    )
                
                if condition.operator == FilterOperator.BETWEEN:
                    if condition.value_end is None:
                        errors.append(
                            f"Block {i+1}, Condition {j+1}: BETWEEN requires value_end"
                        )
        
        # Validate ranges
        if filters.salary_min and filters.salary_max:
            if filters.salary_min > filters.salary_max:
                errors.append("salary_min cannot be greater than salary_max")
        
        if filters.age_min and filters.age_max:
            if filters.age_min > filters.age_max:
                errors.append("age_min cannot be greater than age_max")
        
        if filters.hire_date_from and filters.hire_date_to:
            if filters.hire_date_from > filters.hire_date_to:
                errors.append("hire_date_from cannot be after hire_date_to")
        
        return errors
