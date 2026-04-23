import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import List, Dict

def fit_ols_model(df: pd.DataFrame, target: str, features: List[str]) -> sm.regression.linear_model.RegressionResultsWrapper:
    """定数項を含むOLS回帰の実行。"""
    data = df[[target] + features].dropna()
    return sm.OLS(data[target], sm.add_constant(data[features])).fit()

def forecast_future(panel: pd.DataFrame, neighbors_dict: Dict[str, List[str]], model, ssdse_cols: List[str], forecast_years: List[int], base_year: int = 2020) -> pd.DataFrame:
    """再帰的な時空間予測の実行。"""
    current_logs = panel[panel["year"] == base_year].set_index("city_name")["log_pop"].to_dict()
    feat_df = panel[panel["year"] == base_year].set_index("city_name")[ssdse_cols]
    results = []
    for y in range(base_year + 1, max(forecast_years) + 1):
        new_logs = {}
        for city, log_lag1 in current_logs.items():
            neigh_logs = [current_logs[n] for n in neighbors_dict.get(city, []) if n in current_logs]
            w_log = np.mean(neigh_logs) if neigh_logs else log_lag1
            x = pd.DataFrame([{"const": 1.0, "log_pop_lag1": log_lag1, "W_log_pop_lag1": w_log, **feat_df.loc[city]}])
            log_pred = model.predict(x[model.params.index])[0]
            new_logs[city] = log_pred
            if y in forecast_years:
                results.append({"city_name": city, "year": y, "pop_pred": np.exp(log_pred)})
        current_logs = new_logs
    return pd.DataFrame(results)

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """予測精度（MAPE, RMSE）を算出する。"""
    ape = np.abs((y_true - y_pred) / y_true)
    return {
        "MAPE": np.mean(ape),
        "RMSE": np.sqrt(np.mean((y_true - y_pred)**2))
    }