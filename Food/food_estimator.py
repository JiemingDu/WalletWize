# Food/food_estimator.py
"""
Food estimator — built FIRST.
Assumes a separate 'model' will later provide a CPI index by year where base 2025 = 100.

Frontend inputs we support:
  - year: int (target year selected in UI)
  - eating_out: str in {"never","1-2x","3-5x","daily"}  (↑ frequency → ↑ spending)
  - store_type: str in {"Maxi","Super C","Walmart","Costco","Metro","Provigo","Supermarché P.A.","Adonis","IGA"}
  - weekly_grocery_budget: float (household weekly budget, in 2025 dollars)

CPI convention (required by design):
  - The model will output a dict like: {2025: 100.0, 2026: 103.1, 2027: 106.5, ...}
  - Estimator multiplies base spending by (CPI[target_year] / 100.0).

Notes:
  - This module has ZERO external dependencies.
  - The CPI dict is an input (cpi_index_by_year) so we can wire the model later with no changes here.
"""

from __future__ import annotations
from typing import Dict, Final, Optional

# weekly → monthly (52 weeks / 12 months)
WEEKS_PER_MONTH: Final[float] = 52.0 / 12.0  # ~4.3333

# ↑ eating-out frequency → ↑ total spending
EAT_OUT_FACTOR: Final[Dict[str, float]] = {
    "never": 1.00,
    "1-2x":  1.05,
    "3-5x":  1.12,
    "daily": 1.20,
}

# store/brand effect on spending level
STORE_TIER_FACTOR: Final[Dict[str, float]] = {
    # discount-ish
    "Maxi": 0.95, "Super C": 0.95, "Walmart": 0.96, "Costco": 0.94,
    # mid/full-service
    "Metro": 1.02, "Provigo": 1.05, "Supermarché P.A.": 1.00, "Adonis": 0.99, "IGA": 1.03,
}

BASE_YEAR: Final[int] = 2025  # CPI base year; CPI[2025] must be 100.0


def _monthly_base_from_weekly(weekly_grocery_budget: float) -> float:
    """weekly → monthly (no behavior or CPI effects yet)."""
    try:
        weekly = float(weekly_grocery_budget)
    except:
        weekly = 0.0
    if weekly < 0:
        weekly = 0.0
    return weekly * WEEKS_PER_MONTH


def _behavior_multiplier(eating_out: str, store_type: str) -> float:
    """Multiply eating-out and store factors (defaults to 1.0 if unknown key)."""
    eat = EAT_OUT_FACTOR.get(eating_out, 1.0)
    store = STORE_TIER_FACTOR.get(store_type, 1.0)
    return eat * store


def _cpi_multiplier_for_year(year: int, cpi_index_by_year: Dict[int, float]) -> float:
    """
    Given a CPI index dict where CPI[2025] = 100,
    return multiplier = CPI[year] / 100. If year not present:
      - if year < min(dict), use min year
      - if year > max(dict), use max year
    """
    if not cpi_index_by_year or BASE_YEAR not in cpi_index_by_year:
        # No CPI provided or base missing → treat as 2025 dollars (multiplier 1.0)
        return 1.0

    # clamp to known range to avoid KeyError
    years_sorted = sorted(cpi_index_by_year.keys())
    clamped_year = max(years_sorted[0], min(years_sorted[-1], int(year)))
    cpi_val = float(cpi_index_by_year.get(clamped_year, 100.0))
    if cpi_val <= 0:
        return 1.0
    return cpi_val / 100.0


def expected_monthly_food_cost_for_year(
    *,
    year: int,
    eating_out: str,
    store_type: str,
    weekly_grocery_budget: float,
    cpi_index_by_year: Optional[Dict[int, float]] = None
) -> float:
    """
    FINAL frontend-facing function.

    Calculation:
      base_monthly_2025 = weekly_grocery_budget * (52/12)
      behavior_mult     = EAT_OUT_FACTOR[eating_out] * STORE_TIER_FACTOR[store_type]
      cpi_mult          = CPI[year] / 100   (with CPI[2025] = 100)
      result            = base_monthly_2025 * behavior_mult * cpi_mult

    Inputs:
      - year: target year selected in the UI.
      - eating_out: one of {"never","1-2x","3-5x","daily"}.
      - store_type: one of STORE_TIER_FACTOR keys.
      - weekly_grocery_budget: household weekly budget in base-year (2025) dollars.
      - cpi_index_by_year: dict mapping int year -> CPI index with CPI[2025]=100.
                           (Provided by the future 'model'. If None, we assume multiplier=1.0.)

    Returns:
      - float CAD/month in the target year dollars, rounded to 2 decimals.
    """
    base_monthly = _monthly_base_from_weekly(weekly_grocery_budget)
    behavior_mult = _behavior_multiplier(eating_out, store_type)
    cpi_mult = _cpi_multiplier_for_year(year, cpi_index_by_year or {})
    return round(base_monthly * behavior_mult * cpi_mult, 2)


# ---------- Optional stub for local testing ONLY (remove if you want it ultra-minimal) ----------

def _stub_cpi_index_by_year(
    start_year: int = BASE_YEAR,
    end_year: int = 2035,
    annual_growth: float = 0.025
) -> Dict[int, float]:
    """
    Build a simple CPI dict where CPI[2025]=100 and grows by a fixed CAGR thereafter.
    This is ONLY for quick testing before the real model is plugged in.
    """
    d: Dict[int, float] = {}
    for y in range(start_year, end_year + 1):
        years_from_base = y - BASE_YEAR
        d[y] = 100.0 * ((1.0 + annual_growth) ** years_from_base)
    return d


if __name__ == "__main__":
    # quick sanity check
    cpi = _stub_cpi_index_by_year(2025, 2030, 0.03)  # 3% stub growth
    ex = expected_monthly_food_cost_for_year(
        year=2028,
        eating_out="3-5x",
        store_type="Walmart",
        weekly_grocery_budget=180.0,  # in 2025 dollars
        cpi_index_by_year=cpi
    )
    print("Example 2028 monthly:", ex)
