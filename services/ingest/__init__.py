"""
Data ingestion service for the Quant Alerts System.

This module handles data ingestion from external sources with proper
error handling, retries, and data validation.
"""

from .yahoo_finance import YahooFinanceIngester
from .base import BaseIngester, IngestionError

__all__ = ["YahooFinanceIngester", "BaseIngester", "IngestionError"]