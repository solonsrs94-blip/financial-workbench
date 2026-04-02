"""
Constants — cache TTLs, mappings, and fixed values.
These rarely change. If they do, change them here only.
"""

# --- Cache TTL (time-to-live) in seconds ---
CACHE_TTL = {
    "price_daily": 86400,          # 24 hours
    "price_intraday": 3600,        # 1 hour
    "financials": 604800,          # 7 days
    "ratios": 86400,               # 24 hours
    "company_info": 2592000,       # 30 days
    "damodaran": 2592000,          # 30 days
    "macro": 86400,                # 24 hours
    "news": 3600,                  # 1 hour
    "insider": 86400,              # 24 hours
    "options": 3600,               # 1 hour
    "sec_filings": 86400,          # 24 hours
}

# Max age before stale cache is deleted entirely (90 days)
CACHE_MAX_AGE = 7776000

# --- Number Formatting ---
LARGE_NUMBER_SUFFIXES = {
    1_000_000_000_000: "T",
    1_000_000_000: "B",
    1_000_000: "M",
    1_000: "K",
}

# --- Damodaran URLs ---
DAMODARAN_URLS = {
    "erp_monthly": "https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPbymonth.xlsx",
    "spreads": "https://pages.stern.nyu.edu/~adamodar/pc/ratings.xlsx",
    "crp": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctryprem.xlsx",
    "betas_us": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/betas.xls",
    "betas_global": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaGlobal.xls",
    "betas_emerging": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaemerg.xls",
    "wacc": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/wacc.xlsx",
}

# --- FRED Series IDs ---
FRED_SPREAD_SERIES = {
    "AAA": "BAMLC0A1CAAA",
    "AA": "BAMLC0A2CAA",
    "A": "BAMLC0A3CA",
    "BBB": "BAMLC0A4CBBB",
    "BB": "BAMLH0A1HYBB",
    "B": "BAMLH0A2HYB",
    "CCC": "BAMLH0A3HYC",
}

# --- Chart Defaults ---
CHART_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "positive": "#2ca02c",
    "negative": "#d62728",
    "neutral": "#7f7f7f",
    "background": "#0e1117",
    "grid": "#1e2530",
}

CHART_HEIGHT = 500
CHART_TEMPLATE = "plotly_dark"

# --- Period to calendar days mapping ---
PERIOD_DAYS = {
    "1mo": 30, "3mo": 90, "6mo": 180,
    "1y": 365, "2y": 730, "5y": 1825,
}

# --- Session state cache key prefixes ---
# Used for clearing all cached data when ticker changes.
# ADD NEW PREFIXES HERE when adding new cached data types.
SESSION_CACHE_PREFIXES = (
    "company_", "price_", "events_", "fin_data_",
    "holders_", "recs_", "news_", "peer_medians_",
    "val_",
)

# --- Yahoo Screener categories for Browse ---
# --- Valuation Defaults ---
DEFAULT_MRP = 0.055          # Market risk premium (Damodaran long-run avg)
DEFAULT_TAX_RATE = 0.21      # US corporate tax rate
DEFAULT_TERMINAL_GROWTH = 0.025  # Long-run GDP growth proxy

SECTOR_EXIT_MULTIPLES = {
    "Technology": 18.0,
    "Communication Services": 14.0,
    "Healthcare": 14.0,
    "Consumer Cyclical": 12.0,
    "Consumer Defensive": 12.0,
    "Financial Services": 10.0,
    "Industrials": 11.0,
    "Energy": 7.0,
    "Utilities": 10.0,
    "Real Estate": 15.0,
    "Basic Materials": 8.0,
}

# --- Yahoo Screener categories for Browse ---
SCREENER_CATEGORIES = {
    "Most Active": "most_actives",
    "Day Gainers": "day_gainers",
    "Day Losers": "day_losers",
    "Undervalued Large Caps": "undervalued_large_caps",
    "Growth Tech": "growth_technology_stocks",
    "Small Cap Gainers": "small_cap_gainers",
}
