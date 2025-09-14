"""
Alert models for the Quant Alerts System.

Immutable dataclasses representing alerts and notifications generated
from trading signals.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from .signals import TradingSignal


class AlertChannel(Enum):
    """Alert delivery channels."""
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"
    LOG = "LOG"


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def from_confidence(cls, confidence: float) -> 'AlertPriority':
        """Determine alert priority from signal confidence."""
        if confidence >= 0.9:
            return cls.CRITICAL
        elif confidence >= 0.8:
            return cls.HIGH
        elif confidence >= 0.6:
            return cls.MEDIUM
        else:
            return cls.LOW


@dataclass(frozen=True)
class Alert:
    """
    An alert generated from trading signals.
    
    Immutable representation of a notification with all metadata
    required for delivery and audit trails.
    """
    alert_id: str
    symbols: List[str]
    signals: List[TradingSignal]
    priority: AlertPriority
    channel: AlertChannel
    title: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate alert data."""
        if not self.signals:
            raise ValueError("Alert must contain at least one signal")
        
        if not self.symbols:
            raise ValueError("Alert must contain at least one symbol")
        
        # Verify symbols match signals
        signal_symbols = {signal.symbol for signal in self.signals}
        if set(self.symbols) != signal_symbols:
            raise ValueError(
                f"Alert symbols {self.symbols} don't match signal symbols {signal_symbols}"
            )
    
    @property
    def is_consensus(self) -> bool:
        """Check if alert represents a consensus signal."""
        return len(self.signals) > 1
    
    @property
    def avg_confidence(self) -> float:
        """Average confidence across all signals."""
        if not self.signals:
            return 0.0
        return sum(signal.confidence for signal in self.signals) / len(self.signals)
    
    @property
    def strategy_names(self) -> List[str]:
        """List of strategy names that generated the signals."""
        return [signal.strategy_name for signal in self.signals]
    
    @property
    def unique_strategies(self) -> List[str]:
        """List of unique strategy names."""
        return list(set(self.strategy_names))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for serialization."""
        return {
            'alert_id': self.alert_id,
            'symbols': self.symbols,
            'signals': [signal.to_dict() for signal in self.signals],
            'priority': self.priority.value,
            'channel': self.channel.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create alert from dictionary."""
        return cls(
            alert_id=data['alert_id'],
            symbols=data['symbols'],
            signals=[TradingSignal.from_dict(s) for s in data['signals']],
            priority=AlertPriority(data['priority']),
            channel=AlertChannel(data['channel']),
            title=data['title'],
            message=data['message'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata')
        )