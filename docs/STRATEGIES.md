# Trading Strategies Documentation

This document provides detailed information about the quantitative trading strategies implemented in the system.

## Overview

The system implements three complementary strategies designed to capture different market conditions:

1. **RSI Mean Reversion**: Captures oversold/overbought opportunities
2. **Moving Average Crossover**: Identifies trend changes
3. **Bollinger Band Squeeze**: Detects volatility breakouts

## 1. RSI Mean Reversion Strategy

### Concept
The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and magnitude of price changes. This strategy identifies potential reversal points when assets become oversold or overbought.

### Implementation
- **RSI Period**: 14 (default)
- **Oversold Threshold**: 30
- **Overbought Threshold**: 70
- **Trend Filter**: 20-period SMA

### Signal Generation
- **BUY Signal**: RSI crosses above 30 + price above 20-day SMA
- **SELL Signal**: RSI crosses below 70 + price below 20-day SMA

### Confidence Scoring
Confidence is calculated based on how far the RSI was from the threshold:
```
confidence = min(0.9, abs(previous_rsi - threshold) / 10)
```

### Best Market Conditions
- Sideways/ranging markets
- High volatility periods
- Strong support/resistance levels

## 2. Moving Average Crossover Strategy

### Concept
This strategy identifies trend changes by monitoring the relationship between short-term and long-term moving averages.

### Implementation
- **Short Period**: 20 (default)
- **Long Period**: 50 (default)
- **Volume Confirmation**: 1.2x average volume
- **MACD Confirmation**: Additional trend validation

### Signal Generation
- **BUY Signal (Golden Cross)**: Short MA crosses above Long MA + volume confirmation
- **SELL Signal (Death Cross)**: Short MA crosses below Long MA + volume confirmation

### Confidence Scoring
```
confidence = min(0.9, abs(short_ma - long_ma) / long_ma)
```

### Best Market Conditions
- Trending markets
- Clear directional movements
- Strong volume participation

## 3. Bollinger Band Squeeze Strategy

### Concept
Bollinger Bands measure volatility and identify potential breakout opportunities. The "squeeze" occurs when volatility contracts, often preceding significant price movements.

### Implementation
- **Period**: 20
- **Standard Deviation**: 2
- **Squeeze Detection**: Band width in bottom 20th percentile
- **RSI Confirmation**: Additional momentum validation

### Signal Generation
- **BUY Signal**: Price breaks above upper band after squeeze + RSI < 70
- **SELL Signal**: Price breaks below lower band after squeeze + RSI > 30
- **Mean Reversion**: Price touches lower band in uptrend

### Confidence Scoring
- **Breakout signals**: Based on distance from band
- **Mean reversion**: Fixed at 0.6 (lower confidence)

### Best Market Conditions
- Low volatility periods followed by breakouts
- Earnings announcements
- News-driven movements

## Strategy Combination

### Consensus Signals
The system generates consensus signals when multiple strategies agree:
- **Minimum Strategies**: 2 (configurable)
- **Minimum Confidence**: 0.5 (configurable)
- **Weighting**: Equal weight for all strategies

### Signal Prioritization
1. **Consensus signals** (highest priority)
2. **High-confidence individual signals** (>80%)
3. **Summary alerts** for multiple moderate signals

## Technical Indicators Used

### Primary Indicators
- **RSI**: Relative Strength Index
- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **Bollinger Bands**: Volatility bands
- **MACD**: Moving Average Convergence Divergence

### Supporting Indicators
- **Volume SMA**: Volume trend analysis
- **%B**: Position within Bollinger Bands
- **Band Width**: Volatility measurement

## Risk Management

### Built-in Filters
1. **Trend Confirmation**: Multiple timeframe analysis
2. **Volume Validation**: Ensures institutional participation
3. **Volatility Context**: Adapts to market conditions
4. **Multiple Strategy Confirmation**: Reduces false signals

### Confidence Thresholds
- **High Confidence**: >80% - Individual alerts
- **Medium Confidence**: 60-80% - Summary inclusion
- **Low Confidence**: <60% - Logged but not alerted

## Performance Characteristics

### Expected Performance
- **Win Rate**: 55-65% (strategy dependent)
- **Risk/Reward**: 1:1.5 average
- **Drawdown**: <15% typical
- **Frequency**: 2-5 signals per symbol per month

### Market Sensitivity
- **Bull Markets**: MA Crossover performs best
- **Bear Markets**: RSI Mean Reversion excels
- **Volatile Markets**: Bollinger Bands optimal
- **Sideways Markets**: RSI and Bollinger combination

## Customization

### Parameters
All strategy parameters are configurable via environment variables:
```env
RSI_PERIOD=14
MA_SHORT=20
MA_LONG=50
MIN_CONFIDENCE=0.6
```

### Adding New Strategies
1. Inherit from `BaseStrategy`
2. Implement `calculate_indicators()`
3. Implement `generate_signals()`
4. Add to `StrategyManager`
5. Write tests

### Example Custom Strategy
```python
class CustomStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("Custom Strategy", **kwargs)
    
    def calculate_indicators(self, data):
        # Add your indicators
        data['custom_indicator'] = your_calculation(data)
        return data
    
    def generate_signals(self, data):
        # Generate signals
        data['signal'] = your_signal_logic(data)
        data['confidence'] = your_confidence_calculation(data)
        return data
```

## Backtesting

### Historical Performance
The system includes backtesting capabilities for strategy validation:
- **Data Range**: Up to 10 years historical data
- **Metrics**: Sharpe ratio, maximum drawdown, win rate
- **Benchmark**: S&P 500 comparison

### Validation Process
1. **Out-of-sample testing**: 70/30 split
2. **Walk-forward analysis**: Rolling windows
3. **Monte Carlo simulation**: Multiple scenarios
4. **Transaction cost adjustment**: Real-world conditions

## Disclaimer

**Important**: These strategies are for educational purposes only. Past performance does not guarantee future results. Always do your own research and consider your risk tolerance before making investment decisions.