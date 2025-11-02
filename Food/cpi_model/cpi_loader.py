# Food/cpi_loader.py
from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT
from pathlib import Path
import pandas as pd

STORES_FC = DATA_DIR / "qc_food_stores_forecast.csv"
RESTO_FC  = DATA_DIR / "qc_food_restaurants_forecast.csv"

def _first_yoy(path: Path, default: float = 0.04) -> float:
    try:
        print(f"🔎 reading {path}")
        df = pd.read_csv(path, parse_dates=["Date"])
        val = float(df["YoY_inflation"].dropna().iloc[0])
        print(f"   → YoY={val:.3%}")
        return val
    except Exception as e:
        print(f"⚠️ {path} not usable: {e} → using default {default:.3%}")
        return default

def blended_food_cpi(eat_out_ratio: float) -> float:
    grocery = _first_yoy(STORES_FC, 0.04)
    resto   = _first_yoy(RESTO_FC, 0.05)
    blended = (1 - eat_out_ratio) * grocery + eat_out_ratio * resto
    print(f"📈 blended={blended:.3%} (stores={grocery:.3%}, restaurants={resto:.3%})")
    return blended

if __name__ == "__main__":
    print(f"DATA_DIR = {DATA_DIR}")
    freq_map = {"never": 0.0, "1–2x": 0.2, "3–5x": 0.5, "daily": 0.9}
    ratio = freq_map["3–5x"]
    cpi = blended_food_cpi(ratio)
    print(f"✅ Estimated annual food CPI: {cpi:.2%}")
