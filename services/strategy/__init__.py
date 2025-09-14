"""
Strategy service for the Quant Alerts System.

This module contains all quantitative trading strategies with proper
encapsulation, validation, and composability.
"""

from .base import BaseStrategy
from .technical import RSIMeanReversionStrategy, MovingAverageCrossoverStrategy, BollingerBandSqueezeStrategy
from .manager import StrategyManager

__all__ = [
    "BaseStrategy",
    "RSIMeanReversionStrategy", 
    "MovingAverageCrossoverStrategy",
    "BollingerBandSqueezeStrategy",
    "StrategyManager"
]