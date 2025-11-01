import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
\
def train_evaluate_and_predict():

    df = pd.read_csv("CPI_housing.csv")

    #Data processing (This part is perfect)
    df["datetime"] = pd.to_datetime(df["Date"], format = "%b-%y")

    df["Year"] = df["datetime"].dt.year

    current_sys_year = pd.Timestamp.now().year

    df.loc[df["Year"] > current_sys_year, "Year"] -= 100

    # Group by year
    annual_df = df.groupby("Year")["Index"].mean().reset_index()
    annual_df.columns = ["Year", "CPI"]

    latest_year = int(annual_df['Year'].max())

    #Data prep
    X = annual_df[["Year"]]
    y = annual_df["CPI"]

    #Training
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions_test = model.predict(X_test)

    accuracy = r2_score(y_test, predictions_test)
    print(f"--- Model Accuracy (R2 Score): {accuracy:.4f} ---")

    model_final = LinearRegression()
    model_final.fit(X, y)
    print("--- Re-trained model on ALL data for final forecast ---")

    # Base the future years on the latest year found in the file
    start_year = latest_year + 1
    future_years_list = list(range(start_year, start_year + 5)) # e.g., if 2025 is latest, this is [2026, 2027, ... 2045]

    X_future = pd.DataFrame(future_years_list, columns=["Year"])

    future_predictions = model_final.predict(X_future)

    print(f"--- Generated predictions for the next 20 years: {future_years_list} ---")

    # This combines the future years and the predicted CPI values into a table
    future_df = pd.DataFrame({
        'year': future_years_list,
        'predicted_cpi': future_predictions
    })

    future_df['predicted_cpi'] = future_df['predicted_cpi'].round(1)

    print("\n--- Model Predictions for Future CPI ---")

    return future_df

future_df = train_evaluate_and_predict()

print(future_df)

