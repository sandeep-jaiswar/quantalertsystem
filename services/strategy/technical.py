"""Technical analysis strategies."""

import pandas as pd
from .base import BaseStrategy


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI-based mean reversion strategy."""
    
    def __init__(self, **kwargs):
        super().__init__("RSI Mean Reversion", **kwargs)
        self.rsi_period = kwargs.get('rsi_period', 14)
        self.oversold_threshold = kwargs.get('oversold_threshold', 30)
        self.overbought_threshold = kwargs.get('overbought_threshold', 70)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and supporting indicators."""
        # Calculate RSI
        data['rsi'] = self._calculate_rsi(data['close'], self.rsi_period)
        
        # Calculate moving averages for trend context
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        
        # Calculate Bollinger Bands for volatility context
        data['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on RSI."""
        data['signal'] = None
        data['confidence'] = 0.0
        
        for i in range(1, len(data)):
            current_rsi = data['rsi'].iloc[i]
            prev_rsi = data['rsi'].iloc[i-1]
            current_price = data['close'].iloc[i]
            sma_20 = data['sma_20'].iloc[i]
            
            if pd.isna(current_rsi) or pd.isna(prev_rsi):
                continue
            
            # Buy signal: RSI crosses above oversold level
            if (current_rsi > self.oversold_threshold and 
                prev_rsi <= self.oversold_threshold and
                current_price > sma_20):  # Additional trend filter
                
                confidence = min(0.9, (self.oversold_threshold - prev_rsi) / 10)
                data.loc[data.index[i], 'signal'] = 'BUY'
                data.loc[data.index[i], 'confidence'] = confidence
            
            # Sell signal: RSI crosses below overbought level
            elif (current_rsi < self.overbought_threshold and 
                  prev_rsi >= self.overbought_threshold and
                  current_price < sma_20):  # Additional trend filter
                
                confidence = min(0.9, (prev_rsi - self.overbought_threshold) / 10)
                data.loc[data.index[i], 'signal'] = 'SELL'
                data.loc[data.index[i], 'confidence'] = confidence
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class MovingAverageCrossoverStrategy(BaseStrategy):
    """Moving average crossover strategy."""
    
    def __init__(self, **kwargs):
        super().__init__("MA Crossover", **kwargs)
        self.short_period = kwargs.get('short_period', 20)
        self.long_period = kwargs.get('long_period', 50)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages and supporting indicators."""
        # Simple moving averages
        data['sma_short'] = data['close'].rolling(window=self.short_period).mean()
        data['sma_long'] = data['close'].rolling(window=self.long_period).mean()
        
        # Exponential moving averages
        data['ema_short'] = data['close'].ewm(span=self.short_period).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_period).mean()
        
        # Volume moving average for confirmation
        data['volume_sma'] = data['volume'].rolling(window=20).mean()
        
        # MACD for additional confirmation
        data['macd'] = data['ema_short'] - data['ema_long']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on moving average crossovers."""
        data['signal'] = None
        data['confidence'] = 0.0
        
        for i in range(1, len(data)):
            current_short = data['sma_short'].iloc[i]
            current_long = data['sma_long'].iloc[i]
            prev_short = data['sma_short'].iloc[i-1]
            prev_long = data['sma_long'].iloc[i-1]
            
            current_volume = data['volume'].iloc[i]
            avg_volume = data['volume_sma'].iloc[i]
            
            if pd.isna(current_short) or pd.isna(current_long):
                continue
            
            # Golden cross: short MA crosses above long MA
            if (current_short > current_long and 
                prev_short <= prev_long and
                current_volume > avg_volume * 1.2):  # Volume confirmation
                
                confidence = min(0.9, abs(current_short - current_long) / current_long)
                data.loc[data.index[i], 'signal'] = 'BUY'
                data.loc[data.index[i], 'confidence'] = confidence
            
            # Death cross: short MA crosses below long MA
            elif (current_short < current_long and 
                  prev_short >= prev_long and
                  current_volume > avg_volume * 1.2):  # Volume confirmation
                
                confidence = min(0.9, abs(current_short - current_long) / current_long)
                data.loc[data.index[i], 'signal'] = 'SELL'
                data.loc[data.index[i], 'confidence'] = confidence
        
        return data


class BollingerBandStrategy(BaseStrategy):
    """Bollinger Band squeeze and breakout strategy."""
    
    def __init__(self, **kwargs):
        super().__init__("Bollinger Bands", **kwargs)
        self.period = kwargs.get('period', 20)
        self.std_multiplier = kwargs.get('std_multiplier', 2)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and related indicators."""
        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(window=self.period).mean()
        bb_std = data['close'].rolling(window=self.period).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * self.std_multiplier)
        data['bb_lower'] = data['bb_middle'] - (bb_std * self.std_multiplier)
        
        # Band width (for squeeze detection)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        # %B indicator
        data['percent_b'] = (data['close'] - data['bb_lower']) / (
            data['bb_upper'] - data['bb_lower']
        )
        
        # RSI for confirmation
        data['rsi'] = self._calculate_rsi(data['close'], 14)
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on Bollinger Band patterns."""
        data['signal'] = None
        data['confidence'] = 0.0
        
        # Calculate band width percentile for squeeze detection
        data['bb_width_percentile'] = data['bb_width'].rolling(window=50).rank(pct=True)
        
        for i in range(1, len(data)):
            current_close = data['close'].iloc[i]
            prev_close = data['close'].iloc[i-1]
            
            bb_upper = data['bb_upper'].iloc[i]
            bb_lower = data['bb_lower'].iloc[i]
            bb_middle = data['bb_middle'].iloc[i]
            
            percent_b = data['percent_b'].iloc[i]
            bb_width_pct = data['bb_width_percentile'].iloc[i]
            rsi = data['rsi'].iloc[i]
            
            if pd.isna(bb_upper) or pd.isna(bb_lower):
                continue
            
            # Squeeze breakout - price breaks above upper band after squeeze
            if (current_close > bb_upper and 
                prev_close <= bb_upper and
                bb_width_pct < 0.2 and  # Recently squeezed
                rsi < 70):  # Not overbought
                
                confidence = min(0.9, (current_close - bb_upper) / bb_upper)
                data.loc[data.index[i], 'signal'] = 'BUY'
                data.loc[data.index[i], 'confidence'] = confidence
            
            # Squeeze breakdown - price breaks below lower band after squeeze
            elif (current_close < bb_lower and 
                  prev_close >= bb_lower and
                  bb_width_pct < 0.2 and  # Recently squeezed
                  rsi > 30):  # Not oversold
                
                confidence = min(0.9, (bb_lower - current_close) / bb_lower)
                data.loc[data.index[i], 'signal'] = 'SELL'
                data.loc[data.index[i], 'confidence'] = confidence
            
            # Mean reversion - price touches lower band in uptrend
            elif (current_close <= bb_lower and 
                  bb_middle > data['bb_middle'].iloc[i-5] and  # Uptrend
                  percent_b <= 0.1):
                
                confidence = 0.6  # Lower confidence for mean reversion
                data.loc[data.index[i], 'signal'] = 'BUY'
                data.loc[data.index[i], 'confidence'] = confidence
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi