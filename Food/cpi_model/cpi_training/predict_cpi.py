# Food/cpi_training/predict_cpi.py
from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT
from pathlib import Path
import pandas as pd, joblib
import sys

from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT

CLEAN_FILES = {
    "qc_stores": DATA_DIR / "qc_food_purchased_from_stores_clean.csv",
    "qc_restaurants": DATA_DIR / "qc_food_purchased_from_restaurants_clean.csv",
}
OUT_FILES = {
    "qc_stores": DATA_DIR / "qc_food_stores_forecast.csv",
    "qc_restaurants": DATA_DIR / "qc_food_restaurants_forecast.csv",
}
MONTHS_AHEAD = int(sys.argv[1]) if len(sys.argv) > 1 else 12  # forecast horizon


def forecast_one(tag: str, clean_path: Path):
    # 1) Load ARIMA and last date used in training
    bundle = joblib.load(MODELS_DIR / f"{tag}_cpi_arima.pkl")
    model = bundle["model"]
    last_date = pd.to_datetime(bundle["last_date"])

    # 2) Forecast next N months on month-end dates ('ME' avoids deprecation)
    dates = pd.date_range(last_date + pd.offsets.MonthEnd(1), periods=MONTHS_AHEAD, freq="ME")
    preds = model.forecast(steps=MONTHS_AHEAD)
    fc = pd.DataFrame({"Date": dates, "CPI_Food": preds.values})

    # 3) Load history and align to month-end frequency
    hist = pd.read_csv(clean_path, parse_dates=["Date"]).sort_values("Date")
    hist = hist.set_index("Date").asfreq("ME")     # ensure month-end index
    hist = hist["CPI_Food"].ffill()                # fill any gaps

    # 4) Combine hist + forecast as one series
    s_all = pd.concat([hist, fc.set_index("Date")["CPI_Food"]]).sort_index()

    # 4b) Compute YoY only for the forecast timestamps
    fc_idx = fc["Date"]
    base_12m = s_all.shift(12)                # value 12 months earlier
    yoy_fc = (s_all.loc[fc_idx] - base_12m.loc[fc_idx]) / base_12m.loc[fc_idx]

    # 5) Build output for forecast rows only
    out = fc.copy()
    out["Model"] = "ARIMA(1,1,1)"
    out["YoY_inflation"] = yoy_fc.values
    out["YoY_inflation"] = out["YoY_inflation"].ffill().bfill().fillna(0.0)
    out.to_csv(OUT_FILES[tag], index=False)
    print(f"✅ Forecast saved -> {OUT_FILES[tag]}")

    # 6) Save
    out.to_csv(OUT_FILES[tag], index=False)
    print(f"✅ Forecast saved -> {OUT_FILES[tag]}")


def main():
    for tag, clean in CLEAN_FILES.items():
        forecast_one(tag, clean)

if __name__ == "__main__":
    main()
