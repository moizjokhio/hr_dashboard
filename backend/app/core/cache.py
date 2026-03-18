"""
Redis caching service with async support
Implements caching strategies for API responses and computed data
"""

import json
import hashlib
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings


T = TypeVar('T')


class CacheService:
    """
    Redis-based caching service with async support
    
    Features:
    - Automatic JSON serialization
    - Key namespacing
    - TTL management
    - Cache invalidation patterns
    """
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self.prefix = "hr_analytics"
    
    async def connect(self):
        """Initialize Redis connection pool"""
        self.pool = ConnectionPool.from_url(
            settings.redis.REDIS_URL,
            max_connections=50,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        await self.client.ping()
    
    async def disconnect(self):
        """Close Redis connections"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
    
    def _make_key(self, key: str) -> str:
        """Create namespaced cache key"""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.client:
            return None
            
        try:
            full_key = self._make_key(key)
            value = await self.client.get(full_key)
            
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default from settings)
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
            
        try:
            full_key = self._make_key(key)
            ttl = ttl or settings.redis.CACHE_TTL
            
            serialized = json.dumps(value, default=str)
            await self.client.setex(full_key, ttl, serialized)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        full_key = self._make_key(key)
        await self.client.delete(full_key)
        return True
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Glob pattern (e.g., "employees:*")
            
        Returns:
            Number of deleted keys
        """
        full_pattern = self._make_key(pattern)
        cursor = 0
        deleted = 0
        
        while True:
            cursor, keys = await self.client.scan(
                cursor=cursor,
                match=full_pattern,
                count=100
            )
            
            if keys:
                await self.client.delete(*keys)
                deleted += len(keys)
            
            if cursor == 0:
                break
        
        return deleted
    
    async def invalidate_employee_cache(self, employee_id: Optional[str] = None):
        """Invalidate employee-related cache entries"""
        if employee_id:
            await self.delete(f"employee:{employee_id}")
            await self.delete_pattern(f"employee:{employee_id}:*")
        else:
            await self.delete_pattern("employee:*")
            await self.delete_pattern("analytics:*")
    
    async def invalidate_analytics_cache(self):
        """Invalidate all analytics cache"""
        await self.delete_pattern("analytics:*")
        await self.delete_pattern("dashboard:*")


# Singleton instance
cache_service = CacheService()


def cache_key_builder(*args, **kwargs) -> str:
    """Build cache key from function arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Callable[..., str] = None
):
    """
    Decorator for caching async function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key
        
    Usage:
        @cached(prefix="employees", ttl=300)
        async def get_employees(department: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                key = f"{prefix}:{cache_key_builder(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = await cache_service.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class CacheInvalidator:
    """Helper for batch cache invalidation"""
    
    def __init__(self):
        self.keys_to_delete = []
        self.patterns_to_delete = []
    
    def add_key(self, key: str):
        self.keys_to_delete.append(key)
        return self
    
    def add_pattern(self, pattern: str):
        self.patterns_to_delete.append(pattern)
        return self
    
    async def execute(self):
        """Execute all invalidations"""
        for key in self.keys_to_delete:
            await cache_service.delete(key)
        
        for pattern in self.patterns_to_delete:
            await cache_service.delete_pattern(pattern)
