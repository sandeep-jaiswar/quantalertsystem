"""Base strategy class for quantitative trading strategies."""

from abc import ABC, abstractmethod
import logging
import pandas as pd
from typing import Dict, Any, Optional, Tuple


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.params = kwargs
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the strategy."""
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on strategy logic."""
        pass
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Complete analysis pipeline for the strategy.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with analysis results
        """
        try:
            # Calculate indicators
            data_with_indicators = self.calculate_indicators(data.copy())
            
            # Generate signals
            data_with_signals = self.generate_signals(data_with_indicators)
            
            # Get latest signal
            latest_signal = self._get_latest_signal(data_with_signals)
            
            return {
                'strategy': self.name,
                'symbol': data['symbol'].iloc[0] if 'symbol' in data.columns else 'Unknown',
                'latest_signal': latest_signal,
                'data': data_with_signals,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error in {self.name} strategy analysis: {str(e)}")
            return {
                'strategy': self.name,
                'symbol': data['symbol'].iloc[0] if 'symbol' in data.columns else 'Unknown',
                'latest_signal': None,
                'data': None,
                'success': False,
                'error': str(e)
            }
    
    def _get_latest_signal(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Extract the latest signal from the data."""
        if data.empty or 'signal' not in data.columns:
            return None
        
        # Get the most recent non-null signal
        latest_row = data.dropna(subset=['signal']).tail(1)
        
        if latest_row.empty:
            return None
        
        row = latest_row.iloc[0]
        
        return {
            'date': row.get('date'),
            'signal': row.get('signal'),
            'confidence': row.get('confidence', 0.0),
            'price': row.get('close', 0.0),
            'indicators': self._extract_indicators(row)
        }
    
    def _extract_indicators(self, row: pd.Series) -> Dict[str, float]:
        """Extract indicator values from a data row."""
        indicators = {}
        
        # Common indicators to extract
        indicator_columns = [
            'rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'bb_middle',
            'sma_short', 'sma_long', 'ema_short', 'ema_long', 'volume_sma'
        ]
        
        for col in indicator_columns:
            if col in row.index and pd.notna(row[col]):
                indicators[col] = float(row[col])
        
        return indicators
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data has required columns."""
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        if data.empty:
            self.logger.error("Data is empty")
            return False
        
        return True