"""Telegram bot for sending trading alerts."""

import asyncio
import logging
from typing import List, Dict, Any
from telegram import Bot
from telegram.constants import ParseMode
from config.settings import get_settings


class TelegramAlertsBot:
    """Handles sending alerts via Telegram."""
    
    def __init__(self):
        self.settings = get_settings()
        self.bot_token = self.settings.telegram_bot_token
        self.chat_id = self.settings.telegram_chat_id
        self.bot = None
        
        if self.bot_token and self.bot_token != "your_bot_token_here":
            self.bot = Bot(token=self.bot_token)
        else:
            self.logger.warning("Telegram bot token not configured")
    
    async def send_message(self, message: str, parse_mode: str = ParseMode.MARKDOWN) -> bool:
        """
        Send a message to the configured chat.
        
        Args:
            message: Message text to send
            parse_mode: Telegram parsing mode (Markdown, HTML, or None)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot:
            self.logger.error("Telegram bot not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.info("Telegram message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def format_signal_message(self, signal: Dict[str, Any]) -> str:
        """
        Format a trading signal into a Telegram message.
        
        Args:
            signal: Signal dictionary with trading information
        
        Returns:
            Formatted message string
        """
        signal_type = signal.get('signal_type', 'UNKNOWN')
        symbol = signal.get('symbol', 'UNKNOWN')
        strategy = signal.get('strategy', 'Unknown Strategy')
        confidence = signal.get('confidence', 0.0)
        price = signal.get('price', 0.0)
        
        # Choose emoji based on signal type
        emoji = "🟢" if signal_type == "BUY" else "🔴" if signal_type == "SELL" else "⚪"
        
        # Format confidence as percentage
        confidence_pct = confidence * 100
        
        message = f"""
{emoji} *{signal_type} SIGNAL* {emoji}

*Symbol:* `{symbol}`
*Strategy:* {strategy}
*Price:* ${price:.2f}
*Confidence:* {confidence_pct:.1f}%

*Indicators:*
"""
        
        # Add indicator information if available
        indicators = signal.get('indicators', {})
        if indicators:
            for key, value in indicators.items():
                if isinstance(value, (int, float)):
                    message += f"• {key}: {value:.2f}\n"
                else:
                    message += f"• {key}: {value}\n"
        
        # Add timestamp
        timestamp = signal.get('analysis_timestamp')
        if timestamp:
            message += f"\n*Analysis Time:* {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return message.strip()
    
    def format_consensus_message(self, consensus_signal: Dict[str, Any]) -> str:
        """
        Format a consensus signal into a Telegram message.
        
        Args:
            consensus_signal: Consensus signal dictionary
        
        Returns:
            Formatted message string
        """
        signal_type = consensus_signal.get('signal_type', 'UNKNOWN')
        symbol = consensus_signal.get('symbol', 'UNKNOWN')
        strategies = consensus_signal.get('strategies', [])
        strategies_count = consensus_signal.get('strategies_count', 0)
        avg_confidence = consensus_signal.get('avg_confidence', 0.0)
        avg_price = consensus_signal.get('avg_price', 0.0)
        
        emoji = "🟢🟢" if signal_type == "BUY" else "🔴🔴" if signal_type == "SELL" else "⚪⚪"
        
        message = f"""
{emoji} *CONSENSUS {signal_type} SIGNAL* {emoji}

*Symbol:* `{symbol}`
*Strategies Agreeing:* {strategies_count}
*Average Confidence:* {avg_confidence * 100:.1f}%
*Average Price:* ${avg_price:.2f}

*Strategies:*
"""
        
        for strategy in strategies:
            message += f"• {strategy}\n"
        
        timestamp = consensus_signal.get('analysis_timestamp')
        if timestamp:
            message += f"\n*Analysis Time:* {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return message.strip()
    
    def format_summary_message(self, signals: List[Dict[str, Any]]) -> str:
        """
        Format multiple signals into a summary message.
        
        Args:
            signals: List of signal dictionaries
        
        Returns:
            Formatted summary message
        """
        if not signals:
            return "📊 *Market Analysis Complete* - No actionable signals found."
        
        buy_signals = [s for s in signals if s.get('signal_type') == 'BUY']
        sell_signals = [s for s in signals if s.get('signal_type') == 'SELL']
        
        message = f"""
📊 *MARKET ANALYSIS SUMMARY*

*Total Signals:* {len(signals)}
🟢 *Buy Signals:* {len(buy_signals)}
🔴 *Sell Signals:* {len(sell_signals)}

*Top Signals:*
"""
        
        # Show top 5 signals by confidence
        top_signals = sorted(signals, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
        
        for i, signal in enumerate(top_signals, 1):
            symbol = signal.get('symbol', 'UNKNOWN')
            signal_type = signal.get('signal_type', 'UNKNOWN')
            confidence = signal.get('confidence', 0.0) * 100
            
            emoji = "🟢" if signal_type == "BUY" else "🔴"
            message += f"{i}. {emoji} `{symbol}` {signal_type} ({confidence:.1f}%)\n"
        
        return message.strip()
    
    async def send_signal_alert(self, signal: Dict[str, Any]) -> bool:
        """Send a single signal alert."""
        message = self.format_signal_message(signal)
        return await self.send_message(message)
    
    async def send_consensus_alert(self, consensus_signal: Dict[str, Any]) -> bool:
        """Send a consensus signal alert."""
        message = self.format_consensus_message(consensus_signal)
        return await self.send_message(message)
    
    async def send_summary_alert(self, signals: List[Dict[str, Any]]) -> bool:
        """Send a summary of all signals."""
        message = self.format_summary_message(signals)
        return await self.send_message(message)
    
    async def send_multiple_alerts(self, signals: List[Dict[str, Any]]) -> int:
        """
        Send multiple signal alerts.
        
        Args:
            signals: List of signals to send
        
        Returns:
            Number of successfully sent alerts
        """
        sent_count = 0
        
        for signal in signals:
            try:
                success = await self.send_signal_alert(signal)
                if success:
                    sent_count += 1
                
                # Add small delay between messages to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error sending alert for {signal.get('symbol', 'UNKNOWN')}: {str(e)}")
        
        return sent_count
    
    async def test_connection(self) -> bool:
        """Test the Telegram bot connection."""
        if not self.bot:
            return False
        
        try:
            me = await self.bot.get_me()
            self.logger.info(f"Telegram bot connected: @{me.username}")
            return True
        except Exception as e:
            self.logger.error(f"Telegram bot connection test failed: {str(e)}")
            return False


def send_alert_sync(message: str) -> bool:
    """Send a Telegram alert synchronously."""
    logger = logging.getLogger(__name__)
    bot = TelegramAlertsBot()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(bot.send_message(message))
    except Exception as e:
        logger.error(f"Error sending sync alert: {str(e)}")
        return False


# Alias for backward compatibility
TelegramNotifier = TelegramAlertsBot