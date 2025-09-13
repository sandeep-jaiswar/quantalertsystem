"""Configuration management for the quantitative alerting system."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., env="TELEGRAM_CHAT_ID")
    
    # Database Configuration
    database_path: str = Field("./data/quant_alerts.db", env="DATABASE_PATH")
    
    # Data Configuration
    data_dir: str = Field("./data", env="DATA_DIR")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Strategy Configuration
    default_symbols: str = Field("AAPL,GOOGL,MSFT,TSLA,NVDA", env="DEFAULT_SYMBOLS")
    lookback_days: int = Field(60, env="LOOKBACK_DAYS")
    rsi_period: int = Field(14, env="RSI_PERIOD")
    ma_short: int = Field(20, env="MA_SHORT")
    ma_long: int = Field(50, env="MA_LONG")
    
    @property
    def symbols_list(self) -> List[str]:
        """Get symbols as a list."""
        return [s.strip().upper() for s in self.default_symbols.split(",")]
    
    def create_directories(self):
        """Create necessary directories."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        # Ensure database directory exists
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()