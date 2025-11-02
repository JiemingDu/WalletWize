# visualize_food.py
"""
Visual diagnostic script for the Food cost estimator + CPI model.

Run from project root:
    python visualize_food.py

Requires matplotlib:
    pip install matplotlib
"""

from Food.model import build_food_cpi_model
from Food.food_estimator import expected_monthly_food_cost_for_year
import matplotlib.pyplot as plt

# --- 1) Load CPI data and build the model ---
CPI_PATH = "Food/1810000401-eng.csv"
cpi_index = build_food_cpi_model(CPI_PATH, end_year=2035)

print("\n✅ CPI model built successfully.")
print(f"  Base year (2025) index = {cpi_index.get(2025, 'N/A')}")
print(f"  Forecasted 2030 index  = {cpi_index.get(2030, 'N/A')}")
print(f"  Forecasted 2035 index  = {cpi_index.get(2035, 'N/A')}")
print("-" * 50)

# --- 2) Plot CPI Index by Year ---
years = sorted(cpi_index.keys())
values = [cpi_index[y] for y in years]

plt.figure()
plt.plot(years, values, marker="o")
plt.title("Food CPI Index by Year (2025 = 100)")
plt.xlabel("Year")
plt.ylabel("Index")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.savefig("cpi_index_by_year.png", dpi=150)
print("🖼 Saved CPI curve → cpi_index_by_year.png")

# --- 3) Compare food costs for different eating-out habits ---
store = "Walmart"
weekly_budget = 180.0
scenarios = ["never", "3-5x", "daily"]
years_eval = list(range(2025, 2036))

plt.figure()
for freq in scenarios:
    costs = [
        expected_monthly_food_cost_for_year(
            year=y,
            eating_out=freq,
            store_type=store,
            weekly_grocery_budget=weekly_budget,
            cpi_index_by_year=cpi_index,
        )
        for y in years_eval
    ]
    plt.plot(years_eval, costs, marker="o", label=f"Eating out: {freq}")

plt.title(
    f"Predicted Monthly Grocery Cost (Store: {store}, Weekly Budget: ${weekly_budget:.0f})"
)
plt.xlabel("Year")
plt.ylabel("Monthly Cost (CAD)")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("food_cost_comparison.png", dpi=150)
print("🖼 Saved cost comparison → food_cost_comparison.png")

plt.show()
print("\n✅ Visualization complete.\n")
