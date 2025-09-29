"""Tests for trading strategies."""

import pytest
import pandas as pd
import numpy as np
from services.strategy.technical import (
    RSIMeanReversionStrategy,
    MovingAverageCrossoverStrategy,
    BollingerBandStrategy
)


@pytest.fixture
def sample_data():
    """Create sample stock data for testing."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    
    # Generate synthetic price data with some trends
    np.random.seed(42)
    base_price = 100
    prices = []
    
    for i in range(100):
        # Add some trend and randomness
        trend = 0.01 if i > 50 else -0.005
        noise = np.random.normal(0, 0.02)
        base_price *= (1 + trend + noise)
        prices.append(base_price)
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 100),
        'symbol': 'TEST'
    })
    
    return data


def test_rsi_strategy(sample_data):
    """Test RSI mean reversion strategy."""
    strategy = RSIMeanReversionStrategy()
    
    # Validate data
    assert strategy.validate_data(sample_data)
    
    # Run analysis
    result = strategy.analyze(sample_data)
    
    assert result['success'] is True
    assert result['strategy'] == 'RSI Mean Reversion'
    assert 'data' in result
    assert 'rsi' in result['data'].columns


def test_ma_crossover_strategy(sample_data):
    """Test moving average crossover strategy."""
    strategy = MovingAverageCrossoverStrategy()
    
    # Validate data
    assert strategy.validate_data(sample_data)
    
    # Run analysis
    result = strategy.analyze(sample_data)
    
    assert result['success'] is True
    assert result['strategy'] == 'MA Crossover'
    assert 'data' in result
    assert 'sma_short' in result['data'].columns
    assert 'sma_long' in result['data'].columns


def test_bollinger_band_strategy(sample_data):
    """Test Bollinger Band strategy."""
    strategy = BollingerBandStrategy()
    
    # Validate data
    assert strategy.validate_data(sample_data)
    
    # Run analysis
    result = strategy.analyze(sample_data)
    
    assert result['success'] is True
    assert result['strategy'] == 'Bollinger Bands'
    assert 'data' in result
    assert 'bb_upper' in result['data'].columns
    assert 'bb_lower' in result['data'].columns


def test_invalid_data():
    """Test strategy behavior with invalid data."""
    strategy = RSIMeanReversionStrategy()
    
    # Test with empty DataFrame
    empty_data = pd.DataFrame()
    assert not strategy.validate_data(empty_data)
    
    # Test with missing columns
    incomplete_data = pd.DataFrame({'date': [1, 2, 3], 'close': [100, 101, 102]})
    assert not strategy.validate_data(incomplete_data)