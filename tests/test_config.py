"""Tests for configuration module."""

import pytest
from quantalertsystem.config import Settings


def test_settings_default_values():
    """Test that settings have sensible defaults."""
    # Mock environment to avoid requiring actual values
    import os
    os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
    os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
    
    settings = Settings()
    
    assert settings.telegram_bot_token == 'test_token'
    assert settings.telegram_chat_id == 'test_chat_id'
    assert settings.lookback_days == 60
    assert settings.rsi_period == 14
    assert settings.ma_short == 20
    assert settings.ma_long == 50


def test_symbols_list():
    """Test symbols list parsing."""
    import os
    os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
    os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
    os.environ['DEFAULT_SYMBOLS'] = 'AAPL, GOOGL, MSFT'
    
    settings = Settings()
    
    assert settings.symbols_list == ['AAPL', 'GOOGL', 'MSFT']