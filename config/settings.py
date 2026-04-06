"""
Application settings — reads from st.secrets (Streamlit Cloud) with .env fallback (local dev).
All API keys and configurable values live here.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Load .env file (local dev fallback)
load_dotenv(ROOT_DIR / ".env")


def _get_secret(key: str, default: str = "") -> str:
    """Read from st.secrets first, fall back to os.getenv."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def get_firebase_service_account():
    """Return Firebase service account credentials dict, or None."""
    try:
        import streamlit as st
        if "firebase_service_account" in st.secrets:
            return dict(st.secrets["firebase_service_account"])
    except Exception:
        pass
    # Local fallback: read from JSON file
    sa_path = ROOT_DIR / "firebase-service-account.json"
    if sa_path.exists():
        return json.loads(sa_path.read_text())
    return None


# --- API Keys ---
FRED_API_KEY = _get_secret("FRED_API_KEY")
ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
SIMFIN_API_KEY = _get_secret("SIMFIN_API_KEY")
FMP_API_KEY = _get_secret("FMP_API_KEY")
FINNHUB_API_KEY = _get_secret("FINNHUB_API_KEY")

# --- Firebase ---
FIREBASE_API_KEY = _get_secret("FIREBASE_API_KEY")
FIREBASE_PROJECT_ID = _get_secret("FIREBASE_PROJECT_ID")
FIREBASE_AUTH_DOMAIN = _get_secret("FIREBASE_AUTH_DOMAIN")

# --- App Settings ---
APP_NAME = "Financial Workbench"
APP_ICON = "\U0001f4ca"
DEFAULT_LAYOUT = "wide"

# --- Data Paths ---
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DB = CACHE_DIR / "cache.db"
PORTFOLIO_DIR = DATA_DIR / "portfolio"
EXPERIMENTS_DIR = DATA_DIR / "experiments"
SESSIONS_DIR = DATA_DIR / "sessions"
SAVED_VALUATIONS_DIR = ROOT_DIR / "saved_valuations"

# --- Default Values ---
DEFAULT_MARKET_INDEX = "^GSPC"        # S&P 500
DEFAULT_RISK_FREE_TICKER = "^TNX"     # 10-Year US Treasury
DEFAULT_HISTORY_PERIOD = "5y"
DEFAULT_CURRENCY = "USD"
