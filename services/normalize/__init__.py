"""
Data normalization service for the Quant Alerts System.

This module handles data cleaning, split adjustments, and dividend adjustments
to ensure consistent and accurate market data.
"""

from .data_normalizer import DataNormalizer

__all__ = ["DataNormalizer"]