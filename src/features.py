import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Tuple

def calculate_ssdse_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """SSDSEの生データから分析用指標を算出する。"""
    res = df.copy()
    pop = res["population"]
    res["share_under15"] = res["A1301"] / pop
    res["share_over65"] = res["A1303"] / pop
    res["nat_inc_rate"] = (res["A4101"] - res["A4200"]) / pop
    res["soc_inc_rate"] = (res["A5101"] - res["A5102"]) / pop
    return res

def run_pca_analysis(panel: pd.DataFrame, n_components: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler, PCA]:
    """人口データに行列PCAを適用する。"""
    mat = panel.pivot_table(index="year", columns="city_name", values="log_pop").dropna(axis=1)
    scaler = StandardScaler()
    X_std = scaler.fit_transform(mat.values)
    pca = PCA(n_components=n_components)
    scores = pd.DataFrame(pca.fit_transform(X_std), index=mat.index, columns=[f"PC{k+1}_score" for k in range(n_components)])
    loadings = pd.DataFrame(pca.components_.T, index=mat.columns, columns=[f"PC{k+1}_loading" for k in range(n_components)])
    return scores, loadings, scaler, pca