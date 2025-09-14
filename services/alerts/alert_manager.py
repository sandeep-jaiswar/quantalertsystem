"""
Alert management for the Quant Alerts System.

Orchestrates alert generation, formatting, and delivery with proper
prioritization and audit trails.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

from models.alerts import Alert, AlertChannel, AlertPriority
from models.signals import TradingSignal, ConfidenceLevel
from .telegram import TelegramNotifier


logger = logging.getLogger(__name__)


class AlertManager:
    """
    Alert management service for coordinating signal-to-alert conversion.
    
    Handles alert prioritization, formatting, and delivery across
    multiple channels with proper error handling and logging.
    """
    
    def __init__(self, telegram_notifier: TelegramNotifier):
        """
        Initialize alert manager.
        
        Args:
            telegram_notifier: Telegram notification service
        """
        self.telegram_notifier = telegram_notifier
        
    def process_signals(self, signals: List[TradingSignal]) -> List[Alert]:
        """
        Process trading signals and generate alerts.
        
        Args:
            signals: List of trading signals
            
        Returns:
            List of generated alerts
        """
        if not signals:
            logger.info("No signals to process")
            return []
        
        alerts = []
        
        # Group signals by symbol for consensus detection
        signal_groups = self._group_signals_by_symbol(signals)
        
        for symbol, symbol_signals in signal_groups.items():
            try:
                # Generate alerts for this symbol
                symbol_alerts = self._generate_symbol_alerts(symbol, symbol_signals)
                alerts.extend(symbol_alerts)
                
            except Exception as e:
                logger.error(f"Failed to generate alerts for {symbol}: {e}")
                continue
        
        # Send all alerts
        for alert in alerts:
            try:
                self._send_alert(alert)
            except Exception as e:
                logger.error(f"Failed to send alert {alert.alert_id}: {e}")
        
        return alerts
    
    def _group_signals_by_symbol(self, signals: List[TradingSignal]) -> Dict[str, List[TradingSignal]]:
        """Group signals by symbol."""
        groups = {}
        for signal in signals:
            if signal.symbol not in groups:
                groups[signal.symbol] = []
            groups[signal.symbol].append(signal)
        return groups
    
    def _generate_symbol_alerts(self, symbol: str, signals: List[TradingSignal]) -> List[Alert]:
        """Generate alerts for a single symbol."""
        alerts = []
        
        # Filter actionable signals
        actionable_signals = [s for s in signals if s.is_actionable]
        
        if not actionable_signals:
            return alerts
        
        # Check for consensus signals
        consensus_signals = [s for s in actionable_signals if s.is_consensus_worthy]
        
        if len(consensus_signals) >= 2:
            # Create consensus alert
            alert = self._create_consensus_alert(symbol, consensus_signals)
            alerts.append(alert)
            
        else:
            # Create individual alerts for high-confidence signals
            high_conf_signals = [s for s in actionable_signals if s.confidence >= 0.8]
            
            for signal in high_conf_signals:
                alert = self._create_individual_alert(symbol, [signal])
                alerts.append(alert)
        
        return alerts
    
    def _create_consensus_alert(self, symbol: str, signals: List[TradingSignal]) -> Alert:
        """Create a consensus alert from multiple signals."""
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Determine priority from average confidence
        priority = AlertPriority.from_confidence(avg_confidence)
        
        # Generate alert message
        signal_type = signals[0].signal_type  # Assume consensus on signal type
        title = f"🟢🟢 CONSENSUS {signal_type.value} SIGNAL 🟢🟢" if signal_type.value == "BUY" else f"🔴🔴 CONSENSUS {signal_type.value} SIGNAL 🔴🔴"
        
        strategies = [s.strategy_name for s in signals]
        avg_price = sum(float(s.price) for s in signals) / len(signals)
        
        message = f"""
{title}

Symbol: {symbol}
Strategies Agreeing: {len(signals)}
Average Confidence: {avg_confidence:.1%}
Average Price: ${avg_price:.2f}

Strategies:
{chr(10).join(f"• {strategy}" for strategy in strategies)}

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
""".strip()
        
        return Alert(
            alert_id=str(uuid.uuid4()),
            symbols=[symbol],
            signals=signals,
            priority=priority,
            channel=AlertChannel.TELEGRAM,
            title=title,
            message=message,
            timestamp=datetime.now()
        )
    
    def _create_individual_alert(self, symbol: str, signals: List[TradingSignal]) -> Alert:
        """Create an individual alert from a single signal."""
        signal = signals[0]
        priority = AlertPriority.from_confidence(signal.confidence)
        
        emoji = "🟢" if signal.signal_type.value == "BUY" else "🔴"
        title = f"{emoji} {signal.signal_type.value} SIGNAL - {symbol}"
        
        message = f"""
{title}

Strategy: {signal.strategy_name}
Confidence: {signal.confidence:.1%}
Price: ${float(signal.price):.2f}

Key Indicators:
{chr(10).join(f"• {k}: {v:.2f}" for k, v in signal.indicators.items())}

Analysis Time: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
""".strip()
        
        return Alert(
            alert_id=str(uuid.uuid4()),
            symbols=[symbol],
            signals=signals,
            priority=priority,
            channel=AlertChannel.TELEGRAM,
            title=title,
            message=message,
            timestamp=datetime.now()
        )
    
    def _send_alert(self, alert: Alert) -> None:
        """Send an alert via the appropriate channel."""
        if alert.channel == AlertChannel.TELEGRAM:
            self.telegram_notifier.send_message(alert.message)
            logger.info(f"Sent Telegram alert {alert.alert_id} for {alert.symbols}")
        else:
            logger.warning(f"Unsupported alert channel: {alert.channel}")