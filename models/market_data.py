"""
Market data models for the Quant Alerts System.

Immutable dataclasses representing market data structures used throughout
the ingestion and processing pipeline.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class MarketDataPoint:
    """
    A single market data observation for a specific symbol and timestamp.
    
    All fields are immutable to ensure data integrity throughout the pipeline.
    """
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adjusted_close: Optional[Decimal] = None
    
    def __post_init__(self) -> None:
        """Validate market data constraints."""
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than low ({self.low})")
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"Open price {self.open} not within high-low range")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"Close price {self.close} not within high-low range")


@dataclass(frozen=True) 
class MarketData:
    """
    Market data container holding a time series of market observations.
    
    Provides immutable access to market data with validation and utility methods.
    """
    symbol: str
    data_points: tuple[MarketDataPoint, ...]
    start_date: datetime
    end_date: datetime
    
    @classmethod
    def from_dataframe(cls, symbol: str, df: pd.DataFrame) -> 'MarketData':
        """
        Create MarketData from a pandas DataFrame.
        
        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV data and datetime index
            
        Returns:
            MarketData instance
            
        Raises:
            ValueError: If DataFrame structure is invalid
        """
        if df.empty:
            raise ValueError(f"DataFrame is empty for symbol {symbol}")
            
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")
        
        data_points = []
        for timestamp, row in df.iterrows():
            point = MarketDataPoint(
                symbol=symbol,
                timestamp=pd.to_datetime(timestamp),
                open=Decimal(str(row['Open'])),
                high=Decimal(str(row['High'])),
                low=Decimal(str(row['Low'])),
                close=Decimal(str(row['Close'])),
                volume=int(row['Volume']),
                adjusted_close=Decimal(str(row.get('Adj Close', row['Close'])))
            )
            data_points.append(point)
        
        return cls(
            symbol=symbol,
            data_points=tuple(data_points),
            start_date=pd.to_datetime(df.index.min()),
            end_date=pd.to_datetime(df.index.max())
        )
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert MarketData to pandas DataFrame.
        
        Returns:
            DataFrame with datetime index and OHLCV columns
        """
        data = []
        for point in self.data_points:
            data.append({
                'timestamp': point.timestamp,
                'Open': float(point.open),
                'High': float(point.high), 
                'Low': float(point.low),
                'Close': float(point.close),
                'Volume': point.volume,
                'Adj Close': float(point.adjusted_close or point.close)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    @property
    def length(self) -> int:
        """Number of data points."""
        return len(self.data_points)
    
    @property
    def is_valid(self) -> bool:
        """Check if market data is valid and non-empty."""
        return len(self.data_points) > 0 and self.start_date <= self.end_date