import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd

plt.rcParams["font.family"] = "MS Gothic"

def make_level_map(panel: pd.DataFrame, gdf_city: gpd.GeoDataFrame, year: int, output_path: str = None):
    """人口レベルマップの作成。"""
    data = panel[panel["year"] == year]
    merged = gdf_city.merge(data, on="city_name", how="left")
    fig, ax = plt.subplots(figsize=(8, 8))
    merged.plot(column="population", cmap="OrRd", edgecolor="black", linewidth=0.3, legend=True, ax=ax)
    ax.set_title(f"茨城県 市町村人口（{year}年）")
    ax.axis("off")
    if output_path: plt.savefig(output_path, dpi=300)
    plt.show()