# Quantitative Alerting System

A zero-cost quantitative alerting platform for stock trading signals, built with the rigor of an investment bank system but running at zero cost, with transparency, reproducibility, and extensibility as core values.

## 🎯 Features

- **Zero Cost**: Runs entirely on GitHub Actions - no server costs
- **Investment Bank Quality**: Professional-grade quantitative strategies and data handling
- **Real-time Alerts**: Instant Telegram notifications when trading opportunities arise
- **Multiple Strategies**: RSI Mean Reversion, Moving Average Crossover, Bollinger Band Squeeze
- **Efficient Data Storage**: Uses DuckDB with PyArrow for columnar data storage
- **Comprehensive Logging**: Full audit trail of all analysis and alerts
- **Extensible**: Easy to add new strategies and data sources

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Fetcher  │    │  Strategy Mgr   │    │  Alert System  │
│   (YFinance)    │───▶│  (Pandas/NumPy) │───▶│  (Telegram)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Storage  │    │   Analysis Log  │    │   Alert Log     │
│  (DuckDB/Arrow) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Supported Strategies

### 1. RSI Mean Reversion
- Identifies oversold/overbought conditions using RSI
- Filters signals using moving average trends
- Confidence scoring based on RSI deviation

### 2. Moving Average Crossover
- Golden Cross (bullish) and Death Cross (bearish) detection
- Volume confirmation for signal validation
- MACD confirmation for trend strength

### 3. Bollinger Band Squeeze
- Detects volatility contractions and breakouts
- Mean reversion signals at band extremes
- Squeeze detection for high-probability setups

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/sandeep-jaiswar/quantalertsystem.git
cd quantalertsystem

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DEFAULT_SYMBOLS=AAPL,GOOGL,MSFT,TSLA,NVDA
```

### 3. Run Analysis

```bash
# Test the system
python -m quantalertsystem.main --test

# Run analysis on default symbols
python -m quantalertsystem.main

# Analyze specific symbols
python -m quantalertsystem.main --symbols AAPL TSLA NVDA

# Run without sending alerts
python -m quantalertsystem.main --no-alerts
```

## 🤖 GitHub Actions Setup

The system runs automatically using GitHub Actions. Set up these secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID

### Scheduling

The system runs automatically:
- **9:30 AM EST**: Market open analysis
- **12:00 PM EST**: Midday check
- **4:00 PM EST**: Market close analysis

Only runs on weekdays when markets are open.

## 📱 Telegram Setup

### 1. Create a Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Save the bot token

### 2. Get Chat ID

1. Add the bot to your chat/group
2. Send a message to the bot
3. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find your chat ID in the response

## 📈 Data & Storage

- **Source**: Yahoo Finance via YFinance library
- **Storage**: DuckDB database with PyArrow columnar format
- **Retention**: 1 year of daily data, 2 years of alerts
- **Backup**: Automatic export to Parquet format

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=quantalertsystem

# Run specific test file
pytest tests/test_strategies.py
```

### Code Formatting

```bash
# Format code
black quantalertsystem/

# Lint code
flake8 quantalertsystem/
```

### Adding New Strategies

1. Create strategy class inheriting from `BaseStrategy`
2. Implement `calculate_indicators()` and `generate_signals()` methods
3. Add to `StrategyManager` initialization
4. Add tests in `tests/test_strategies.py`

Example:

```python
from quantalertsystem.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("My Strategy", **kwargs)
    
    def calculate_indicators(self, data):
        # Add your indicators
        return data
    
    def generate_signals(self, data):
        # Generate buy/sell signals
        return data
```

## 📊 Performance & Costs

- **Runtime**: ~2-3 minutes for 5 symbols
- **GitHub Actions**: ~10 minutes/month usage
- **Storage**: <100MB for 1 year of data
- **Cost**: $0 (free GitHub Actions tier)

## 🔒 Security & Privacy

- No sensitive data stored in repository
- All credentials managed via GitHub Secrets
- Database stored only in GitHub Actions runner (ephemeral)
- Automatic cleanup of old data

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

- 📧 Issues: Use GitHub Issues for bug reports
- 💬 Discussions: Use GitHub Discussions for questions
- 📖 Documentation: Check the `/docs` folder for detailed guides

## ⚠️ Disclaimer

This system is for educational and informational purposes only. Not financial advice. Always do your own research before making investment decisions.