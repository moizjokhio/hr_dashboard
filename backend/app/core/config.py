"""
HR Analytics System - Core Configuration
Enterprise-grade settings management with validation
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration"""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "hr_admin"
    POSTGRES_PASSWORD: str = "zbfXZpBPyxgEYEVm"
    POSTGRES_DB: str = "hr_analytics"
    
    # Connection pool settings
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 300000
    POOL_RECYCLE: int = 1800
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_prefix = "DB_"
        env_file = ".env"


class RedisSettings(BaseSettings):
    """Redis configuration for caching and task queue"""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour default
    
    @property
    def REDIS_URL(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_prefix = "REDIS_"


class VectorDBSettings(BaseSettings):
    """Qdrant vector database configuration"""
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    COLLECTION_NAME: str = "hr_embeddings"
    EMBEDDING_DIMENSION: int = 1024  # BGE-Large dimension
    
    @property
    def QDRANT_URL(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    class Config:
        env_prefix = "VECTOR_"


class AIModelSettings(BaseSettings):
    """AI/ML model configuration for local inference"""
    # Embedding model
    EMBEDDING_MODEL_PATH: str = "./ml-models/bge-large-en-v1.5"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # LLM model (Qwen2 72B GGUF)
    LLM_MODEL_PATH: str = "./ml-models/qwen2-72b-instruct-q4_k_m.gguf"
    LLM_CONTEXT_LENGTH: int = 8192
    LLM_GPU_LAYERS: int = 80  # Number of layers to offload to GPU
    LLM_THREADS: int = 8
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.1
    
    # Predictive models
    ATTRITION_MODEL_PATH: str = "./ml-models/attrition_model.pkl"
    PERFORMANCE_MODEL_PATH: str = "./ml-models/performance_model.pkl"
    PROMOTION_MODEL_PATH: str = "./ml-models/promotion_model.pkl"
    
    # GPU settings
    CUDA_VISIBLE_DEVICES: str = "0"
    USE_GPU: bool = True
    GPU_MEMORY_FRACTION: float = 0.9

    class Config:
        env_prefix = "AI_"


class SecuritySettings(BaseSettings):
    """Security and authentication configuration"""
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    ALLOWED_HEADERS: List[str] = ["*"]

    class Config:
        env_prefix = "SECURITY_"


class AppSettings(BaseSettings):
    """Main application settings"""
    APP_NAME: str = "HR Analytics System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    LOG_FILE: str = "logs/hr_analytics.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # File upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".pdf"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    class Config:
        env_prefix = "APP_"
        env_file = ".env"


class Settings(BaseSettings):
    """Aggregated settings for the entire application"""
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    vector_db: VectorDBSettings = VectorDBSettings()
    ai: AIModelSettings = AIModelSettings()
    security: SecuritySettings = SecuritySettings()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
