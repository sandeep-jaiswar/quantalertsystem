"""
Yahoo Finance ingestion service for the Quant Alerts System.

Provides market data ingestion from Yahoo Finance with proper error handling,
data validation, and retry logic.
"""

import logging
from datetime import datetime
from typing import List

import pandas as pd
import yfinance as yf

from models.market_data import MarketData
from .base import BaseIngester, IngestionError


logger = logging.getLogger(__name__)


class YahooFinanceIngester(BaseIngester):
    """
    Yahoo Finance data ingester with robust error handling and validation.
    
    Fetches OHLCV data from Yahoo Finance with automatic retries,
    data validation, and proper error reporting.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize Yahoo Finance ingester.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
        """
        super().__init__(max_retries, retry_delay)
        
    def fetch_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> List[MarketData]:
        """
        Fetch market data from Yahoo Finance.
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'MSFT'])
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional yfinance parameters
            
        Returns:
            List of MarketData objects for each symbol
            
        Raises:
            IngestionError: If data fetching fails
        """
        # Validate inputs
        self.validate_symbols(symbols)
        self.validate_date_range(start_date, end_date)
        
        results = []
        failed_symbols = []
        
        for symbol in symbols:
            try:
                logger.debug(f"Fetching data for {symbol}")
                market_data = self._fetch_single_symbol(
                    symbol, start_date, end_date, **kwargs
                )
                
                # Validate the fetched data
                self.validate_market_data(market_data)
                results.append(market_data)
                
                logger.info(
                    f"Successfully fetched {market_data.length} data points for {symbol}"
                )
                
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                failed_symbols.append(symbol)
                continue
        
        if not results and failed_symbols:
            raise IngestionError(
                f"Failed to fetch data for all symbols: {failed_symbols}"
            )
        
        if failed_symbols:
            logger.warning(f"Failed to fetch data for some symbols: {failed_symbols}")
        
        return results
    
    def _fetch_single_symbol(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> MarketData:
        """
        Fetch data for a single symbol from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            **kwargs: Additional yfinance parameters
            
        Returns:
            MarketData object
            
        Raises:
            IngestionError: If fetching fails
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            df = ticker.history(
                start=start_date,
                end=end_date,
                **kwargs
            )
            
            if df.empty:
                raise IngestionError(f"No data returned for {symbol}")
            
            # Check for required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise IngestionError(
                    f"Missing columns for {symbol}: {missing_columns}"
                )
            
            # Clean the data
            df = self._clean_dataframe(df, symbol)
            
            # Convert to MarketData
            market_data = MarketData.from_dataframe(symbol, df)
            
            return market_data
            
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(f"Yahoo Finance API error for {symbol}: {e}") from e
    
    def _clean_dataframe(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and validate DataFrame from Yahoo Finance.
        
        Args:
            df: Raw DataFrame from yfinance
            symbol: Stock symbol for error reporting
            
        Returns:
            Cleaned DataFrame
            
        Raises:
            IngestionError: If data is invalid or cannot be cleaned
        """
        try:
            # Make a copy to avoid modifying original
            df = df.copy()
            
            # Remove timezone info from index if present
            if hasattr(df.index, 'tz') and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            # Check for missing data
            if df.isnull().any().any():
                logger.warning(f"Found missing data for {symbol}, forward filling")
                df = df.fillna(method='ffill')
                
                # If still have NaNs after forward fill, drop them
                if df.isnull().any().any():
                    initial_length = len(df)
                    df = df.dropna()
                    logger.warning(
                        f"Dropped {initial_length - len(df)} rows with NaN values for {symbol}"
                    )
            
            # Validate price data consistency
            invalid_rows = (
                (df['High'] < df['Low']) |
                (df['Open'] < 0) | (df['High'] < 0) | 
                (df['Low'] < 0) | (df['Close'] < 0) |
                (df['Volume'] < 0)
            )
            
            if invalid_rows.any():
                logger.warning(
                    f"Found {invalid_rows.sum()} invalid rows for {symbol}, removing"
                )
                df = df[~invalid_rows]
            
            # Sort by date
            df = df.sort_index()
            
            # Ensure we have minimum amount of data
            if len(df) < 10:
                raise IngestionError(
                    f"Insufficient data for {symbol}: only {len(df)} valid rows"
                )
            
            return df
            
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(f"Failed to clean data for {symbol}: {e}") from e
    
    def get_info(self, symbol: str) -> dict:
        """
        Get company information for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company info
            
        Raises:
            IngestionError: If info retrieval fails
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key information
            return {
                'symbol': symbol,
                'company_name': info.get('longName', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown')
            }
            
        except Exception as e:
            raise IngestionError(f"Failed to get info for {symbol}: {e}") from e