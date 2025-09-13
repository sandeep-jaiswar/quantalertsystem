"""Strategy manager for coordinating multiple trading strategies."""

import pandas as pd
from typing import Dict, List, Any, Optional
from .technical import (
    RSIMeanReversionStrategy,
    MovingAverageCrossoverStrategy,
    BollingerBandStrategy
)
from config.settings import get_settings


class StrategyManager:
    """Manages and coordinates multiple trading strategies."""
    
    def __init__(self):
        self.settings = get_settings()
        self.strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict[str, Any]:
        """Initialize all available strategies."""
        strategies = {}
        
        # RSI Mean Reversion Strategy
        strategies['rsi_mean_reversion'] = RSIMeanReversionStrategy(
            rsi_period=settings.rsi_period,
            oversold_threshold=30,
            overbought_threshold=70
        )
        
        # Moving Average Crossover Strategy
        strategies['ma_crossover'] = MovingAverageCrossoverStrategy(
            short_period=settings.ma_short,
            long_period=settings.ma_long
        )
        
        # Bollinger Band Strategy
        strategies['bollinger_bands'] = BollingerBandStrategy(
            period=20,
            std_multiplier=2
        )
        
        self.logger.info(f"Initialized {len(strategies)} strategies")
        return strategies
    
    def analyze_symbol(
        self,
        symbol: str,
        data: pd.DataFrame,
        strategies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a symbol using specified strategies.
        
        Args:
            symbol: Stock symbol to analyze
            data: OHLCV data for the symbol
            strategies: List of strategy names to use (None for all)
        
        Returns:
            Dictionary with analysis results for each strategy
        """
        if strategies is None:
            strategies = list(self.strategies.keys())
        
        results = {
            'symbol': symbol,
            'analysis_timestamp': pd.Timestamp.now(),
            'strategies': {}
        }
        
        for strategy_name in strategies:
            if strategy_name not in self.strategies:
                self.logger.warning(f"Strategy '{strategy_name}' not found")
                continue
            
            try:
                strategy = self.strategies[strategy_name]
                if not strategy.validate_data(data):
                    self.logger.error(f"Data validation failed for {strategy_name}")
                    continue
                
                analysis_result = strategy.analyze(data)
                results['strategies'][strategy_name] = analysis_result
                
                self.logger.info(
                    f"Completed {strategy_name} analysis for {symbol}"
                )
                
            except Exception as e:
                self.logger.error(
                    f"Error in {strategy_name} analysis for {symbol}: {str(e)}"
                )
                results['strategies'][strategy_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def analyze_multiple_symbols(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        strategies: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple symbols using specified strategies.
        
        Args:
            symbols_data: Dictionary with symbol as key and DataFrame as value
            strategies: List of strategy names to use (None for all)
        
        Returns:
            Dictionary with symbol as key and analysis results as value
        """
        all_results = {}
        
        for symbol, data in symbols_data.items():
            self.logger.info(f"Analyzing {symbol}")
            results = self.analyze_symbol(symbol, data, strategies)
            all_results[symbol] = results
        
        return all_results
    
    def get_actionable_signals(
        self,
        analysis_results: Dict[str, Dict[str, Any]],
        min_confidence: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Extract actionable signals from analysis results.
        
        Args:
            analysis_results: Results from analyze_multiple_symbols
            min_confidence: Minimum confidence threshold for signals
        
        Returns:
            List of actionable signals
        """
        actionable_signals = []
        
        for symbol, symbol_results in analysis_results.items():
            strategies_results = symbol_results.get('strategies', {})
            
            for strategy_name, strategy_result in strategies_results.items():
                if not strategy_result.get('success', False):
                    continue
                
                latest_signal = strategy_result.get('latest_signal')
                if not latest_signal:
                    continue
                
                signal_type = latest_signal.get('signal')
                confidence = latest_signal.get('confidence', 0.0)
                
                if signal_type and confidence >= min_confidence:
                    actionable_signals.append({
                        'symbol': symbol,
                        'strategy': strategy_name,
                        'signal_type': signal_type,
                        'confidence': confidence,
                        'price': latest_signal.get('price', 0.0),
                        'date': latest_signal.get('date'),
                        'indicators': latest_signal.get('indicators', {}),
                        'analysis_timestamp': symbol_results.get('analysis_timestamp')
                    })
        
        # Sort by confidence descending
        actionable_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.logger.info(f"Found {len(actionable_signals)} actionable signals")
        return actionable_signals
    
    def get_consensus_signals(
        self,
        analysis_results: Dict[str, Dict[str, Any]],
        min_strategies: int = 2,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Get signals where multiple strategies agree.
        
        Args:
            analysis_results: Results from analyze_multiple_symbols
            min_strategies: Minimum number of strategies that must agree
            min_confidence: Minimum average confidence
        
        Returns:
            List of consensus signals
        """
        consensus_signals = []
        
        for symbol, symbol_results in analysis_results.items():
            strategies_results = symbol_results.get('strategies', {})
            
            # Group signals by type
            buy_signals = []
            sell_signals = []
            
            for strategy_name, strategy_result in strategies_results.items():
                if not strategy_result.get('success', False):
                    continue
                
                latest_signal = strategy_result.get('latest_signal')
                if not latest_signal:
                    continue
                
                signal_type = latest_signal.get('signal')
                confidence = latest_signal.get('confidence', 0.0)
                
                if signal_type == 'BUY' and confidence >= min_confidence:
                    buy_signals.append({
                        'strategy': strategy_name,
                        'confidence': confidence,
                        'price': latest_signal.get('price', 0.0),
                        'indicators': latest_signal.get('indicators', {})
                    })
                elif signal_type == 'SELL' and confidence >= min_confidence:
                    sell_signals.append({
                        'strategy': strategy_name,
                        'confidence': confidence,
                        'price': latest_signal.get('price', 0.0),
                        'indicators': latest_signal.get('indicators', {})
                    })
            
            # Check for consensus
            if len(buy_signals) >= min_strategies:
                avg_confidence = sum(s['confidence'] for s in buy_signals) / len(buy_signals)
                avg_price = sum(s['price'] for s in buy_signals) / len(buy_signals)
                
                consensus_signals.append({
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'strategies_count': len(buy_signals),
                    'strategies': [s['strategy'] for s in buy_signals],
                    'avg_confidence': avg_confidence,
                    'avg_price': avg_price,
                    'analysis_timestamp': symbol_results.get('analysis_timestamp')
                })
            
            if len(sell_signals) >= min_strategies:
                avg_confidence = sum(s['confidence'] for s in sell_signals) / len(sell_signals)
                avg_price = sum(s['price'] for s in sell_signals) / len(sell_signals)
                
                consensus_signals.append({
                    'symbol': symbol,
                    'signal_type': 'SELL',
                    'strategies_count': len(sell_signals),
                    'strategies': [s['strategy'] for s in sell_signals],
                    'avg_confidence': avg_confidence,
                    'avg_price': avg_price,
                    'analysis_timestamp': symbol_results.get('analysis_timestamp')
                })
        
        # Sort by strategies count and confidence
        consensus_signals.sort(
            key=lambda x: (x['strategies_count'], x['avg_confidence']),
            reverse=True
        )
        
        self.logger.info(f"Found {len(consensus_signals)} consensus signals")
        return consensus_signals
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names."""
        return list(self.strategies.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific strategy."""
        if strategy_name not in self.strategies:
            return None
        
        strategy = self.strategies[strategy_name]
        return {
            'name': strategy.name,
            'parameters': strategy.params,
            'description': strategy.__class__.__doc__
        }