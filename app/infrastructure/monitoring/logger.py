"""
ONI v2.0 - Structured Logging Configuration
"""
import logging
import sys
from typing import Any

import structlog
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog processors
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        add_log_level,
        TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add JSON renderer for production, console for development
    processors.append(JSONRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Optional logger name
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
