"""Logging configuration for the quantitative alerting system."""

import logging
import sys
from pathlib import Path
from typing import Optional
from ..config import settings


def setup_logger(
    name: str = "quantalertsystem",
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """Set up logger with console and file handlers."""
    
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Set logging level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        file_handler = logging.FileHandler(f"logs/{log_file}")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = setup_logger(log_file="quant_alerts.log")