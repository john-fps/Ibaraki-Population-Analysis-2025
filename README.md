# Ibaraki-Population-Analysis-2025
統計データ分析コンペティション2025 インプレッシブ賞受賞作。茨城県内市町村の人口動態を時空間自己回帰モデルで予測。/ Spatio-temporal population prediction model for Ibaraki.
# 茨城県市町村における人口の時空間予測モデルの構築
# Spatio-temporal Population Prediction Model for Ibaraki Municipalities

## 概要 (Overview)
[cite_start]茨城県の44市町村を対象に、1975年から2020年までの長期パネルデータとSSDSEを統合し、時間・空間・社会指標を同時に扱う時空間人口予測モデルを構築しました [cite: 5, 8]。
本プロジェクトは、北関東3大学連携 統計データ分析コンペティションにて**インプレッシブ賞**を受賞しました。

## 特徴 (Features)
- [cite_start]**時空間自己回帰モデル**: 時間的自己回帰に加え、隣接市町村の影響を考慮した「空間ラグ項」を導入 [cite: 12, 17]。
- [cite_start]**要因分析**: SSDSE指標（高齢化率、自然増減率等）を用いた人口変動の主因を分析 [cite: 20]。
- [cite_start]**将来予測**: 2030年および2040年の将来人口を予測 [cite: 23]。

## モデル式 (Model)
$$y_{i,t}=\alpha+\phi y_{i,t-1}+\rho\sum_{j}w_{ij}y_{j,t-1}+\beta^{T}x_{i,t-1}+\epsilon_{i,t}$$
[cite_start][cite: 12]

## 実行環境 (Environment)
- **Language**: Python
- **Computing Resource**: 自宅デスクトップ（NVIDIA GeForce RTX 4070 Ti）に大学のノートパソコンからリモート接続して実行。

## 著者 (Author)
[cite_start]茨城大学 工学部 機械システム工学科 粂田 悠希 [cite: 2]
