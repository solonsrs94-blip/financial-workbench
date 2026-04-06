"""Company classifier — simple 3-category system.

Classifies companies into:
- "financial": Banks, insurance, capital markets → DDM primary
- "dividend_stable": Utilities, REITs, stable dividend payers → DDM + DCF
- "normal": Everything else → DCF primary

The classifier returns a dict with:
- type, recommended_methods, reason (always present)
- subtype, data_source (for financial companies)
- signals: dict of classification inputs for UI display

No Streamlit imports (lib/ rule).
"""


_FINANCIAL_SECTORS = {"Financial Services", "Financials"}
_STABLE_SECTORS = {"Utilities", "Real Estate"}

_FINANCIAL_KEYWORDS = (
    "bank", "insurance", "capital markets", "financial",
    "asset management", "brokerage",
)
_BANK_KEYWORDS = (
    "bank", "diversified bank", "regional bank", "capital market",
    "financial service", "asset management", "brokerage",
)
_INSURANCE_KEYWORDS = (
    "insurance", "life insurance", "property & casualty",
    "reinsurance", "multi-line insurance",
)


def classify_company(
    ticker: str,
    sector: str,
    sub_industry: str,
    ratios: list[dict],
) -> dict:
    """Classify company for valuation method selection.

    Returns: {"type": str, "recommended_methods": list, "reason": str,
              "signals": dict}
    """
    sect = (sector or "").strip()
    sub = (sub_industry or "").lower()

    signals = {
        "sector": sect,
        "industry": sub_industry or "",
        "method": None,
    }

    # Financial institutions — check sector first, then industry keywords
    if sect in _FINANCIAL_SECTORS or any(k in sub for k in _FINANCIAL_KEYWORDS):
        subtype = "bank"
        if any(k in sub for k in _INSURANCE_KEYWORDS):
            subtype = "insurance"

        signals["method"] = (
            f"sector '{sect}'" if sect in _FINANCIAL_SECTORS
            else f"industry keyword match"
        )
        return {
            "type": "financial",
            "subtype": subtype,
            "data_source": "simfin",
            "recommended_methods": ["ddm"],
            "reason": f"Financial institution ({subtype}) — revenue from "
                      f"interest/premiums, DCF not appropriate",
            "signals": signals,
        }

    # Stable dividend payers — utilities, REITs, real estate
    if sect in _STABLE_SECTORS or "reit" in sub:
        signals["method"] = f"sector '{sect}'"
        return {
            "type": "dividend_stable",
            "recommended_methods": ["ddm", "dcf"],
            "reason": "Stable dividend payer — DDM primary, DCF secondary",
            "signals": signals,
        }

    # Check by ratios: high payout + low growth → dividend_stable
    if len(ratios) >= 3:
        growths = [r.get("revenue_growth") for r in ratios
                   if r.get("revenue_growth") is not None]
        avg_growth = sum(growths) / len(growths) if growths else 0
        last = ratios[-1]
        payout = last.get("payout_ratio")
        if payout and payout > 0.50 and avg_growth < 0.05:
            signals["method"] = (
                f"payout {payout*100:.0f}%, avg growth "
                f"{avg_growth*100:.1f}%"
            )
            return {
                "type": "dividend_stable",
                "recommended_methods": ["ddm", "dcf"],
                "reason": "Stable dividend payer — high payout, low growth",
                "signals": signals,
            }

    # Default
    signals["method"] = "no financial/stable signals matched"
    return {
        "type": "normal",
        "recommended_methods": ["dcf"],
        "reason": "Standard operating company",
        "signals": signals,
    }
