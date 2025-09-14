"""Main application module for the quantitative alerting system."""

import asyncio
import argparse
from typing import List, Optional
from datetime import datetime

from .config import settings
from .utils.logger import setup_logger, logger
from .data.fetcher import DataFetcher
from .data.storage import DataStorage
from .strategies.manager import StrategyManager
from .alerts.telegram import TelegramAlertsBot


class QuantAlertSystem:
    """Main application class for the quantitative alerting system."""
    
    def __init__(self):
        self.logger = logger
        self.data_fetcher = DataFetcher()
        self.data_storage = DataStorage()
        self.strategy_manager = StrategyManager()
        self.telegram_bot = TelegramAlertsBot()
        
        # Ensure directories exist
        settings.create_directories()
    
    async def run_analysis(
        self,
        symbols: Optional[List[str]] = None,
        send_alerts: bool = True,
        min_confidence: float = 0.6
    ) -> dict:
        """
        Run complete analysis pipeline.
        
        Args:
            symbols: List of symbols to analyze (None for default)
            send_alerts: Whether to send Telegram alerts
            min_confidence: Minimum confidence for alerts
        
        Returns:
            Dictionary with analysis results
        """
        if symbols is None:
            symbols = settings.symbols_list
        
        self.logger.info(f"Starting analysis for symbols: {symbols}")
        
        try:
            # Step 1: Fetch latest data
            self.logger.info("Fetching market data...")
            market_data = self.data_fetcher.fetch_stock_data(
                symbols=symbols,
                period="1y"  # Get 1 year of data for analysis
            )
            
            if not market_data:
                self.logger.error("No market data fetched")
                return {'success': False, 'error': 'No market data'}
            
            # Step 2: Store data
            self.logger.info("Storing market data...")
            self.data_storage.store_stock_data(market_data)
            
            # Step 3: Run strategy analysis
            self.logger.info("Running strategy analysis...")
            analysis_results = self.strategy_manager.analyze_multiple_symbols(market_data)
            
            # Step 4: Extract actionable signals
            actionable_signals = self.strategy_manager.get_actionable_signals(
                analysis_results, min_confidence=min_confidence
            )
            
            # Step 5: Get consensus signals
            consensus_signals = self.strategy_manager.get_consensus_signals(
                analysis_results, min_strategies=2, min_confidence=0.5
            )
            
            # Step 6: Store alerts in database
            for signal in actionable_signals:
                alert_data = {
                    'symbol': signal['symbol'],
                    'strategy': signal['strategy'],
                    'signal_type': signal['signal_type'],
                    'signal_strength': signal['confidence'],
                    'price': signal['price'],
                    'message': f"{signal['signal_type']} signal for {signal['symbol']} from {signal['strategy']} strategy"
                }
                self.data_storage.store_alert(alert_data)
            
            # Step 7: Send alerts if requested
            alerts_sent = 0
            if send_alerts and (actionable_signals or consensus_signals):
                self.logger.info("Sending Telegram alerts...")
                
                # Send consensus signals first (highest priority)
                for consensus_signal in consensus_signals:
                    success = await self.telegram_bot.send_consensus_alert(consensus_signal)
                    if success:
                        alerts_sent += 1
                
                # Send individual high-confidence signals
                high_confidence_signals = [
                    s for s in actionable_signals 
                    if s['confidence'] >= 0.8 and len(consensus_signals) < 3
                ]
                
                if high_confidence_signals:
                    sent = await self.telegram_bot.send_multiple_alerts(high_confidence_signals)
                    alerts_sent += sent
                
                # Send summary if we have signals but didn't send individual alerts
                if actionable_signals and not high_confidence_signals and not consensus_signals:
                    success = await self.telegram_bot.send_summary_alert(actionable_signals)
                    if success:
                        alerts_sent += 1
            
            # Prepare results
            results = {
                'success': True,
                'timestamp': datetime.now(),
                'symbols_analyzed': len(market_data),
                'total_signals': len(actionable_signals),
                'consensus_count': len(consensus_signals),
                'alerts_sent': alerts_sent,
                'actionable_signals': actionable_signals,
                'consensus_signals': consensus_signals,
                'analysis_results': analysis_results
            }
            
            self.logger.info(f"Analysis complete: {len(actionable_signals)} signals, {alerts_sent} alerts sent")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in analysis pipeline: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def test_system(self) -> bool:
        """Test all system components."""
        self.logger.info("Testing system components...")
        
        try:
            # Test Telegram connection
            telegram_ok = await self.telegram_bot.test_connection()
            self.logger.info(f"Telegram bot: {'OK' if telegram_ok else 'FAILED'}")
            
            # Test data fetching
            test_data = self.data_fetcher.fetch_single_symbol("AAPL", period="5d")
            data_fetch_ok = test_data is not None and not test_data.empty
            self.logger.info(f"Data fetching: {'OK' if data_fetch_ok else 'FAILED'}")
            
            # Test database
            if data_fetch_ok:
                db_ok = self.data_storage.store_stock_data({"AAPL": test_data})
                self.logger.info(f"Database storage: {'OK' if db_ok else 'FAILED'}")
            else:
                db_ok = False
            
            # Test strategies
            if data_fetch_ok:
                strategy_results = self.strategy_manager.analyze_symbol("AAPL", test_data)
                strategies_ok = strategy_results.get('strategies', {})
                strategy_count = sum(1 for s in strategies_ok.values() if s.get('success', False))
                self.logger.info(f"Strategies: {strategy_count}/{len(strategies_ok)} OK")
            else:
                strategies_ok = False
            
            overall_ok = telegram_ok and data_fetch_ok and db_ok and strategies_ok
            
            # Send test message if Telegram is working
            if telegram_ok:
                await self.telegram_bot.send_message("🧪 QuantAlert System Test - All systems operational!")
            
            return overall_ok
            
        except Exception as e:
            self.logger.error(f"System test failed: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        self.data_storage.close()
        self.logger.info("System cleanup completed")


async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Quantitative Alerting System")
    parser.add_argument(
        '--symbols', 
        nargs='+', 
        help='Stock symbols to analyze (e.g., AAPL GOOGL MSFT)'
    )
    parser.add_argument(
        '--no-alerts', 
        action='store_true', 
        help='Run analysis without sending alerts'
    )
    parser.add_argument(
        '--min-confidence', 
        type=float, 
        default=0.6, 
        help='Minimum confidence threshold for alerts (default: 0.6)'
    )
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Test system components'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='Set logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level=args.log_level, log_file="quant_alerts.log")
    
    # Initialize system
    system = QuantAlertSystem()
    
    try:
        if args.test:
            # Run system test
            success = await system.test_system()
            print(f"System test: {'PASSED' if success else 'FAILED'}")
            return 0 if success else 1
        
        else:
            # Run analysis
            results = await system.run_analysis(
                symbols=args.symbols,
                send_alerts=not args.no_alerts,
                min_confidence=args.min_confidence
            )
            
            if results['success']:
                print("Analysis completed successfully:")
                print(f"  Symbols analyzed: {results['symbols_analyzed']}")
                print(f"  Total signals: {results['total_signals']}")
                print(f"  Consensus signals: {results['consensus_signals']}")
                print(f"  Alerts sent: {results['alerts_sent']}")
                return 0
            else:
                print(f"Analysis failed: {results.get('error', 'Unknown error')}")
                return 1
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    
    finally:
        system.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)