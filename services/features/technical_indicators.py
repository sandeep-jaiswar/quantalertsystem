"""
Technical indicators for the Quant Alerts System.

Pure functions for calculating technical indicators used in quantitative strategies.
All functions are stateless and vectorized for performance.
"""

import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Collection of technical indicators for quantitative analysis.
    
    All methods are static and pure functions for maximum testability
    and composability. Uses vectorized operations for performance.
    """
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series (typically close prices)
            period: RSI period (default 14)
            
        Returns:
            RSI values as pandas Series
            
        Raises:
            ValueError: If period is invalid or insufficient data
        """
        if period < 2:
            raise ValueError(f"RSI period must be >= 2, got {period}")
        
        if len(prices) < period + 1:
            raise ValueError(
                f"Insufficient data for RSI calculation. Need {period + 1}, got {len(prices)}"
            )
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses using Wilder's smoothing
        avg_gains = gains.ewm(alpha=1/period, adjust=False).mean()
        avg_losses = losses.ewm(alpha=1/period, adjust=False).mean()
        
        # Calculate relative strength
        rs = avg_gains / avg_losses
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def sma(prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).
        
        Args:
            prices: Price series
            period: Moving average period
            
        Returns:
            SMA values as pandas Series
        """
        if period < 1:
            raise ValueError(f"SMA period must be >= 1, got {period}")
            
        return prices.rolling(window=period, min_periods=period).mean()
    
    @staticmethod
    def ema(prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            prices: Price series
            period: EMA period
            
        Returns:
            EMA values as pandas Series
        """
        if period < 1:
            raise ValueError(f"EMA period must be >= 1, got {period}")
            
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def bollinger_bands(
        prices: pd.Series, 
        period: int = 20, 
        num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Price series
            period: Moving average period (default 20)
            num_std: Number of standard deviations (default 2.0)
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if period < 2:
            raise ValueError(f"Bollinger Bands period must be >= 2, got {period}")
            
        if num_std <= 0:
            raise ValueError(f"Standard deviation multiplier must be > 0, got {num_std}")
        
        # Middle band (SMA)
        middle = TechnicalIndicators.sma(prices, period)
        
        # Calculate rolling standard deviation
        std = prices.rolling(window=period, min_periods=period).std()
        
        # Upper and lower bands
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return upper, middle, lower
    
    @staticmethod
    def macd(
        prices: pd.Series, 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Price series
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line EMA period (default 9)
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        if fast >= slow:
            raise ValueError(f"Fast period ({fast}) must be < slow period ({slow})")
            
        # Calculate EMAs
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            period: ATR period (default 14)
            
        Returns:
            ATR values as pandas Series
        """
        if period < 1:
            raise ValueError(f"ATR period must be >= 1, got {period}")
            
        # Calculate true range components
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        
        # True range is the maximum of the three
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR is the smoothed average of true range
        atr = true_range.ewm(alpha=1/period, adjust=False).mean()
        
        return atr
    
    @staticmethod
    def stochastic(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            k_period: %K period (default 14)
            d_period: %D smoothing period (default 3)
            
        Returns:
            Tuple of (%K, %D)
        """
        if k_period < 1 or d_period < 1:
            raise ValueError("Stochastic periods must be >= 1")
        
        # Calculate %K
        lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
        highest_high = high.rolling(window=k_period, min_periods=k_period).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        
        # Calculate %D (smoothed %K)
        d_percent = k_percent.rolling(window=d_period, min_periods=d_period).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def williams_r(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Williams %R.
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            period: Lookback period (default 14)
            
        Returns:
            Williams %R values as pandas Series
        """
        if period < 1:
            raise ValueError(f"Williams %R period must be >= 1, got {period}")
        
        highest_high = high.rolling(window=period, min_periods=period).max()
        lowest_low = low.rolling(window=period, min_periods=period).min()
        
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        
        return williams_r
    
    @staticmethod
    def vwap(prices: pd.Series, volumes: pd.Series) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).
        
        Args:
            prices: Price series (typically close or typical price)
            volumes: Volume series
            
        Returns:
            VWAP values as pandas Series
        """
        cumulative_pv = (prices * volumes).cumsum()
        cumulative_volume = volumes.cumsum()
        
        # Avoid division by zero
        vwap = cumulative_pv / cumulative_volume.replace(0, np.nan)
        
        return vwap
    
    @staticmethod
    def money_flow_index(
        high: pd.Series,
        low: pd.Series, 
        close: pd.Series,
        volume: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Money Flow Index (MFI).
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            volume: Volume series
            period: MFI period (default 14)
            
        Returns:
            MFI values as pandas Series
        """
        if period < 1:
            raise ValueError(f"MFI period must be >= 1, got {period}")
        
        # Calculate typical price
        typical_price = (high + low + close) / 3
        
        # Calculate money flow
        money_flow = typical_price * volume
        
        # Determine positive and negative money flow
        price_change = typical_price.diff()
        positive_flow = money_flow.where(price_change > 0, 0)
        negative_flow = money_flow.where(price_change < 0, 0)
        
        # Calculate rolling sums
        positive_mf = positive_flow.rolling(window=period, min_periods=period).sum()
        negative_mf = negative_flow.rolling(window=period, min_periods=period).sum()
        
        # Calculate money flow ratio and MFI
        mf_ratio = positive_mf / negative_mf.replace(0, np.nan)
        mfi = 100 - (100 / (1 + mf_ratio))
        
        return mfi