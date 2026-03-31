"""Financial data middleware — routes requests to EDGAR or SimFin.

Pages import from here, never directly from providers.
No Streamlit imports (lib/ rule).
"""

from typing import Optional


def fetch_bank_financials(ticker: str, market: str = "us") -> Optional[dict]:
    """Fetch bank financials via SimFin."""
    from lib.data.providers.simfin_provider import fetch_bank_financials as _fetch
    return _fetch(ticker, market)


def fetch_insurance_financials(ticker: str, market: str = "us") -> Optional[dict]:
    """Fetch insurance financials via SimFin."""
    from lib.data.providers.simfin_provider import fetch_insurance_financials as _fetch
    return _fetch(ticker, market)
