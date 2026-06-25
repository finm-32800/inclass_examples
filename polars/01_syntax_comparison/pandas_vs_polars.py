"""
Pandas vs Polars: side-by-side syntax comparison.

Demonstrates why Polars has a more consistent, less error-prone API
than pandas, using synthetic daily stock return data.

Usage:
    python pandas_vs_polars.py
"""

import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
import polars as pl


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------

def generate_stock_data(n_tickers: int = 10, n_days: int = 10, seed: int = 42):
    """Generate a small DataFrame of daily stock data in both libraries."""
    rng = np.random.default_rng(seed)

    tickers = [f"TICK{i:02d}" for i in range(n_tickers)]
    sectors = ["Technology", "Healthcare", "Finance"]
    dates = [date(2024, 1, 2) + timedelta(days=i) for i in range(n_days)]

    rows = []
    for d in dates:
        for t in tickers:
            rows.append({
                "date": d,
                "ticker": t,
                "sector": rng.choice(sectors),
                "return_pct": round(rng.normal(0, 0.02), 6),
                "volume": int(rng.lognormal(mean=14, sigma=1)),
                "price": round(rng.uniform(10, 500), 2),
            })

    pdf = pd.DataFrame(rows)
    plf = pl.DataFrame(rows)
    return pdf, plf


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def sub(label: str):
    print(f"\n--- {label} ---")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pdf, plf = generate_stock_data()

    # ======================================================================
    # 1. Creating & inspecting DataFrames
    # ======================================================================
    section("1. Creating & Inspecting DataFrames")

    sub("pandas dtypes")
    print(pdf.dtypes)

    sub("polars schema (explicit types, no ambiguity)")
    print(plf.schema)

    sub("pandas head")
    print(pdf.head(3).to_string(index=False))

    sub("polars head")
    print(plf.head(3))

    # ======================================================================
    # 2. Selecting columns
    # ======================================================================
    section("2. Selecting Columns")

    sub("pandas: df[['ticker','return_pct']] — returns DataFrame")
    print(type(pdf[["ticker", "return_pct"]]))

    sub("pandas: df['ticker'] — returns Series (inconsistent!)")
    print(type(pdf["ticker"]))

    sub("polars: df.select() ALWAYS returns a DataFrame")
    print(type(plf.select("ticker")))
    print(type(plf.select("ticker", "return_pct")))

    sub("polars: regex column selection")
    print(plf.select(pl.col("^.*pct$")).head(3))

    # ======================================================================
    # 3. Filtering rows
    # ======================================================================
    section("3. Filtering Rows")

    sub("pandas: df[df['return_pct'] > 0]")
    pos_pd = pdf[pdf["return_pct"] > 0]
    print(f"  {len(pos_pd)} rows with positive returns")

    sub("polars: df.filter() — one way to filter, no confusion")
    pos_pl = plf.filter(pl.col("return_pct") > 0)
    print(f"  {pos_pl.height} rows with positive returns")

    sub("polars: compound filters are clean")
    result = plf.filter(
        (pl.col("return_pct") > 0) & 
        (pl.col("sector") == "Technology")
    )
    print(f"  {result.height} positive-return Technology rows")

    # ======================================================================
    # 4. The SettingWithCopyWarning problem
    # ======================================================================
    section("4. SettingWithCopyWarning (pandas-only problem)")

    sub("pandas: filtering then assigning triggers a warning")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        filtered = pdf[pdf["sector"] == "Technology"]
        # This may trigger SettingWithCopyWarning depending on pandas version
        try:
            filtered["log_return"] = np.log(1 + filtered["return_pct"])
            if w:
                print(f"  WARNING triggered: {w[0].category.__name__}")
            else:
                print("  (pandas 3.x+ may use copy-on-write; older versions warn)")
        except Exception as e:
            print(f"  Error: {e}")

    sub("polars: filter + with_columns — no warnings, no ambiguity")
    result = (
        plf
        .filter(pl.col("sector") == "Technology")
        .with_columns(pl.col("return_pct").log1p().alias("log_return"))
    )
    print(result.head(3))

    # ======================================================================
    # 5. Conditional logic
    # ======================================================================
    section("5. Conditional Logic")

    sub("pandas: np.where (not very readable)")
    pdf_cond = pdf.copy()
    pdf_cond["direction"] = np.where(pdf_cond["return_pct"] > 0, "up", "down")
    print(pdf_cond[["ticker", "return_pct", "direction"]].head(5).to_string(index=False))

    sub("polars: pl.when().then().otherwise() — reads like English")
    result = plf.with_columns(
        pl.when(pl.col("return_pct") > 0)
        .then(pl.lit("up"))
        .otherwise(pl.lit("down"))
        .alias("direction")
    )
    print(result.select("ticker", "return_pct", "direction").head(5))

    sub("polars: nested conditions (multi-level classification)")
    result = plf.with_columns(
        pl.when(pl.col("return_pct") > 0.01)
        .then(pl.lit("strong_up"))
        .when(pl.col("return_pct") > 0)
        .then(pl.lit("weak_up"))
        .when(pl.col("return_pct") > -0.01)
        .then(pl.lit("weak_down"))
        .otherwise(pl.lit("strong_down"))
        .alias("signal")
    )
    print(result.select("ticker", "return_pct", "signal").head(5))

    # ======================================================================
    # 6. GroupBy + aggregation
    # ======================================================================
    section("6. GroupBy + Aggregation")

    sub("pandas: multiple agg calls or dict syntax")
    print(
        pdf.groupby("sector")
        .agg(
            avg_return=("return_pct", "mean"),
            total_volume=("volume", "sum"),
            num_obs=("ticker", "count"),
        )
        .to_string()
    )

    sub("polars: multiple expressions in a single .agg() — clean and explicit")
    print(
        plf.group_by("sector").agg(
            pl.col("return_pct").mean().alias("avg_return"),
            pl.col("volume").sum().alias("total_volume"),
            pl.col("ticker").count().alias("num_obs"),
        )
    )

    # ======================================================================
    # 7. Window functions (groupby().transform vs .over())
    # ======================================================================
    section("7. Window Functions")

    sub("pandas: groupby().transform() — verbose")
    pdf_win = pdf.copy()
    pdf_win["sector_avg"] = pdf_win.groupby("sector")["return_pct"].transform("mean")
    print(pdf_win[["ticker", "sector", "return_pct", "sector_avg"]].head(5).to_string(index=False))

    sub("polars: .over() — intuitive, reads naturally")
    result = plf.with_columns(
        pl.col("return_pct").mean().over("sector").alias("sector_avg")
    )
    print(result.select("ticker", "sector", "return_pct", "sector_avg").head(5))

    sub("polars: rank within group")
    result = plf.with_columns(
        pl.col("volume").rank(descending=True).over("date").alias("volume_rank")
    )
    print(result.select("date", "ticker", "volume", "volume_rank").head(5))

    # ======================================================================
    # 8. Method chaining — where polars really shines
    # ======================================================================
    section("8. Method Chaining: Full Analytical Pipeline")

    sub("pandas: typically requires intermediate variables")
    temp = pdf[pdf["return_pct"].abs() < 0.05].copy()
    temp["log_return"] = np.log(1 + temp["return_pct"])
    result_pd = (
        temp.groupby("sector")
        .agg(
            avg_log_return=("log_return", "mean"),
            total_volume=("volume", "sum"),
            count=("ticker", "count"),
        )
        .sort_values("avg_log_return", ascending=False)
    )
    print(result_pd.to_string())

    sub("polars: one readable chain, no intermediate variables")
    result_pl = (
        plf
        .filter(pl.col("return_pct").abs() < 0.05)
        .with_columns(pl.col("return_pct").log1p().alias("log_return"))
        .group_by("sector")
        .agg(
            pl.col("log_return").mean().alias("avg_log_return"),
            pl.col("volume").sum().alias("total_volume"),
            pl.col("ticker").count().alias("count"),
        )
        .sort("avg_log_return", descending=True)
    )
    print(result_pl)

    print("\nDone! Polars provides a consistent, readable API with no gotchas.")
