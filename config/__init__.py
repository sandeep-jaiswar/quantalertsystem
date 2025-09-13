"""
Configuration management for the Quant Alerts System.

Centralized configuration with environment-based settings following
the manifesto principles of strict configuration discipline.
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]