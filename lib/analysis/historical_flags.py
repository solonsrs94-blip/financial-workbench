"""Historical anomaly detection — delegates to flags.py (15 rules).

Thin wrapper that preserves the same public API.
No Streamlit imports (lib/ rule).
"""

from typing import Optional

from lib.analysis.flags import detect_flags  # noqa: F401

# Re-export
from lib.analysis.historical_averages import compute_averages  # noqa: F401
