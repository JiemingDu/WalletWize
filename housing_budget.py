import pandas as pd
from housing_model import train_evaluate_and_predict

future_df = train_evaluate_and_predict()

one_yr_cpi = future_df.loc[0,"predicted_cpi"]
two_yr_cpi = future_df.loc[1, "predicted_cpi"]
three_yr_cpi = future_df.loc[2, "predicted_cpi"]
four_yr_cpi = future_df.loc[3, "predicted_cpi"]
five_yr_cpi = future_df.loc[4,"predicted_cpi"]


print(five_yr_cpi)