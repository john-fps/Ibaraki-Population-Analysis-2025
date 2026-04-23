# -*- coding: utf-8 -*-
import re
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from typing import List, Tuple, Optional, Dict

def clean_city_name(name: str) -> str:
    """市町村名の表記ゆれ（カッコ内の削除など）をクリーニングする。"""
    s = str(name)
    s = re.sub(r"（.*?）", "", s)
    s = re.sub(r"\(.*?\)", "", s)
    return s.strip()

def auto_detect_pref_city_cols(gdf: gpd.GeoDataFrame) -> Tuple[Optional[str], Optional[str]]:
    """GeoDataFrameの列から都道府県名と市町村名の列を自動推測する。"""
    cols = list(gdf.columns)
    pref_col = next((c for c in ["PREF_NAME", "KEN", "N03_001", "都道府県名"] if c in cols), None)

    text_cols = [c for c in cols if gdf[c].dtype == object]
    city_col, best_score = None, -1
    for c in text_cols:
        score = gdf[c].astype(str).head(200).str.contains("市|町|村").sum() / 200
        if score > best_score:
            best_score, city_col = score, c
    return pref_col, city_col

def build_neighbor_list(shapefile_path: str, panel_cities: List[str], pref_name: str = "茨城県") -> pd.DataFrame:
    """シェープファイルから隣接リストを作成する。"""
    gdf = gpd.read_file(shapefile_path)
    pref_col, city_col = auto_detect_pref_city_cols(gdf)
    if pref_col:
        gdf = gdf[gdf[pref_col] == pref_name].copy()
    gdf["city_name"] = gdf[city_col].map(clean_city_name)
    gdf = gdf[gdf["city_name"].isin(panel_cities)].dissolve(by="city_name", as_index=False)

    gdf = gdf.reset_index(drop=True)
    sindex = gdf.sindex
    neighbors = set()
    for i, geom_i in enumerate(gdf.geometry):
        name_i = gdf.loc[i, "city_name"]
        possible_idx = list(sindex.intersection(geom_i.bounds))
        for j in possible_idx:
            if i == j: continue
            if geom_i.touches(gdf.geometry.iloc[j]):
                pair = tuple(sorted([name_i, gdf.loc[j, "city_name"]]))
                neighbors.add(pair)
    rows = []
    for ci, cj in sorted(neighbors):
        rows.append({"city_name": ci, "neighbor_name": cj})
        rows.append({"city_name": cj, "neighbor_name": ci})
    return pd.DataFrame(rows).drop_duplicates().sort_values(["city_name", "neighbor_name"])

def build_spatial_lag(panel: pd.DataFrame, neighbors_dict: Dict[str, List[str]]) -> pd.DataFrame:
    """空間ラグ項 W_log_pop_lag1 を計算して追加する。"""
    panel = panel.copy()
    panel["W_log_pop_lag1"] = np.nan
    for t in sorted(panel["year"].unique()):
        prev_map = panel[panel["year"] == t-1].set_index("city_name")["log_pop"].to_dict()
        if not prev_map: continue
        mask_t = panel["year"] == t
        for idx in panel.index[mask_t]:
            city = panel.at[idx, "city_name"]
            vals = [prev_map[nc] for nc in neighbors_dict.get(city, []) if nc in prev_map]
            if vals: panel.at[idx, "W_log_pop_lag1"] = np.mean(vals)
    return panel

def load_panel(path: str) -> pd.DataFrame:
    """BOM付きCSVにも対応したパネルデータの読み込み。"""
    return pd.read_csv(path, encoding="utf-8-sig")

def load_neighbors_dict(path: str) -> Dict[str, List[str]]:
    """隣接CSVから辞書形式への変換。"""
    df = pd.read_csv(path, encoding="utf-8-sig")
    return df.groupby("city_name")["neighbor_name"].apply(list).to_dict()

def load_raw_population_excel(path: str) -> pd.DataFrame:
    """
    茨城県提供の人口推移Excelを読み込み、パネルデータ形式に変換する。
    """
    # データの読み込み（4行目からデータ開始）
    df_raw = pd.read_excel(path, skiprows=3)

    # 必要な列（市町村名と人口データ）を抽出
    # 0列目が市町村名、2列目から51列目までが各年度の人口
    years_cols = df_raw.columns[2:52]
    df_clean = df_raw.iloc[:, [0] + list(range(2, 52))].copy()
    df_clean.columns = ["city_name"] + list(years_cols)

    # 市町村名のクリーニング
    df_clean["city_name"] = df_clean["city_name"].map(clean_city_name)

    # 合計（茨城県）や欠損値を除外
    df_clean = df_clean[df_clean["city_name"].notna() & (df_clean["city_name"] != "茨城県")]

    # 縦持ち（パネル形式）に変換
    df_panel = df_clean.melt(id_vars="city_name", var_name="year_str", value_name="population")

    # 年度の数値化（例：「昭和50年」→ 1975）
    def convert_year(s):
        s = str(s)
        match = re.search(r'\d+', s)
        val = int(match.group()) if match else None
        if "昭和" in s: return val + 1925
        if "平成" in s: return val + 1988
        if "令和" in s: return val + 2018
        return val

    df_panel["year"] = df_panel["year_str"].apply(convert_year)
    df_panel["log_pop"] = np.log(df_panel["population"])

    return df_panel.sort_values(["city_name", "year"]).reset_index(drop=True)