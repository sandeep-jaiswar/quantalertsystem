"""
Services package for the Quant Alerts System.

This package contains all the core services following the layered architecture:
- ingest: Data ingestion from external sources (Yahoo Finance)
- normalize: Data cleaning, splits, dividends handling
- features: Technical indicators and feature engineering
- strategy: Signal generation and encapsulated strategy logic
- alerts: Notification delivery and persistence

Each service is designed to be stateless, testable, and composable.
"""

__version__ = "1.0.0"