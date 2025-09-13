"""Performance benchmarks for the system."""

import pandas as pd
import pytest
from services.features.technical_indicators import TechnicalIndicators


@pytest.mark.performance
def test_rsi_calculation_performance(benchmark):
    """Benchmark RSI calculation performance."""
    data = pd.DataFrame({
        'close': [100 + i * 0.5 for i in range(1000)]
    })
    
    indicators = TechnicalIndicators()
    
    def calculate_rsi():
        return indicators.rsi(data['close'], period=14)
    
    result = benchmark(calculate_rsi)
    assert len(result) == len(data)


@pytest.mark.performance 
def test_moving_average_performance(benchmark):
    """Benchmark moving average calculation performance."""
    data = pd.DataFrame({
        'close': [100 + i * 0.1 for i in range(5000)]
    })
    
    indicators = TechnicalIndicators()
    
    def calculate_sma():
        return indicators.sma(data['close'], period=20)
    
    result = benchmark(calculate_sma)
    assert len(result) == len(data)