# Food/cpi_training/train_cpi.py
from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT
from pathlib import Path
import pandas as pd, numpy as np, joblib
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT

CLEAN_FILES = {
    "qc_stores": DATA_DIR / "qc_food_purchased_from_stores_clean.csv",
    "qc_restaurants": DATA_DIR / "qc_food_purchased_from_restaurants_clean.csv",
}

def train_one(tag: str, path: Path):
    print(f"📄 Training on {tag}: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Missing clean file: {path}")
    df = pd.read_csv(path, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)

    # Linear Regression on time index
    df["t"] = np.arange(len(df))
    X = df[["t"]].values
    y = df["CPI_Food"].values
    lin = LinearRegression().fit(X, y)
    lin_path = MODELS_DIR / f"{tag}_cpi_lin.pkl"
    joblib.dump({"model": lin, "n_obs": len(df), "last_date": df["Date"].iloc[-1]}, lin_path)
    print(f"✅ Linear model saved -> {lin_path}")

    # ARIMA(1,1,1)
    arima = ARIMA(df["CPI_Food"], order=(1,1,1)).fit()
    arima_path = MODELS_DIR / f"{tag}_cpi_arima.pkl"
    joblib.dump({"model": arima, "last_date": df["Date"].iloc[-1]}, arima_path)
    print(f"✅ ARIMA model saved -> {arima_path}")

def main():
    for tag, path in CLEAN_FILES.items():
        train_one(tag, path)

if __name__ == "__main__":
    main()
