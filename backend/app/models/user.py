"""
User and authentication models
"""

from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, 
    ForeignKey, Table, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


# Many-to-many association table for User-Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'))
)


class Role(Base):
    """User roles for RBAC"""
    
    __tablename__ = "roles"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Permissions stored as JSON
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    users = relationship(
        "User", 
        secondary=user_roles, 
        back_populates="roles"
    )
    
    def __repr__(self):
        return f"<Role {self.name}>"


class User(Base):
    """System users for authentication"""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Authentication
    username: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Link to employee record (if applicable)
    employee_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        ForeignKey("employees.employee_id", ondelete="SET NULL")
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Security
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    roles = relationship(
        "Role", 
        secondary=user_roles, 
        back_populates="users"
    )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def role_names(self) -> List[str]:
        return [role.name for role in self.roles]
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        
        for role in self.roles:
            perms = role.permissions.get("permissions", [])
            if permission in perms or "*" in perms:
                return True
        return False
    
    def __repr__(self):
        return f"<User {self.username}>"


# Alias for backwards compatibility
UserRole = user_roles
