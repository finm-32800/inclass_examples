"""
LazyFrames and query optimization in Polars.

Demonstrates eager vs lazy execution, query plans, and the pushdown
optimizations (predicate + projection) that make Polars fast on medium
to large datasets.

Usage:
    python lazy_and_pushdown.py
"""

import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "output"
PARQUET_PATH = OUTPUT_DIR / "stock_data.parquet"

N_TICKERS = 50
N_DAYS = 2_000  # ~100K rows total


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------

def generate_wide_stock_data(n_tickers: int, n_days: int, seed: int = 42) -> pl.DataFrame:
    """Generate a wide DataFrame with many columns (simulating factor data)."""
    rng = np.random.default_rng(seed)

    tickers = [f"TICK{i:03d}" for i in range(n_tickers)]
    sectors = [
        "Technology", "Healthcare", "Finance", "Energy", "Consumer",
        "Industrial", "Materials", "Utilities", "RealEstate", "Telecom",
    ]
    dates = [date(2005, 1, 3) + timedelta(days=i) for i in range(n_days)]

    n_rows = n_tickers * n_days

    data = {
        "date": [d for d in dates for _ in range(n_tickers)],
        "ticker": tickers * n_days,
        "sector": [rng.choice(sectors) for _ in range(n_rows)],
        "return_pct": rng.normal(0, 0.02, n_rows).round(6).tolist(),
        "volume": rng.lognormal(mean=14, sigma=1, size=n_rows).astype(int).tolist(),
        "price": rng.uniform(10, 500, n_rows).round(2).tolist(),
        "market_cap": rng.lognormal(mean=23, sigma=2, size=n_rows).round(0).tolist(),
        "bid_ask_spread": rng.exponential(0.01, n_rows).round(6).tolist(),
    }

    # Add 12 "factor exposure" columns to make the dataset wide
    for i in range(12):
        data[f"factor_{i:02d}"] = rng.normal(0, 1, n_rows).round(4).tolist()

    return pl.DataFrame(data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def sub(label: str):
    print(f"\n--- {label} ---")


def time_it(label: str, func):
    """Time a function and print the result."""
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    print(f"  {label}: {elapsed:.4f}s")
    return result, elapsed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # -- Generate and save data ------------------------------------------------
    section("Setup: Generating synthetic data")
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not PARQUET_PATH.exists():
        print(f"  Generating {N_TICKERS} tickers × {N_DAYS} days = {N_TICKERS * N_DAYS:,} rows ...")
        df = generate_wide_stock_data(N_TICKERS, N_DAYS)
        df.write_parquet(PARQUET_PATH)
        print(f"  Written to {PARQUET_PATH} ({PARQUET_PATH.stat().st_size / 1e6:.1f} MB)")
    else:
        print(f"  Using existing {PARQUET_PATH}")
        df = pl.read_parquet(PARQUET_PATH)
        type(df)

        df = pl.scan_parquet(PARQUET_PATH)
        type(df)
        df
        dff = df.filter(pl.col("sector") == "Technology")
        dff
        dff.collect()
        df.collect()

    print(f"  Shape: {df.shape}  |  Columns: {df.columns[:6]} ... ({len(df.columns)} total)")

    # ======================================================================
    # 1. Eager vs Lazy
    # ======================================================================
    section("1. Eager vs Lazy Execution")

    sub("Eager: each step executes immediately")
    print("  df = pl.read_parquet(...)      # loads ALL data into memory NOW")
    print("  df.filter(...)                 # executes filter NOW, allocates new DataFrame")
    print("  df.select(...)                 # executes select NOW, allocates again")
    print()

    sub("Lazy: build a plan, execute once")
    lf = df.lazy()
    print(f"  type(df.lazy()) = {type(lf)}")
    print("  Nothing has executed yet — lf is just a plan.")
    print("  Only .collect() triggers execution.")

    # ======================================================================
    # 2. scan_parquet — lazy from the start
    # ======================================================================
    section("2. scan_parquet(): Lazy From the Start")

    sub("scan_parquet returns a LazyFrame instantly (no data loaded)")
    start = time.perf_counter()
    lf_scan = pl.scan_parquet(PARQUET_PATH)
    scan_time = time.perf_counter() - start
    print(f"  pl.scan_parquet() took {scan_time:.6f}s (essentially instant)")
    print(f"  type: {type(lf_scan)}")
    print(f"  schema: {lf_scan.collect_schema()}")

    # ======================================================================
    # 3. Query plans
    # ======================================================================
    section("3. Reading Query Plans with .explain()")

    query = (
        pl.scan_parquet(PARQUET_PATH)
        .filter(pl.col("sector") == "Technology")
        .select("date", "ticker", "return_pct", "volume")
        .group_by("ticker")
        .agg(
            pl.col("return_pct").mean().alias("avg_return"),
            pl.col("volume").sum().alias("total_volume"),
        )
    )

    sub("Naive (unoptimized) plan")
    print(query.explain(optimized=False))

    sub("Optimized plan (default)")
    print(query.explain())
    print("  ^ Notice: the FILTER moved into the SCAN (predicate pushdown)")
    print("    and unused columns were dropped (projection pushdown)")

    # ======================================================================
    # 4. Predicate pushdown
    # ======================================================================
    section("4. Predicate Pushdown")
    print("  Filter to ~10% of rows (one sector out of ten).\n")

    sub("Eager: read everything, then filter")
    _, eager_time = time_it(
        "read_parquet + filter",
        lambda: pl.read_parquet(PARQUET_PATH).filter(pl.col("sector") == "Technology"),
    )

    sub("Lazy: filter is pushed into the parquet reader")
    _, lazy_time = time_it(
        "scan_parquet + filter + collect",
        lambda: (
            pl.scan_parquet(PARQUET_PATH)
            .filter(pl.col("sector") == "Technology")
            .collect()
        ),
    )

    print(f"\n  Speedup: {eager_time / lazy_time:.1f}x")

    # ======================================================================
    # 5. Projection pushdown
    # ======================================================================
    section("5. Projection Pushdown")
    n_cols = len(df.columns)
    print(f"  Select 3 of {n_cols} columns.\n")

    sub("Eager: read all columns, then select")
    _, eager_time = time_it(
        "read_parquet + select 3 cols",
        lambda: pl.read_parquet(PARQUET_PATH).select("date", "ticker", "return_pct"),
    )

    sub("Lazy: only needed columns are read from disk")
    _, lazy_time = time_it(
        "scan_parquet + select 3 cols + collect",
        lambda: (
            pl.scan_parquet(PARQUET_PATH)
            .select("date", "ticker", "return_pct")
            .collect()
        ),
    )

    print(f"\n  Speedup: {eager_time / lazy_time:.1f}x")

    # ======================================================================
    # 6. Combined pushdowns
    # ======================================================================
    section("6. Combined: Predicate + Projection Pushdown")
    print("  Filter to 1 sector AND select 3 columns.\n")

    sub("Eager: read everything, filter, then select")
    _, eager_time = time_it(
        "eager",
        lambda: (
            pl.read_parquet(PARQUET_PATH)
            .filter(pl.col("sector") == "Technology")
            .select("date", "ticker", "return_pct")
        ),
    )

    sub("Lazy: both pushdowns applied")
    _, lazy_time = time_it(
        "lazy",
        lambda: (
            pl.scan_parquet(PARQUET_PATH)
            .filter(pl.col("sector") == "Technology")
            .select("date", "ticker", "return_pct")
            .collect()
        ),
    )

    print(f"\n  Speedup: {eager_time / lazy_time:.1f}x")

    sub("Optimized query plan (see both pushdowns)")
    plan = (
        pl.scan_parquet(PARQUET_PATH)
        .filter(pl.col("sector") == "Technology")
        .select("date", "ticker", "return_pct")
    )
    print(plan.explain())

    # ======================================================================
    # Summary
    # ======================================================================
    section("Summary")
    print(
        "  LazyFrames let Polars optimize your query before running it.\n"
        "  Predicate pushdown avoids reading rows you don't need.\n"
        "  Projection pushdown avoids reading columns you don't need.\n"
        "  Together, they can dramatically reduce I/O and memory usage.\n"
        "  Always prefer scan_parquet() + .collect() over read_parquet()."
    )
