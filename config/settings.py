"""
Settings configuration for the Quant Alerts System.

Type-safe configuration management with Pydantic validation
following manifesto principles for strict configuration discipline.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings with comprehensive validation.
    
    All configuration is loaded from environment variables with
    sensible defaults for development and production use.
    """
    
    # === Alert Configuration ===
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., env="TELEGRAM_CHAT_ID")
    
    # === Data Storage Configuration ===
    data_dir: Path = Field(Path("./data"), env="DATA_DIR")
    database_path: Path = Field(Path("./data/quant_alerts.duckdb"), env="DATABASE_PATH")
    data_retention_days: int = Field(180, env="DATA_RETENTION_DAYS", ge=30, le=365)
    
    # === Analysis Configuration ===
    default_symbols: str = Field("AAPL,GOOGL,MSFT,TSLA,NVDA", env="DEFAULT_SYMBOLS")
    lookback_days: int = Field(60, env="LOOKBACK_DAYS", ge=10, le=365)
    min_confidence_threshold: float = Field(0.6, env="MIN_CONFIDENCE_THRESHOLD", ge=0.0, le=1.0)
    max_symbols_per_run: int = Field(50, env="MAX_SYMBOLS_PER_RUN", ge=1, le=100)
    
    # === Strategy Parameters ===
    rsi_strategy_enabled: bool = Field(True, env="RSI_STRATEGY_ENABLED")
    ma_strategy_enabled: bool = Field(True, env="MA_STRATEGY_ENABLED")
    bollinger_strategy_enabled: bool = Field(True, env="BOLLINGER_STRATEGY_ENABLED")
    consensus_strategy_enabled: bool = Field(True, env="CONSENSUS_STRATEGY_ENABLED")
    
    # RSI Parameters
    rsi_period: int = Field(14, env="RSI_PERIOD", ge=2, le=50)
    rsi_oversold: float = Field(30.0, env="RSI_OVERSOLD_THRESHOLD", ge=10.0, le=40.0)
    rsi_overbought: float = Field(70.0, env="RSI_OVERBOUGHT_THRESHOLD", ge=60.0, le=90.0)
    
    # Moving Average Parameters
    ma_short: int = Field(20, env="MA_SHORT", ge=5, le=50)
    ma_long: int = Field(50, env="MA_LONG", ge=20, le=200)
    ma_volume_multiplier: float = Field(1.2, env="MA_VOLUME_MULTIPLIER", ge=1.0, le=3.0)
    
    # Bollinger Band Parameters
    bb_period: int = Field(20, env="BB_PERIOD", ge=10, le=50)
    bb_std: float = Field(2.0, env="BB_STD_DEV", ge=1.0, le=3.0)
    bb_squeeze_threshold: float = Field(0.2, env="BB_SQUEEZE_THRESHOLD", ge=0.1, le=0.5)
    
    # === Risk Management Configuration ===
    max_alerts_per_symbol_per_day: int = Field(3, env="MAX_ALERTS_PER_SYMBOL_PER_DAY", ge=1, le=10)
    min_alert_interval_minutes: int = Field(60, env="MIN_ALERT_INTERVAL_MINUTES", ge=5, le=1440)
    enable_position_sizing: bool = Field(True, env="ENABLE_POSITION_SIZING")
    
    # === Signal Filtering ===
    min_confidence: float = Field(0.6, env="MIN_CONFIDENCE", ge=0.0, le=1.0)
    min_consensus_strategies: int = Field(2, env="MIN_CONSENSUS_STRATEGIES", ge=2, le=5)
    volume_threshold_multiplier: float = Field(1.2, env="VOLUME_THRESHOLD_MULTIPLIER", ge=1.0, le=3.0)
    
    # === Performance Configuration ===
    max_retries: int = Field(3, env="MAX_RETRIES", ge=1, le=10)
    retry_delay: float = Field(1.0, env="RETRY_DELAY", ge=0.1, le=10.0)
    enable_performance_monitoring: bool = Field(True, env="ENABLE_PERFORMANCE_MONITORING")
    
    # === API Rate Limiting ===
    yahoo_finance_rate_limit: int = Field(100, env="YAHOO_FINANCE_RATE_LIMIT", ge=10, le=1000)
    telegram_rate_limit: int = Field(30, env="TELEGRAM_RATE_LIMIT", ge=1, le=100)
    
    # === Timeout Configuration ===
    data_fetch_timeout: int = Field(300, env="DATA_FETCH_TIMEOUT", ge=60, le=3600)
    analysis_timeout: int = Field(600, env="ANALYSIS_TIMEOUT", ge=300, le=7200)
    alert_send_timeout: int = Field(30, env="ALERT_SEND_TIMEOUT", ge=5, le=120)
    
    # === Logging Configuration ===
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_retention_days: int = Field(30, env="LOG_RETENTION_DAYS", ge=7, le=90)
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # === Development Configuration ===
    test_mode: bool = Field(False, env="TEST_MODE")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    no_alerts: bool = Field(False, env="NO_ALERTS")
    paper_trading: bool = Field(False, env="PAPER_TRADING")
    
    # === Environment Configuration ===
    environment: str = Field("development", env="ENVIRONMENT")
    version: str = Field("1.0.0", env="VERSION")
    deployment_id: str = Field("local", env="DEPLOYMENT_ID")
    
    # === Health Check Configuration ===
    health_check_enabled: bool = Field(True, env="HEALTH_CHECK_ENABLED")
    health_check_port: int = Field(8080, env="HEALTH_CHECK_PORT", ge=1024, le=65535)
    
    # === Metrics Configuration ===
    metrics_enabled: bool = Field(False, env="METRICS_ENABLED")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator('ma_long')
    @classmethod
    def validate_ma_periods(cls, v: int, info) -> int:
        """Validate that long MA > short MA."""
        if 'ma_short' in info.data and v <= info.data['ma_short']:
            raise ValueError("Long MA period must be greater than short MA period")
        return v
    
    @field_validator('rsi_overbought')
    @classmethod
    def validate_rsi_levels(cls, v: float, info) -> float:
        """Validate that overbought > oversold."""
        if 'rsi_oversold' in info.data and v <= info.data['rsi_oversold']:
            raise ValueError("RSI overbought must be greater than oversold")
        return v
    
    @property
    def symbols_list(self) -> List[str]:
        """Get symbols as a validated list."""
        symbols = [s.strip().upper() for s in self.default_symbols.split(",")]
        # Filter out empty strings
        symbols = [s for s in symbols if s]
        if not symbols:
            raise ValueError("At least one symbol must be provided")
        return symbols
    
    @property
    def database_url(self) -> str:
        """Get DuckDB connection URL."""
        return f"duckdb:///{self.database_path}"
    
    def create_directories(self) -> None:
        """
        Create necessary directories for data and logs.
        
        Ensures all required directories exist with proper permissions.
        """
        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create database directory
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Create subdirectories for different data stages
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "normalized").mkdir(exist_ok=True)
        (self.data_dir / "features").mkdir(exist_ok=True)
        (self.data_dir / "alerts").mkdir(exist_ok=True)
    
    def validate_configuration(self) -> None:
        """
        Validate complete configuration setup.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Check required directories can be created
        try:
            self.create_directories()
        except Exception as e:
            raise ValueError(f"Cannot create required directories: {e}")
        
        # Validate symbols
        try:
            symbols = self.symbols_list
            if len(symbols) > 50:  # Reasonable limit
                raise ValueError("Too many symbols (max 50)")
        except Exception as e:
            raise ValueError(f"Invalid symbols configuration: {e}")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Cached Settings instance
    """
    settings = Settings()
    settings.validate_configuration()
    return settings