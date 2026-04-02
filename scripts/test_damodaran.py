"""Test script for Damodaran provider.

Verifies all four fetch functions return expected data.
Run: python scripts/test_damodaran.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data.providers.damodaran import (
    fetch_erp,
    fetch_crp,
    fetch_spread,
    fetch_industry_beta,
)


def test_erp():
    """ERP should be between 3% and 7%."""
    print("=" * 50)
    print("TEST: fetch_erp()")
    erp = fetch_erp()
    print(f"  Result: {erp}")
    assert erp is not None, "ERP returned None"
    assert 0.03 <= erp <= 0.07, f"ERP {erp} outside 3-7% range"
    print(f"  PASS — ERP = {erp:.4f} ({erp*100:.2f}%)")


def test_crp_iceland():
    """Iceland should have a small but nonzero CRP."""
    print("=" * 50)
    print("TEST: fetch_crp('Iceland')")
    crp = fetch_crp("Iceland")
    print(f"  Result: {crp}")
    assert crp is not None, "CRP for Iceland returned None"
    assert 0.0 < crp < 0.10, f"CRP {crp} seems unreasonable"
    print(f"  PASS — Iceland CRP = {crp:.4f} ({crp*100:.2f}%)")


def test_crp_us():
    """US should have 0 or near-0 CRP."""
    print("=" * 50)
    print("TEST: fetch_crp('United States')")
    crp = fetch_crp("United States")
    print(f"  Result: {crp}")
    assert crp is not None, "CRP for US returned None"
    assert crp < 0.01, f"US CRP {crp} should be near 0"
    print(f"  PASS — US CRP = {crp:.4f} ({crp*100:.2f}%)")


def test_spread():
    """ICR of 8.0 should return a high rating with low spread."""
    print("=" * 50)
    print("TEST: fetch_spread(8.0)")
    result = fetch_spread(8.0)
    print(f"  Result: {result}")
    assert result is not None, "Spread lookup returned None"
    rating, spread = result
    assert isinstance(rating, str), "Rating should be a string"
    assert 0.0 < spread < 0.20, f"Spread {spread} seems unreasonable"
    print(f"  PASS — ICR 8.0 → rating={rating}, spread={spread:.4f}")


def test_spread_low_icr():
    """ICR of 1.0 should return a low rating with high spread."""
    print("=" * 50)
    print("TEST: fetch_spread(1.0)")
    result = fetch_spread(1.0)
    print(f"  Result: {result}")
    assert result is not None, "Spread lookup returned None"
    rating, spread = result
    print(f"  PASS — ICR 1.0 → rating={rating}, spread={spread:.4f}")


def test_industry_beta():
    """Software should have a valid unlevered beta."""
    print("=" * 50)
    print("TEST: fetch_industry_beta('Software (System & Application)')")
    result = fetch_industry_beta("Software (System & Application)")
    print(f"  Result: {result}")
    assert result is not None, "Industry beta returned None"
    assert "unlevered_beta" in result, "Missing unlevered_beta key"
    assert result["unlevered_beta"] > 0, "Unlevered beta should be positive"
    print(
        f"  PASS — {result['industry']}: "
        f"beta={result['beta']:.3f}, "
        f"ulev={result['unlevered_beta']:.3f}, "
        f"D/E={result['de_ratio']:.3f}"
    )


def test_industry_beta_partial():
    """Partial match should work too."""
    print("=" * 50)
    print("TEST: fetch_industry_beta('Software')")
    result = fetch_industry_beta("Software")
    print(f"  Result: {result}")
    assert result is not None, "Partial match returned None"
    print(f"  PASS — matched: {result['industry']}")


def test_industry_beta_global():
    """Global betas should work with region='global'."""
    print("=" * 50)
    print("TEST: fetch_industry_beta('Advertising', region='global')")
    result = fetch_industry_beta("Advertising", region="global")
    print(f"  Result: {result}")
    assert result is not None, "Global industry beta returned None"
    assert result["unlevered_beta"] > 0, "Unlevered beta should be positive"
    print(
        f"  PASS — {result['industry']}: "
        f"beta={result['beta']:.3f}, ulev={result['unlevered_beta']:.3f}"
    )


def test_industry_beta_emerging():
    """Emerging market betas should work with region='emerging'."""
    print("=" * 50)
    print("TEST: fetch_industry_beta('Advertising', region='emerging')")
    result = fetch_industry_beta("Advertising", region="emerging")
    print(f"  Result: {result}")
    assert result is not None, "Emerging industry beta returned None"
    assert result["unlevered_beta"] > 0, "Unlevered beta should be positive"
    print(
        f"  PASS — {result['industry']}: "
        f"beta={result['beta']:.3f}, ulev={result['unlevered_beta']:.3f}"
    )


if __name__ == "__main__":
    tests = [
        test_erp,
        test_crp_iceland,
        test_crp_us,
        test_spread,
        test_spread_low_icr,
        test_industry_beta,
        test_industry_beta_partial,
        test_industry_beta_global,
        test_industry_beta_emerging,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  FAIL — {exc}")
            failed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed:
        sys.exit(1)
