"""
Logging utilities for the Adversarial Sandbox platform.

Provides standardized logging configuration and utilities.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    service_name: str = "adversarial-sandbox",
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Setup standardized logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Name of the service
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            f"[{service_name}] - %(message)s"
        )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get logger for the service
    logger = logging.getLogger(service_name)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

