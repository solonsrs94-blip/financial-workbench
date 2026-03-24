"""
Company model — standardized representation of a company.

Every provider (Yahoo, Bloomberg, etc.) returns data in different formats.
This model is the common language — all providers convert their data into this.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class CompanyInfo:
    """Basic company information."""
    ticker: str
    name: str = ""
    sector: str = ""
    industry: str = ""
    country: str = ""
    currency: str = "USD"
    exchange: str = ""
    website: str = ""
    description: str = ""
    employees: Optional[int] = None


@dataclass
class CompanyPrice:
    """Current price and market data."""
    price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    beta: Optional[float] = None
    target_mean: Optional[float] = None
    target_median: Optional[float] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    analyst_rating: Optional[str] = None
    analyst_count: Optional[int] = None


@dataclass
class CompanyRatios:
    """Key financial ratios."""
    pe_trailing: Optional[float] = None
    pe_forward: Optional[float] = None
    peg: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    gross_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    eps_trailing: Optional[float] = None
    eps_forward: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None


@dataclass
class Company:
    """Complete company data — the main model used throughout the app."""
    info: CompanyInfo
    price: CompanyPrice = field(default_factory=CompanyPrice)
    ratios: CompanyRatios = field(default_factory=CompanyRatios)
    price_history: Optional[pd.DataFrame] = None
    income_statement: Optional[pd.DataFrame] = None
    balance_sheet: Optional[pd.DataFrame] = None
    cash_flow: Optional[pd.DataFrame] = None

    @property
    def ticker(self) -> str:
        return self.info.ticker

    @property
    def name(self) -> str:
        return self.info.name or self.info.ticker
