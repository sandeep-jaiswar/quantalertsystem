"""
Base ingestion service for the Quant Alerts System.

Abstract base class for all data ingestion services with common functionality
for error handling, retries, and validation.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from models.market_data import MarketData


logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Exception raised during data ingestion."""
    pass


class BaseIngester(ABC):
    """
    Abstract base class for market data ingesters.
    
    Provides common functionality for retries, error handling, and data validation
    while allowing concrete implementations to define their specific ingestion logic.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize base ingester.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    @abstractmethod
    def fetch_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> List[MarketData]:
        """
        Fetch market data for given symbols and date range.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of MarketData objects
            
        Raises:
            IngestionError: If data ingestion fails
        """
        pass
    
    def fetch_with_retry(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> List[MarketData]:
        """
        Fetch data with automatic retry logic.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            List of MarketData objects
            
        Raises:
            IngestionError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Fetching data for {symbols} (attempt {attempt + 1}/{self.max_retries + 1})"
                )
                return self.fetch_data(symbols, start_date, end_date, **kwargs)
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Ingestion attempt {attempt + 1} failed: {e}"
                )
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                
        raise IngestionError(
            f"Failed to fetch data after {self.max_retries + 1} attempts: {last_exception}"
        ) from last_exception
    
    def validate_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """
        Validate date range parameters.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Raises:
            ValueError: If date range is invalid
        """
        if start_date >= end_date:
            raise ValueError(f"Start date {start_date} must be before end date {end_date}")
        
        # Check if end date is not in the future (beyond today)
        today = datetime.now().date()
        if end_date.date() > today:
            raise ValueError(f"End date {end_date.date()} cannot be in the future")
        
        # Check if date range is reasonable (not more than 10 years)
        max_range = timedelta(days=365 * 10)
        if end_date - start_date > max_range:
            raise ValueError(f"Date range cannot exceed 10 years")
    
    def validate_symbols(self, symbols: List[str]) -> None:
        """
        Validate symbol list.
        
        Args:
            symbols: List of stock symbols
            
        Raises:
            ValueError: If symbols are invalid
        """
        if not symbols:
            raise ValueError("Symbol list cannot be empty")
        
        for symbol in symbols:
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"Invalid symbol: {symbol}")
            
            if len(symbol) > 10:  # Reasonable symbol length limit
                raise ValueError(f"Symbol too long: {symbol}")
    
    def validate_market_data(self, market_data: MarketData) -> None:
        """
        Validate fetched market data.
        
        Args:
            market_data: MarketData object to validate
            
        Raises:
            IngestionError: If market data is invalid
        """
        if not market_data.is_valid:
            raise IngestionError(f"Invalid market data for {market_data.symbol}")
        
        if market_data.length == 0:
            raise IngestionError(f"No data fetched for {market_data.symbol}")
        
        # Check for data completeness (no gaps larger than 7 days)
        data_points = sorted(market_data.data_points, key=lambda x: x.timestamp)
        for i in range(1, len(data_points)):
            gap = data_points[i].timestamp - data_points[i-1].timestamp
            if gap.days > 7:
                logger.warning(
                    f"Large gap in data for {market_data.symbol}: "
                    f"{gap.days} days between {data_points[i-1].timestamp} and {data_points[i].timestamp}"
                )