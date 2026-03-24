"""
Application settings — reads from .env file.
All API keys and configurable values live here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Load .env file
load_dotenv(ROOT_DIR / ".env")


# --- API Keys ---
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- App Settings ---
APP_NAME = "Financial Workbench"
APP_ICON = "📊"
DEFAULT_LAYOUT = "wide"

# --- Data Paths ---
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DB = CACHE_DIR / "cache.db"
PORTFOLIO_DIR = DATA_DIR / "portfolio"
EXPERIMENTS_DIR = DATA_DIR / "experiments"
SESSIONS_DIR = DATA_DIR / "sessions"

# --- Default Values ---
DEFAULT_MARKET_INDEX = "^GSPC"        # S&P 500
DEFAULT_RISK_FREE_TICKER = "^TNX"     # 10-Year US Treasury
DEFAULT_HISTORY_PERIOD = "5y"
DEFAULT_CURRENCY = "USD"
