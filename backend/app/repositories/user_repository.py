"""
User repository
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username with roles loaded"""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.get_by_field("email", email)
    
    async def get_with_roles(self, user_id: UUID) -> Optional[User]:
        """Get user with roles loaded"""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self, limit: int = 100) -> List[User]:
        """Get all active users"""
        result = await self.session.execute(
            select(User)
            .where(User.is_active == True)
            .order_by(User.username)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def increment_failed_logins(self, user_id: UUID) -> int:
        """Increment failed login count"""
        user = await self.get_by_id(user_id)
        if user:
            user.failed_login_attempts += 1
            await self.session.flush()
            return user.failed_login_attempts
        return 0
    
    async def reset_failed_logins(self, user_id: UUID):
        """Reset failed login count"""
        await self.update(user_id, {"failed_login_attempts": 0, "locked_until": None})


class RoleRepository(BaseRepository[Role]):
    """Repository for role operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return await self.get_by_field("name", name)
    
    async def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        result = await self.session.execute(
            select(Role).order_by(Role.name)
        )
        return list(result.scalars().all())
