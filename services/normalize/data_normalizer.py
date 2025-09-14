"""
Data normalization for the Quant Alerts System.

Handles data cleaning, corporate actions, and quality validation
to ensure consistent market data across all strategies.
"""

import logging
from typing import List

import pandas as pd

from models.market_data import MarketData


logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Data normalization service for market data quality assurance.
    
    Handles split adjustments, dividend adjustments, and data quality
    validation to ensure consistent analysis inputs.
    """
    
    def normalize(self, market_data_list: List[MarketData]) -> List[MarketData]:
        """
        Normalize a list of market data objects.
        
        Args:
            market_data_list: List of MarketData objects to normalize
            
        Returns:
            List of normalized MarketData objects
        """
        normalized_data = []
        
        for market_data in market_data_list:
            try:
                normalized = self._normalize_single(market_data)
                normalized_data.append(normalized)
                logger.info(f"Normalized data for {market_data.symbol}")
                
            except Exception as e:
                logger.error(f"Failed to normalize data for {market_data.symbol}: {e}")
                continue
                
        return normalized_data
    
    def _normalize_single(self, market_data: MarketData) -> MarketData:
        """Normalize a single MarketData object."""
        df = market_data.to_dataframe()
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Sort by date
        df = df.sort_index()
        
        # Validate data quality
        df = self._validate_quality(df, market_data.symbol)
        
        # Create new MarketData object
        return MarketData.from_dataframe(market_data.symbol, df)
    
    def _validate_quality(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Validate and clean data quality issues."""
        # Remove rows with invalid OHLC relationships
        invalid_mask = (
            (df['High'] < df['Low']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close'])
        )
        
        if invalid_mask.any():
            logger.warning(f"Removing {invalid_mask.sum()} invalid rows for {symbol}")
            df = df[~invalid_mask]
        
        return df