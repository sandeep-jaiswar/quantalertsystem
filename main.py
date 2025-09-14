"""
Main application for the Quant Alerts System.

Orchestrates the complete quantitative analysis pipeline following
the layered architecture defined in the copilot manifesto.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from config.settings import get_settings
from models.market_data import MarketData
from models.signals import TradingSignal
from services.alerts.alert_manager import AlertManager
from services.alerts.telegram import TelegramNotifier
from services.features.feature_engine import FeatureEngine
from services.ingest.yahoo_finance import YahooFinanceIngester
from services.normalize.data_normalizer import DataNormalizer
from services.strategy.manager import StrategyManager


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/quant_alerts.log")
        ]
    )


class QuantAlertsPipeline:
    """
    Main quantitative alerts pipeline orchestrator.
    
    Implements the complete data flow: ingestion → normalization → features 
    → strategies → alerts following the architecture defined in the copilot 
    manifesto.
    """
    
    def __init__(self):
        """Initialize the pipeline with all services."""
        self.settings = get_settings()
        self.settings.create_directories()
        
        # Initialize services
        self.ingester = YahooFinanceIngester(
            max_retries=self.settings.max_retries,
            retry_delay=self.settings.retry_delay
        )
        self.normalizer = DataNormalizer()
        self.feature_engine = FeatureEngine()
        self.strategy_manager = StrategyManager()
        
        # Initialize alert system
        telegram_notifier = TelegramNotifier(
            bot_token=self.settings.telegram_bot_token,
            chat_id=self.settings.telegram_chat_id
        )
        self.alert_manager = AlertManager(telegram_notifier)
        
        self.logger = logging.getLogger(__name__)
    
    async def run_analysis(
        self, 
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        send_alerts: bool = True
    ) -> List[TradingSignal]:
        """
        Run complete quantitative analysis pipeline.
        
        Args:
            symbols: List of symbols to analyze (default from config)
            start_date: Analysis start date (default: lookback_days ago)
            end_date: Analysis end date (default: today)
            send_alerts: Whether to send alerts (default: True)
            
        Returns:
            List of generated trading signals
        """
        # Use defaults if not provided
        symbols = symbols or self.settings.symbols_list
        end_date = end_date or datetime.now()
        start_date = start_date or (
            end_date - timedelta(days=self.settings.lookback_days)
        )
        
        self.logger.info(
            f"Starting analysis for {len(symbols)} symbols from "
            f"{start_date.date()} to {end_date.date()}"
        )
        
        try:
            # Step 1: Data Ingestion
            self.logger.info("Step 1: Ingesting market data")
            raw_data = await self._ingest_data(symbols, start_date, end_date)
            
            # Step 2: Data Normalization
            self.logger.info("Step 2: Normalizing market data")
            normalized_data = await self._normalize_data(raw_data)
            
            # Step 3: Feature Engineering
            self.logger.info("Step 3: Engineering features")
            features_data = await self._engineer_features(normalized_data)
            
            # Step 4: Strategy Analysis
            self.logger.info("Step 4: Running strategy analysis")
            signals = await self._analyze_strategies(features_data)
            
            # Step 5: Alert Generation
            if send_alerts and not self.settings.no_alerts:
                self.logger.info("Step 5: Generating alerts")
                alerts = await self._generate_alerts(signals)
                self.logger.info(f"Generated {len(alerts)} alerts")
            
            self.logger.info(f"Analysis complete. Generated {len(signals)} signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise
    
    async def _ingest_data(
        self, 
        symbols: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MarketData]:
        """Ingest market data for analysis."""
        return self.ingester.fetch_with_retry(symbols, start_date, end_date)
    
    async def _normalize_data(self, raw_data: List[MarketData]) -> List[MarketData]:
        """Normalize market data for quality assurance."""
        return self.normalizer.normalize(raw_data)
    
    async def _engineer_features(
        self, market_data: List[MarketData]
    ) -> List[MarketData]:
        """Engineer features from normalized market data."""
        # For now, return as-is since feature engineering is handled in strategies
        # In future versions, this will persist engineered features to Parquet
        return market_data
    
    async def _analyze_strategies(
        self, market_data: List[MarketData]
    ) -> List[TradingSignal]:
        """Run strategy analysis on market data."""
        all_signals = []
        
        for data in market_data:
            try:
                # Convert to DataFrame for strategy analysis
                df = data.to_dataframe()
                
                # Add technical indicators
                df = self.feature_engine.calculate_features(data)
                
                # Run strategies
                signals = self.strategy_manager.analyze(df, data.symbol)
                all_signals.extend(signals)
                
                self.logger.info(
                    f"Generated {len(signals)} signals for {data.symbol}"
                )
                
            except Exception as e:
                self.logger.error(f"Strategy analysis failed for {data.symbol}: {e}")
                continue
        
        return all_signals
    
    async def _generate_alerts(self, signals: List[TradingSignal]) -> List:
        """Generate and send alerts from trading signals."""
        return self.alert_manager.process_signals(signals)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Quantitative Alerts System")
    parser.add_argument(
        "--symbols", 
        nargs="+", 
        help="Symbols to analyze (e.g., AAPL MSFT)"
    )
    parser.add_argument(
        "--no-alerts", 
        action="store_true", 
        help="Run analysis without sending alerts"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--lookback-days", 
        type=int, 
        help="Number of days to look back for data"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize pipeline
        pipeline = QuantAlertsPipeline()
        
        # Override settings if provided
        if args.lookback_days:
            pipeline.settings.lookback_days = args.lookback_days
        if args.no_alerts:
            pipeline.settings.no_alerts = True
        
        # Run analysis
        signals = asyncio.run(pipeline.run_analysis(
            symbols=args.symbols,
            send_alerts=not args.no_alerts
        ))
        
        logger.info(
            f"Analysis completed successfully. Generated {len(signals)} signals."
        )
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    main()