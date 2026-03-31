"""SimFin provider — financial statements for banks, insurance, and general companies.

Free tier: ~5 years of data, delayed ~12 months. No rate limit.
Primary use: Bank and insurance templates (not available via EDGAR standardizer).
Secondary use: Fallback for general companies when EDGAR fails.

Returns dicts in same format as EDGAR standardizer for seamless integration.
"""

import logging
from typing import Optional

from lib.data.providers.simfin_maps import (
    GENERAL_IS_MAP, GENERAL_BS_MAP, GENERAL_CF_MAP,
    BANK_IS_MAP, BANK_BS_MAP, BANK_CF_MAP,
    INSURANCE_IS_MAP,
)
from lib.data.providers.simfin_utils import (
    extract_ticker_data as _extract_ticker_data,
    to_audit_format as _to_audit_format,
    compute_derived as _compute_derived,
)

logger = logging.getLogger(__name__)


def _load_simfin():
    """Lazy import simfin -- avoids crash if not installed."""
    try:
        import simfin as sf
        from config.settings import SIMFIN_API_KEY, DATA_DIR
        if not SIMFIN_API_KEY:
            logger.warning("SIMFIN_API_KEY not set -- SimFin unavailable")
            return None
        sf.set_api_key(SIMFIN_API_KEY)
        sf.set_data_dir(str(DATA_DIR / "simfin_cache"))
        return sf
    except ImportError:
        logger.warning("simfin not installed -- pip install simfin")
        return None


def fetch_general_financials(
    ticker: str, market: str = "us",
) -> Optional[dict]:
    """Fetch general company financials from SimFin."""
    sf = _load_simfin()
    if sf is None:
        return None

    try:
        is_data = _extract_ticker_data(
            sf.load_income(variant="annual", market=market),
            ticker, GENERAL_IS_MAP,
        )
        bs_data = _extract_ticker_data(
            sf.load_balance(variant="annual", market=market),
            ticker, GENERAL_BS_MAP,
        )
        cf_data = _extract_ticker_data(
            sf.load_cashflow(variant="annual", market=market),
            ticker, GENERAL_CF_MAP,
        )

        if not any([is_data, bs_data, cf_data]):
            return None

        for d in [is_data, bs_data, cf_data]:
            if d:
                _compute_derived(d)

        years = set()
        for d in [is_data, bs_data, cf_data]:
            if d:
                years.update(d.keys())

        return {
            "years": sorted(years),
            "income_audit": _to_audit_format(is_data or {}),
            "balance_audit": _to_audit_format(bs_data or {}),
            "cashflow_audit": _to_audit_format(cf_data or {}),
            "source": "simfin",
            "company_type": "general",
        }

    except Exception as e:
        logger.error("SimFin general fetch failed for %s: %s", ticker, e)
        return None


def fetch_bank_financials(
    ticker: str, market: str = "us",
) -> Optional[dict]:
    """Fetch bank financials from SimFin bank template."""
    sf = _load_simfin()
    if sf is None:
        return None

    try:
        is_data = _extract_ticker_data(
            sf.load_income_banks(variant="annual", market=market),
            ticker, BANK_IS_MAP,
        )
        bs_data = _extract_ticker_data(
            sf.load_balance_banks(variant="annual", market=market),
            ticker, BANK_BS_MAP,
        )
        cf_data = _extract_ticker_data(
            sf.load_cashflow_banks(variant="annual", market=market),
            ticker, BANK_CF_MAP,
        )

        if not any([is_data, bs_data, cf_data]):
            return None

        # Bank-specific derived fields
        for year in (is_data or {}):
            d = is_data[year]
            bs = (bs_data or {}).get(year, {})
            nie = d.get("total_non_interest_expense")
            rev = d.get("revenue")
            if nie and rev and rev != 0:
                d["efficiency_ratio"] = abs(nie) / abs(rev)
            ni = d.get("net_income")
            ta = bs.get("total_assets")
            if ni and ta and ta != 0:
                d["roa"] = ni / ta
            te = bs.get("total_equity")
            if ni and te and te != 0:
                d["roe"] = ni / te
            loans = bs.get("net_loans")
            deposits = bs.get("total_deposits")
            if loans and deposits and deposits != 0:
                d["loan_to_deposit"] = loans / deposits
            if te and ta and ta != 0:
                d["tier1_proxy"] = te / ta

        years = set()
        for d in [is_data, bs_data, cf_data]:
            if d:
                years.update(d.keys())

        return {
            "years": sorted(years),
            "income_audit": _to_audit_format(is_data or {}),
            "balance_audit": _to_audit_format(bs_data or {}),
            "cashflow_audit": _to_audit_format(cf_data or {}),
            "source": "simfin_bank",
            "company_type": "bank",
        }

    except Exception as e:
        logger.error("SimFin bank fetch failed for %s: %s", ticker, e)
        return None


def fetch_insurance_financials(
    ticker: str, market: str = "us",
) -> Optional[dict]:
    """Fetch insurance company financials from SimFin insurance template."""
    sf = _load_simfin()
    if sf is None:
        return None

    try:
        is_data = _extract_ticker_data(
            sf.load_income_insurance(variant="annual", market=market),
            ticker, INSURANCE_IS_MAP,
        )
        bs_data = _extract_ticker_data(
            sf.load_balance(variant="annual", market=market),
            ticker, GENERAL_BS_MAP,
        )
        cf_data = _extract_ticker_data(
            sf.load_cashflow(variant="annual", market=market),
            ticker, GENERAL_CF_MAP,
        )

        if not any([is_data, bs_data, cf_data]):
            return None

        years = set()
        for d in [is_data, bs_data, cf_data]:
            if d:
                years.update(d.keys())

        return {
            "years": sorted(years),
            "income_audit": _to_audit_format(is_data or {}),
            "balance_audit": _to_audit_format(bs_data or {}),
            "cashflow_audit": _to_audit_format(cf_data or {}),
            "source": "simfin_insurance",
            "company_type": "insurance",
        }

    except Exception as e:
        logger.error("SimFin insurance fetch failed for %s: %s", ticker, e)
        return None


# Legacy compatibility
def fetch_historical_financials(ticker: str, market: str = "us") -> Optional[dict]:
    """Legacy function -- now calls fetch_general_financials."""
    return fetch_general_financials(ticker, market)
