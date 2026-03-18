"""
Logging configuration using Loguru
Enterprise-grade structured logging with rotation and retention
"""

import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings


def setup_logging():
    """
    Configure application logging with Loguru
    
    Features:
    - Structured JSON logging for production
    - Console logging for development
    - File rotation and retention
    - Request ID tracking
    - Performance timing
    """
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    log_dir = Path(settings.app.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Console handler for development
    if settings.app.DEBUG:
        logger.add(
            sys.stdout,
            format=settings.app.LOG_FORMAT,
            level="DEBUG",
            colorize=True
        )
    else:
        # Structured JSON for production
        logger.add(
            sys.stdout,
            format="{message}",
            level=settings.app.LOG_LEVEL,
            serialize=True
        )
    
    # File handler with rotation
    logger.add(
        settings.app.LOG_FILE,
        format=settings.app.LOG_FORMAT,
        level=settings.app.LOG_LEVEL,
        rotation=settings.app.LOG_ROTATION,
        retention=settings.app.LOG_RETENTION,
        compression="zip",
        enqueue=True  # Thread-safe logging
    )
    
    # Error-specific log file
    error_log = Path(settings.app.LOG_FILE).parent / "errors.log"
    logger.add(
        str(error_log),
        format=settings.app.LOG_FORMAT,
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        enqueue=True
    )
    
    logger.info(f"Logging configured. Environment: {settings.app.ENVIRONMENT}")
    
    return logger


# Request context for logging
class LogContext:
    """Context manager for adding request context to logs"""
    
    def __init__(self, request_id: str, user_id: str = None):
        self.request_id = request_id
        self.user_id = user_id
        
    def __enter__(self):
        self.context = logger.bind(
            request_id=self.request_id,
            user_id=self.user_id
        )
        return self.context
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Audit logger for sensitive operations
audit_logger = logger.bind(audit=True)


def log_audit_event(
    action: str,
    user_id: str,
    resource: str,
    resource_id: str,
    details: dict = None
):
    """
    Log audit event for compliance tracking
    
    Args:
        action: Action performed (CREATE, UPDATE, DELETE, VIEW, EXPORT)
        user_id: ID of user performing action
        resource: Resource type (employee, report, etc.)
        resource_id: ID of affected resource
        details: Additional context
    """
    audit_logger.info(
        f"AUDIT: {action}",
        action=action,
        user_id=user_id,
        resource=resource,
        resource_id=resource_id,
        details=details or {}
    )
