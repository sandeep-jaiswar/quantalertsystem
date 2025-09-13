"""
Quantitative Alerts System.

A zero-cost quantitative alerting platform for stock trading signals, 
built with investment bank quality architecture and following strict 
engineering principles for transparency, reproducibility, and extensibility.
"""

__version__ = "1.0.0"
__author__ = "Quant Alerts Team"
__description__ = "Zero-cost quantitative alerting system with investment bank quality"

# Core system imports
from .config import get_settings
from .main import QuantAlertsPipeline

__all__ = ["get_settings", "QuantAlertsPipeline"]