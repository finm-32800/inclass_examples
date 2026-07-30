"""
Treasury Futures Market Brief — 4 charts + 1 summary table.

Reads Parquet files produced by 01_fetch_data.py and generates:
    1. Indexed price series (normalized to 100)
    2. Curve spreads (10s-2s and 30s-5s)
    3. Volume & open interest bar chart
    4. 20-day rolling annualized volatility
    + Market snapshot table (printed to console)

Usage:
    python 02_market_brief.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Configuration ────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

PRODUCTS = ["ZT", "ZF", "ZN", "TN", "ZB"]
TENORS = {"ZT": "2Y", "ZF": "5Y", "ZN": "10Y", "TN": "Ultra 10Y", "ZB": "30Y"}
COLORS = {"ZT": "#1f77b4", "ZF": "#ff7f0e", "ZN": "#2ca02c", "TN": "#d62728", "ZB": "#9467bd"}

# ── Load data ────────────────────────────────────────────────────
df_ohlcv = pd.read_parquet(OUTPUT_DIR / "ohlcv_daily.parquet")
df_oi = pd.read_parquet(OUTPUT_DIR / "open_interest.parquet")

# Extract product root from symbol (e.g., "ZN.c.0" -> "ZN")
df_ohlcv["product"] = df_ohlcv["symbol"].str.split(".").str[0]

# Pivot to wide format: date × product
df_ohlcv["date"] = df_ohlcv.index if isinstance(df_ohlcv.index, pd.DatetimeIndex) else pd.to_datetime(df_ohlcv.index)
close = df_ohlcv.pivot_table(index="date", columns="product", values="close")
volume = df_ohlcv.pivot_table(index="date", columns="product", values="volume")

# Ensure curve order
close = close[[p for p in PRODUCTS if p in close.columns]]
volume = volume[[p for p in PRODUCTS if p in volume.columns]]

# ── Chart 1: Indexed Price Series ────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
indexed = close / close.iloc[0] * 100
for prod in indexed.columns:
    ax.plot(indexed.index, indexed[prod], label=f"{prod} ({TENORS[prod]})",
            color=COLORS[prod], linewidth=1.5)
ax.set_title("Treasury Futures — Indexed Price Performance", fontsize=14)
ax.set_ylabel("Index (Start = 100)")
ax.legend(loc="best")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "chart_indexed_prices.png", dpi=150)
plt.close(fig)
print("Saved: chart_indexed_prices.png")

# ── Chart 2: Curve Spreads ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
if "ZN" in close.columns and "ZT" in close.columns:
    spread_10s2s = close["ZN"] - close["ZT"]
    ax.plot(spread_10s2s.index, spread_10s2s, label="10s-2s (ZN − ZT)",
            color="#2ca02c", linewidth=1.5)
if "ZB" in close.columns and "ZF" in close.columns:
    spread_30s5s = close["ZB"] - close["ZF"]
    ax.plot(spread_30s5s.index, spread_30s5s, label="30s-5s (ZB − ZF)",
            color="#9467bd", linewidth=1.5)
ax.axhline(y=0, color="black", linewidth=0.8, linestyle="--")
ax.set_title("Treasury Futures — Curve Spreads", fontsize=14)
ax.set_ylabel("Price Spread (points)")
ax.legend(loc="best")
ax.grid(True, alpha=0.3)
ax.text(0.01, 0.01, "Raw price spread, not DV01-weighted",
        transform=ax.transAxes, fontsize=8, color="gray")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "chart_curve_spreads.png", dpi=150)
plt.close(fig)
print("Saved: chart_curve_spreads.png")

# ── Chart 3: Volume & Open Interest Bar Chart ────────────────────
avg_volume = volume.mean()
latest_oi = (
    df_oi.sort_values("date")
    .groupby("product")
    .last()["open_interest"]
)

# Align to curve order
bar_products = [p for p in PRODUCTS if p in avg_volume.index]
bar_labels = [f"{p} ({TENORS[p]})" for p in bar_products]
vol_vals = [avg_volume[p] for p in bar_products]
oi_vals = [latest_oi.get(p, 0) for p in bar_products]

x = np.arange(len(bar_products))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width / 2, vol_vals, width, label="Avg Daily Volume", color="#1f77b4")
bars2 = ax.bar(x + width / 2, oi_vals, width, label="Latest Open Interest", color="#ff7f0e")
ax.set_title("Treasury Futures — Volume & Open Interest", fontsize=14)
ax.set_ylabel("Contracts")
ax.set_xticks(x)
ax.set_xticklabels(bar_labels)
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "chart_volume_oi.png", dpi=150)
plt.close(fig)
print("Saved: chart_volume_oi.png")

# ── Chart 4: Rolling Volatility ──────────────────────────────────
returns = close.pct_change(fill_method=None)
rolling_vol = returns.rolling(20).std() * np.sqrt(252) * 100

fig, ax = plt.subplots(figsize=(12, 6))
for prod in rolling_vol.columns:
    ax.plot(rolling_vol.index, rolling_vol[prod], label=f"{prod} ({TENORS[prod]})",
            color=COLORS[prod], linewidth=1.5)
ax.set_title("Treasury Futures — 20-Day Rolling Annualized Volatility", fontsize=14)
ax.set_ylabel("Volatility (%)")
ax.legend(loc="best")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "chart_rolling_vol.png", dpi=150)
plt.close(fig)
print("Saved: chart_rolling_vol.png")

# ── Table: Market Snapshot ───────────────────────────────────────
print()
print("=" * 90)
print("Treasury Futures — Market Snapshot")
print("=" * 90)

rows = []
for prod in PRODUCTS:
    if prod not in close.columns:
        continue
    series = close[prod].dropna()
    last_price = series.iloc[-1]
    daily_chg = series.iloc[-1] - series.iloc[-2] if len(series) >= 2 else np.nan
    five_day_chg = series.iloc[-1] - series.iloc[-6] if len(series) >= 6 else np.nan
    avg_vol_20d = volume[prod].tail(20).mean() if prod in volume.columns else np.nan
    oi = latest_oi.get(prod, np.nan)
    rows.append({
        "Product": prod,
        "Tenor": TENORS[prod],
        "Last Price": f"{last_price:.3f}",
        "Daily Chg": f"{daily_chg:+.3f}",
        "5-Day Chg": f"{five_day_chg:+.3f}",
        "20D Avg Volume": f"{avg_vol_20d:,.0f}",
        "Open Interest": f"{oi:,.0f}",
    })

df_table = pd.DataFrame(rows)
print(df_table.to_string(index=False))
print()
