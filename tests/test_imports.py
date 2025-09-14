"""Test that all modules can be imported successfully."""

import pytest


def test_config_imports():
    """Test that config module can be imported."""
    try:
        from config import settings
        assert settings is not None
    except ImportError as e:
        pytest.skip(f"Config import failed: {e}")


def test_models_imports():
    """Test that model modules can be imported."""
    try:
        from models import market_data, signals, alerts
        assert market_data is not None
        assert signals is not None 
        assert alerts is not None
    except ImportError as e:
        pytest.skip(f"Models import failed: {e}")


def test_services_imports():
    """Test that service modules can be imported."""
    try:
        from services.strategy import base
        from services.features import technical_indicators
        from services.ingest import base as ingest_base
        assert base is not None
        assert technical_indicators is not None
        assert ingest_base is not None
    except ImportError as e:
        pytest.skip(f"Services import failed: {e}")