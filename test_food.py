# test_food.py
"""
Quick test for the Food cost estimator + CPI model.
Run this from your project root with:
    python test_food.py
"""

from Food.model import build_food_cpi_model
from Food.food_estimator import expected_monthly_food_cost_for_year

# --- Step 1: Build CPI index from your StatsCan CSV ---
CPI_PATH = "Food/1810000401-eng.csv"
cpi_index = build_food_cpi_model(CPI_PATH, end_year=2035)

print("\n✅ CPI model built successfully.")
print(f"  Base year (2025) index = {cpi_index.get(2025, 'N/A')}")
print(f"  Forecasted 2030 index  = {cpi_index.get(2030, 'N/A')}")
print(f"  Forecasted 2035 index  = {cpi_index.get(2035, 'N/A')}")
print("-" * 50)

# --- Step 2: Try a few sample predictions ---

examples = [
    dict(year=2025, eating_out="3-5x", store_type="Maxi", weekly_grocery_budget=150.0),
    dict(year=2030, eating_out="3-5x", store_type="Walmart", weekly_grocery_budget=180.0),
    dict(year=2035, eating_out="daily", store_type="Metro", weekly_grocery_budget=220.0),
]

print("🧮 Example predictions (monthly household grocery cost):\n")
for ex in examples:
    cost = expected_monthly_food_cost_for_year(
        year=ex["year"],
        eating_out=ex["eating_out"],
        store_type=ex["store_type"],
        weekly_grocery_budget=ex["weekly_grocery_budget"],
        cpi_index_by_year=cpi_index,
    )
    print(
        f"Year {ex['year']:<4} | Eating out: {ex['eating_out']:<5} | "
        f"Store: {ex['store_type']:<8} | Weekly budget: ${ex['weekly_grocery_budget']:<6.0f} "
        f"→ Monthly cost: ${cost:.2f}"
    )

print("\n✅ All done.\n")
