"""
Feature engineering engine for the Quant Alerts System.

Orchestrates technical indicator calculation and feature engineering
with proper data validation and performance optimization.
"""

import logging
from typing import Dict, List, Optional

import pandas as pd

from models.market_data import MarketData
from .technical_indicators import TechnicalIndicators


logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    Feature engineering engine for quantitative analysis.
    
    Combines multiple technical indicators and engineered features
    into a comprehensive dataset for strategy analysis.
    """
    
    def __init__(self):
        """Initialize feature engine."""
        self.indicators = TechnicalIndicators()
        
    def calculate_features(self, market_data: MarketData) -> pd.DataFrame:
        """
        Calculate all features for market data.
        
        Args:
            market_data: MarketData object
            
        Returns:
            DataFrame with OHLCV data and calculated features
        """
        # Convert to DataFrame
        df = market_data.to_dataframe()
        
        # Calculate technical indicators
        df = self._add_price_features(df)
        df = self._add_momentum_indicators(df)
        df = self._add_volatility_indicators(df)
        df = self._add_volume_indicators(df)
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price-based features."""
        # Moving averages
        df['sma_20'] = self.indicators.sma(df['Close'], 20)
        df['sma_50'] = self.indicators.sma(df['Close'], 50)
        df['ema_12'] = self.indicators.ema(df['Close'], 12)
        df['ema_26'] = self.indicators.ema(df['Close'], 26)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.indicators.bollinger_bands(df['Close'])
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        df['bb_width'] = (bb_upper - bb_lower) / bb_middle
        df['bb_position'] = (df['Close'] - bb_lower) / (bb_upper - bb_lower)
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based indicators."""
        # RSI
        df['rsi'] = self.indicators.rsi(df['Close'])
        
        # MACD
        macd, signal, histogram = self.indicators.macd(df['Close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_histogram'] = histogram
        
        # Stochastic
        k_percent, d_percent = self.indicators.stochastic(
            df['High'], df['Low'], df['Close']
        )
        df['stoch_k'] = k_percent
        df['stoch_d'] = d_percent
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based indicators."""
        # ATR
        df['atr'] = self.indicators.atr(df['High'], df['Low'], df['Close'])
        
        # True Range
        tr1 = df['High'] - df['Low']
        tr2 = (df['High'] - df['Close'].shift(1)).abs()
        tr3 = (df['Low'] - df['Close'].shift(1)).abs()
        df['true_range'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators."""
        # Volume SMA
        df['volume_sma'] = self.indicators.sma(df['Volume'], 20)
        
        # VWAP
        df['vwap'] = self.indicators.vwap(df['Close'], df['Volume'])
        
        # Money Flow Index
        df['mfi'] = self.indicators.money_flow_index(
            df['High'], df['Low'], df['Close'], df['Volume']
        )
        
        return df