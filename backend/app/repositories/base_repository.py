"""
Base repository pattern implementation
Provides common database operations
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository base class implementing common CRUD operations
    
    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get single record by primary key"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get all records with pagination"""
        query = select(self.model)
        
        if order_by and hasattr(self.model, order_by):
            order_col = getattr(self.model, order_by)
            query = query.order_by(order_col.desc() if order_desc else order_col)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_field(
        self,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """Get single record by field value"""
        if not hasattr(self.model, field):
            raise ValueError(f"Model has no field: {field}")
        
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
    
    async def get_many_by_field(
        self,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by field value"""
        if not hasattr(self.model, field):
            raise ValueError(f"Model has no field: {field}")
        
        result = await self.session.execute(
            select(self.model)
            .where(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_ids(self, ids: List[UUID]) -> List[ModelType]:
        """Get multiple records by IDs"""
        result = await self.session.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def create_many(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records"""
        db_objs = [self.model(**obj) for obj in objects]
        self.session.add_all(db_objs)
        await self.session.flush()
        return db_objs
    
    async def update(
        self,
        id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update record by ID"""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update_by_field(
        self,
        field: str,
        value: Any,
        obj_in: Dict[str, Any]
    ) -> int:
        """Update records matching field value"""
        if not hasattr(self.model, field):
            raise ValueError(f"Model has no field: {field}")
        
        result = await self.session.execute(
            update(self.model)
            .where(getattr(self.model, field) == value)
            .values(**obj_in)
        )
        return result.rowcount
    
    async def delete(self, id: UUID) -> bool:
        """Delete record by ID"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
    
    async def delete_by_field(self, field: str, value: Any) -> int:
        """Delete records matching field value"""
        if not hasattr(self.model, field):
            raise ValueError(f"Model has no field: {field}")
        
        result = await self.session.execute(
            delete(self.model).where(getattr(self.model, field) == value)
        )
        return result.rowcount
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filters"""
        query = select(func.count()).select_from(self.model)
        
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(self, field: str, value: Any) -> bool:
        """Check if record exists by field value"""
        count = await self.count({field: value})
        return count > 0
    
    async def execute_raw(self, query: str, params: Dict[str, Any] = None):
        """Execute raw SQL query"""
        from sqlalchemy import text
        result = await self.session.execute(text(query), params or {})
        return result
