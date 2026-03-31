"""Company classifier — simple 3-category system.

Classifies companies into:
- "financial": Banks, insurance, capital markets → DDM primary
- "dividend_stable": Utilities, REITs, stable dividend payers → DDM + DCF
- "normal": Everything else → DCF primary

No Streamlit imports (lib/ rule).
"""


_FINANCIAL_KEYWORDS = ("bank", "insurance", "capital markets", "financial")
_FINANCIAL_SECTORS = {"Financial Services", "Financials"}
_STABLE_SECTORS = {"Utilities", "Real Estate"}

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

    Returns: {"type": str, "recommended_methods": list, "reason": str}
    """
    sect = (sector or "").strip()
    sub = (sub_industry or "").lower()

    # Financial institutions
    if sect in _FINANCIAL_SECTORS or any(k in sub for k in _FINANCIAL_KEYWORDS):
        # Determine subtype: bank vs insurance
        subtype = "bank"  # default for financial
        if any(k in sub for k in _INSURANCE_KEYWORDS):
            subtype = "insurance"

        return {
            "type": "financial",
            "subtype": subtype,
            "data_source": "simfin",
            "recommended_methods": ["ddm"],
            "reason": f"Financial institution ({subtype}) — revenue from "
                      f"interest/premiums, DCF not appropriate",
        }

    # Stable dividend payers
    if sect in _STABLE_SECTORS or "reit" in sub:
        return {
            "type": "dividend_stable",
            "recommended_methods": ["ddm", "dcf"],
            "reason": "Stable dividend payer — DDM primary, DCF secondary",
        }

    # Check by ratios: high yield + low growth → dividend_stable
    if len(ratios) >= 3:
        growths = [r.get("revenue_growth") for r in ratios
                   if r.get("revenue_growth") is not None]
        avg_growth = sum(growths) / len(growths) if growths else 0
        # Use last year's payout ratio as a proxy for dividend yield
        last = ratios[-1]
        payout = last.get("payout_ratio")
        if payout and payout > 0.50 and avg_growth < 0.05:
            return {
                "type": "dividend_stable",
                "recommended_methods": ["ddm", "dcf"],
                "reason": "Stable dividend payer — high payout, low growth",
            }

    # Default
    return {
        "type": "normal",
        "recommended_methods": ["dcf"],
        "reason": "Standard operating company",
    }
