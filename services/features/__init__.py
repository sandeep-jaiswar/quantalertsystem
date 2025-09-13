"""
Feature engineering service for the Quant Alerts System.

This module handles technical indicator calculation and feature engineering
with proper validation and performance optimization.
"""

from .technical_indicators import TechnicalIndicators
from .feature_engine import FeatureEngine

__all__ = ["TechnicalIndicators", "FeatureEngine"]