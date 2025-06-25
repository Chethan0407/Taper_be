import structlog
import logging
import sys
from typing import Any, Dict

def configure_logging() -> None:
    """Configure structured logging for the application."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    root_logger.addHandler(console_handler)

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

def log_request(logger: structlog.BoundLogger, request_id: str, method: str, path: str, 
                status_code: int, duration_ms: float, **kwargs: Any) -> None:
    """Log HTTP request details in a structured format."""
    logger.info(
        "http_request",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )

def log_error(logger: structlog.BoundLogger, request_id: str, error: Exception, 
              **kwargs: Any) -> None:
    """Log error details in a structured format."""
    logger.error(
        "error_occurred",
        request_id=request_id,
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs
    )

# Audit log helper
def log_audit_event(
    logger: structlog.BoundLogger,
    event_type: str,
    user_id: int,
    resource_type: str,
    resource_id: int,
    action: str,
    details: Dict[str, Any] = None
) -> None:
    """
    Log an audit event with structured data.
    
    Args:
        logger: The structured logger instance
        event_type: Type of event (e.g., 'spec_update', 'comment_delete')
        user_id: ID of the user performing the action
        resource_type: Type of resource being modified
        resource_id: ID of the resource being modified
        action: Action performed (e.g., 'create', 'update', 'delete')
        details: Additional event details
    """
    logger.info(
        "audit_event",
        event_type=event_type,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        details=details or {}
    )

def setup_logging() -> None:
    """Alias for configure_logging to maintain backward compatibility."""
    configure_logging() 