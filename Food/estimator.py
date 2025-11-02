#
#
#

# Food/estimator.py
from typing import Dict, Any
from Food.cpi_model import blended_food_cpi

EAT_OUT_FREQ_TO_RATIO = {"never": 0.0, "1–2x": 0.2, "3–5x": 0.5, "daily": 0.9}
STORE_MULT = {"costco": 0.95, "walmart": 0.98, "super_c": 0.97,
              "iga": 1.05, "metro": 1.05, "provigo": 1.08, "other": 1.00}
WEEKS_PER_MONTH = 4.33
RESTO_PREMIUM = 1.6  # restaurant vs home-cooked

def expected_monthly_food_cost(payload: Dict[str, Any]) -> float:
    """Return one number (CAD) your planner can store."""
    freq = str(payload.get("eating_out_freq", "1–2x")).lower()
    if "never" in freq: eat = "never"
    elif "daily" in freq: eat = "daily"
    elif "3" in freq or "5" in freq: eat = "3–5x"
    else: eat = "1–2x"

    store = str(payload.get("grocery_store", "other")).lower()
    weekly = float(payload.get("grocery_budget_week", 80.0))

    eat_ratio = EAT_OUT_FREQ_TO_RATIO.get(eat, 0.2)
    base = weekly * STORE_MULT.get(store, 1.0) * WEEKS_PER_MONTH
    eat_out = base * eat_ratio * (RESTO_PREMIUM - 1.0)
    total_now = base + eat_out

    cpi = blended_food_cpi(eat_ratio)  # decimal e.g. 0.0143
    total_next_year = total_now * (1 + cpi)

    # choose which one your planner wants; here we return current:
    return round(total_now, 2)
