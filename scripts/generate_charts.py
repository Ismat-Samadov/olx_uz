"""
generate_charts.py
Generates 7 real estate market charts from the OLX Uzbekistan dataset.
All chart text is in English.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "data.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid")
BLUE_PALETTE = ["#084c8d", "#1565c0", "#1976d2", "#1e88e5", "#42a5f5",
                "#64b5f6", "#90caf9", "#bbdefb", "#e3f2fd"]
TEAL_PALETTE = ["#00695c", "#00796b", "#00897b", "#009688", "#26a69a",
                "#4db6ac", "#80cbc4", "#b2dfdb", "#e0f2f1"]
TYPE_COLORS = {
    "Apartments":       "#1565c0",
    "New Builds":       "#00897b",
    "Houses":           "#6a1b9a",
    "Land Plots":       "#e65100",
    "Offices":          "#37474f",
    "Commercial":       "#c62828",
    "Garages":          "#558b2f",
    "Rental (Various)": "#f9a825",
    "Other":            "#90a4ae",
}

# ---------------------------------------------------------------------------
# 1. Load & enrich
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH, encoding="utf-8")

# --- property_type ---
def classify_property(url: str) -> str:
    u = url.lower()
    if any(k in u for k in ["kvartira", "komnata", "xonalik", "honalik"]):
        return "Apartments"
    if any(k in u for k in ["novostroyka", "zhk", "skyline", "hovus",
                              "residence", "new_build"]):
        return "New Builds"
    if any(k in u for k in ["dom", "house", "kottedzh", "uy", "dacha"]):
        return "Houses"
    if any(k in u for k in ["uchastok", "zem", "sotok", "arazi"]):
        return "Land Plots"
    if "ofis" in u:
        return "Offices"
    if any(k in u for k in ["kommerch", "magazin", "tseh", "sklad",
                              "kafe", "biznes", "restoran", "proizvodstvo"]):
        return "Commercial"
    if any(k in u for k in ["garazh", "parking"]):
        return "Garages"
    if any(k in u for k in ["arenda", "sutochno", "ijarada"]):
        return "Rental (Various)"
    return "Other"

df["property_type"] = df["url"].apply(classify_property)

# --- listing_type ---
def classify_listing(url: str) -> str:
    u = url.lower()
    if any(k in u for k in ["arenda", "sutochno", "ijarada"]):
        return "Rental"
    return "Sale"

df["listing_type"] = df["url"].apply(classify_listing)

# --- city ---
df["city"] = df["location"].str.split(",").str[0].str.strip()

# --- price_usd, price_mln_uzs, is_today ---
df["price_usd"]     = (df["price"] / 12_700).round(0).astype(int)
df["price_mln_uzs"] = (df["price"] / 1_000_000).round(1)
df["is_today"]      = df["date"].str.contains("Сегодня", na=False)

# ---------------------------------------------------------------------------
# 2. Filter outliers
# ---------------------------------------------------------------------------
df = df[df["price"] > 1_000_000].copy()
print(f"[INFO] Rows after outlier filter: {len(df)}")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def save_chart(fig, name):
    path = os.path.join(CHARTS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[SAVED] {path}")


def bar_color_gradient(n, palette_list):
    """Return n colors interpolated from a list (dark → light)."""
    cmap = LinearSegmentedColormap.from_list("custom", palette_list[::-1], N=256)
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


# ---------------------------------------------------------------------------
# Chart 1: Listings by City (top 12)
# ---------------------------------------------------------------------------
city_counts = df["city"].value_counts().head(12).sort_values()
n = len(city_counts)
colors_c1 = bar_color_gradient(n, ["#bbdefb", "#0d47a1"])

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(city_counts.index, city_counts.values, color=colors_c1, edgecolor="white")
for bar, val in zip(bars, city_counts.values):
    ax.text(val + city_counts.values.max() * 0.005, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", ha="left", fontsize=10, fontweight="bold")
ax.set_xlabel("Number of Listings", fontsize=12)
ax.set_title("Real Estate Listings by City", fontsize=15, fontweight="bold", pad=15)
ax.tick_params(axis="y", labelsize=11)
ax.set_xlim(0, city_counts.values.max() * 1.12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save_chart(fig, "01_listings_by_city.png")

# ---------------------------------------------------------------------------
# Chart 2: Listings by Property Type
# ---------------------------------------------------------------------------
type_counts = df["property_type"].value_counts()
total_listings = len(df)
type_colors_list = [TYPE_COLORS.get(t, "#90a4ae") for t in type_counts.index]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(type_counts.index, type_counts.values, color=type_colors_list, edgecolor="white")
for bar, val in zip(bars, type_counts.values):
    pct = val / total_listings * 100
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total_listings * 0.003,
            f"{val}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_xlabel("Property Type", fontsize=12)
ax.set_ylabel("Number of Listings", fontsize=12)
ax.set_title("Listings by Property Type", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, type_counts.values.max() * 1.18)
ax.tick_params(axis="x", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save_chart(fig, "02_property_type_distribution.png")

# ---------------------------------------------------------------------------
# Chart 3: Median Price (USD) by City — top 12, ≥5 listings
# ---------------------------------------------------------------------------
city_stats = df.groupby("city").agg(count=("price_usd", "size"),
                                     median_usd=("price_usd", "median")).reset_index()
city_stats = city_stats[city_stats["count"] >= 5].nlargest(12, "median_usd").sort_values("median_usd")
n = len(city_stats)
colors_c3 = bar_color_gradient(n, ["#b3e5fc", "#01579b"])

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(city_stats["city"], city_stats["median_usd"], color=colors_c3, edgecolor="white")
max_val = city_stats["median_usd"].max()
for bar, val in zip(bars, city_stats["median_usd"]):
    ax.text(val + max_val * 0.005, bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}", va="center", ha="left", fontsize=10, fontweight="bold")
ax.set_xlabel("Median Price (USD)", fontsize=12)
ax.set_title("Median Listing Price by City (USD)", fontsize=15, fontweight="bold", pad=15)
ax.tick_params(axis="y", labelsize=11)
ax.set_xlim(0, max_val * 1.18)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${int(x):,}"))
fig.tight_layout()
save_chart(fig, "03_median_price_usd_by_city.png")

# ---------------------------------------------------------------------------
# Chart 4: Median Price by Property Type (USD) — exclude Other & Rental (Various)
# ---------------------------------------------------------------------------
exclude_types = {"Other", "Rental (Various)"}
type_price = (df[~df["property_type"].isin(exclude_types)]
              .groupby("property_type")["price_usd"]
              .median()
              .sort_values(ascending=True))
n = len(type_price)
type_bar_colors = [TYPE_COLORS.get(t, "#90a4ae") for t in type_price.index]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(type_price.index, type_price.values, color=type_bar_colors, edgecolor="white")
max_val = type_price.values.max()
for bar, val in zip(bars, type_price.values):
    ax.text(val + max_val * 0.005, bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}", va="center", ha="left", fontsize=10, fontweight="bold")
ax.set_xlabel("Median Price (USD)", fontsize=12)
ax.set_title("Median Price by Property Type (USD)", fontsize=15, fontweight="bold", pad=15)
ax.tick_params(axis="y", labelsize=11)
ax.set_xlim(0, max_val * 1.18)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${int(x):,}"))
fig.tight_layout()
save_chart(fig, "04_median_price_by_property_type.png")

# ---------------------------------------------------------------------------
# Chart 5: Price Distribution — buckets in USD
# ---------------------------------------------------------------------------
bins   = [0, 10_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, np.inf]
labels = ["Under $10K", "$10K–$50K", "$50K–$100K",
          "$100K–$200K", "$200K–$500K", "$500K–$1M", "Over $1M"]
df["price_bucket"] = pd.cut(df["price_usd"], bins=bins, labels=labels, right=False)
bucket_counts = df["price_bucket"].value_counts().reindex(labels).fillna(0).astype(int)
n = len(bucket_counts)
colors_c5 = bar_color_gradient(n, ["#e3f2fd", "#0d47a1"])

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(bucket_counts.index, bucket_counts.values, color=colors_c5, edgecolor="white")
for bar, val in zip(bars, bucket_counts.values):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bucket_counts.values.max() * 0.008,
                f"{val:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_xlabel("Price Range (USD)", fontsize=12)
ax.set_ylabel("Number of Listings", fontsize=12)
ax.set_title("Price Distribution — Number of Listings per Range (USD)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(0, bucket_counts.values.max() * 1.15)
ax.tick_params(axis="x", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save_chart(fig, "05_price_range_distribution.png")

# ---------------------------------------------------------------------------
# Chart 6: Sale vs. Rental — Top 8 Cities (grouped bar)
# ---------------------------------------------------------------------------
top8_cities = df["city"].value_counts().head(8).index.tolist()
df_top8 = df[df["city"].isin(top8_cities)].copy()
pivot = (df_top8.groupby(["city", "listing_type"])
         .size()
         .unstack(fill_value=0)
         .reindex(columns=["Sale", "Rental"], fill_value=0))
pivot = pivot.loc[top8_cities]  # maintain top-count order

x = np.arange(len(pivot))
width = 0.38
fig, ax = plt.subplots(figsize=(13, 6))
bars_sale   = ax.bar(x - width / 2, pivot["Sale"],   width, label="Sale",   color="#1565c0", edgecolor="white")
bars_rental = ax.bar(x + width / 2, pivot["Rental"], width, label="Rental", color="#00897b", edgecolor="white")

for bar in bars_sale:
    v = int(bar.get_height())
    if v > 0:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{v}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1565c0")
for bar in bars_rental:
    v = int(bar.get_height())
    if v > 0:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{v}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#00897b")

ax.set_xticks(x)
ax.set_xticklabels(pivot.index, fontsize=11)
ax.set_ylabel("Number of Listings", fontsize=12)
ax.set_title("Sale vs. Rental Listings — Top 8 Cities", fontsize=15, fontweight="bold", pad=15)
ax.legend(fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save_chart(fig, "06_sale_vs_rent_top_cities.png")

# ---------------------------------------------------------------------------
# Chart 7: Market Activity — Listing Freshness by Property Type (stacked bar)
# ---------------------------------------------------------------------------
freshness = (df.groupby(["property_type", "is_today"])
             .size()
             .unstack(fill_value=0)
             .rename(columns={True: "Posted Today", False: "Posted Earlier"}))
# ensure both columns exist
for col in ["Posted Today", "Posted Earlier"]:
    if col not in freshness.columns:
        freshness[col] = 0
freshness["total"] = freshness["Posted Today"] + freshness["Posted Earlier"]
freshness = freshness.sort_values("total", ascending=False)

fig, ax = plt.subplots(figsize=(13, 6))
ax.bar(freshness.index, freshness["Posted Earlier"], label="Posted Earlier",
       color="#90caf9", edgecolor="white")
ax.bar(freshness.index, freshness["Posted Today"],   label="Posted Today",
       bottom=freshness["Posted Earlier"], color="#1565c0", edgecolor="white")

for i, (pt, row) in enumerate(freshness.iterrows()):
    total = row["total"]
    today = row["Posted Today"]
    pct = today / total * 100 if total > 0 else 0
    ax.text(i, total + freshness["total"].max() * 0.008,
            f"{pct:.0f}%", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color="#0d47a1")

ax.set_ylabel("Number of Listings", fontsize=12)
ax.set_xlabel("Property Type", fontsize=12)
ax.set_title("Market Activity — Listing Freshness by Property Type",
             fontsize=14, fontweight="bold", pad=15)
ax.tick_params(axis="x", labelsize=10)
ax.set_ylim(0, freshness["total"].max() * 1.14)
ax.legend(fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save_chart(fig, "07_market_activity_freshness.png")

# ---------------------------------------------------------------------------
# Data Summary Report
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("DATA SUMMARY REPORT")
print("=" * 60)
print(f"Total listings (after filter): {len(df):,}")
print(f"  - Sale:   {(df['listing_type']=='Sale').sum():,}")
print(f"  - Rental: {(df['listing_type']=='Rental').sum():,}")
print(f"  - Posted today: {df['is_today'].sum():,} ({df['is_today'].mean()*100:.1f}%)")
print()
print("Price stats (USD):")
print(f"  Min:    ${df['price_usd'].min():,}")
print(f"  Median: ${df['price_usd'].median():,.0f}")
print(f"  Mean:   ${df['price_usd'].mean():,.0f}")
print(f"  Max:    ${df['price_usd'].max():,}")
print()
print("Top 5 cities by listing count:")
for city, cnt in df["city"].value_counts().head(5).items():
    print(f"  {city}: {cnt:,}")
print()
print("Listings by property type:")
for pt, cnt in df["property_type"].value_counts().items():
    pct = cnt / len(df) * 100
    print(f"  {pt}: {cnt:,} ({pct:.1f}%)")
print()
print("Median price (USD) by property type (excl. Other / Rental-Various):")
for pt, med in type_price.sort_values(ascending=False).items():
    print(f"  {pt}: ${med:,.0f}")
print("=" * 60)
print("All 7 charts saved to:", CHARTS_DIR)
