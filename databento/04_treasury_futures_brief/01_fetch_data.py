"""
Fetch daily OHLCV and open interest for Treasury futures across the curve.

Pulls data for 5 products spanning the yield curve:
    ZT (2Y), ZF (5Y), ZN (10Y), TN (Ultra 10Y), ZB (30Y)

Two queries:
    1. OHLCV daily bars using continuous front-month contracts
    2. Statistics (open interest) using parent symbology

Usage:
    python 01_fetch_data.py
"""

from dotenv import load_dotenv
from pathlib import Path
import databento as db
import pandas as pd

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

client = db.Historical()

# ── Configuration ────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Hardcoded 6-month window
START = "2024-07-01"
END = "2025-01-01"

# # Alternative: relative date range
# from datetime import datetime, timedelta
# END = datetime.now().strftime("%Y-%m-%d")
# START = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

# Continuous front-month symbols for daily OHLCV.
#
# We use ".v.0" (roll by VOLUME), not ".c.0" (roll by CALENDAR). The distinction
# matters a lot for Treasury futures:
#
#   .c.0  rolls only when the front contract expires. ZT and ZF stay listed
#         through the end of their delivery month, so .c.0 keeps pointing at a
#         contract that everyone has already rolled out of — daily volume
#         collapses to double digits for weeks at a time.
#   .v.0  rolls when volume migrates to the next expiration, which is what
#         a market brief actually wants.
#
# Try switching to ".c.0" and re-running to see the difference for yourself.
OHLCV_SYMBOLS = ["ZT.v.0", "ZF.v.0", "ZN.v.0", "TN.v.0", "ZB.v.0"]

# Parent symbols for statistics (open interest across all expirations)
STATS_SYMBOLS = ["ZT.FUT", "ZF.FUT", "ZN.FUT", "TN.FUT", "ZB.FUT"]

DATASET = "GLBX.MDP3"

# Statistics query only needs recent data (open interest).
# Parent symbology × statistics schema is very large over long windows,
# so we limit to the last few days to keep the download fast.
STATS_START = (pd.Timestamp(END) - pd.Timedelta(days=5)).strftime("%Y-%m-%d")

# ── Step 1: Check costs (free calls) ────────────────────────────
print("=" * 60)
print("Cost Estimates")
print("=" * 60)

ohlcv_cost = client.metadata.get_cost(
    dataset=DATASET,
    symbols=OHLCV_SYMBOLS,
    stype_in="continuous",
    schema="ohlcv-1d",
    start=START,
    end=END,
)
print(f"  OHLCV daily:    ${ohlcv_cost:.4f}")

stats_cost = client.metadata.get_cost(
    dataset=DATASET,
    symbols=STATS_SYMBOLS,
    stype_in="parent",
    schema="statistics",
    start=STATS_START,
    end=END,
)
print(f"  Statistics:     ${stats_cost:.4f}")

total_cost = ohlcv_cost + stats_cost
print(f"  Total:          ${total_cost:.4f}")

if total_cost > 5.0:
    print(f"\n  WARNING: Total cost exceeds $5.00! Review before proceeding.")
    raise SystemExit(1)

print()

# ── Step 2: Fetch OHLCV daily bars ──────────────────────────────
print("=" * 60)
print(f"Fetching OHLCV daily bars ({START} to {END})")
print("=" * 60)

ohlcv_data = client.timeseries.get_range(
    dataset=DATASET,
    symbols=OHLCV_SYMBOLS,
    stype_in="continuous",
    schema="ohlcv-1d",
    start=START,
    end=END,
)

df_ohlcv = ohlcv_data.to_df()
ohlcv_path = OUTPUT_DIR / "ohlcv_daily.parquet"
df_ohlcv.to_parquet(ohlcv_path)
print(f"  Records: {len(df_ohlcv)}")
print(f"  Symbols: {df_ohlcv['symbol'].unique().tolist()}")
print(f"  Saved:   {ohlcv_path}")
print()

# ── Step 3: Fetch statistics (open interest) ────────────────────
print("=" * 60)
print(f"Fetching statistics ({STATS_START} to {END})")
print("=" * 60)

stats_data = client.timeseries.get_range(
    dataset=DATASET,
    symbols=STATS_SYMBOLS,
    stype_in="parent",
    schema="statistics",
    start=STATS_START,
    end=END,
)

df_stats = stats_data.to_df()
print(f"  Raw records: {len(df_stats)}")

# Filter to open interest (stat_type == 9)
# See: https://databento.com/docs/schemas-and-data-formats/whats-in-a-schema/statistics
df_oi = df_stats[df_stats["stat_type"] == 9].copy()
print(f"  Open interest records (stat_type=9): {len(df_oi)}")

# Drop calendar spreads (e.g. "ZNH5-ZNM5") — we want outright contracts only.
df_oi = df_oi[~df_oi["symbol"].str.contains("-")]

# ── Deduplicate before aggregating ───────────────────────────────
# CME publishes open interest for a given trade date TWICE: a preliminary
# figure shortly after the close, then a final figure the next morning. Both
# arrive as separate records with update_action=1, but they carry the SAME
# ts_ref (the trade date the statistic describes).
#
# Summing them naively double-counts open interest — the 10-Year would show
# ~9.1M contracts when the true figure is ~4.5M.
#
# The fix: group by (contract, ts_ref) and keep the record that arrived last,
# which is the final revision.
df_oi = df_oi.sort_index()  # ts_recv ascending
df_oi = df_oi.groupby(["symbol", "ts_ref"], as_index=False).last()

# The statistic describes ts_ref (the trade date), not when we received it.
df_oi["date"] = pd.to_datetime(df_oi["ts_ref"]).dt.normalize().dt.tz_localize(None)

# Extract product root from symbol (e.g., "ZNH5" -> "ZN")
df_oi["product"] = df_oi["symbol"].str.extract(r"^([A-Z]{2})")

# Aggregate OI across expirations per product per trade date
df_oi_agg = (
    df_oi.groupby(["date", "product"])["quantity"]
    .sum()
    .reset_index()
)
df_oi_agg.columns = ["date", "product", "open_interest"]

oi_path = OUTPUT_DIR / "open_interest.parquet"
df_oi_agg.to_parquet(oi_path, index=False)
print(f"  Aggregated records: {len(df_oi_agg)}")
print(f"  Saved:   {oi_path}")
print()

# ── Summary ─────────────────────────────────────────────────────
print("=" * 60)
print("Summary")
print("=" * 60)
for fpath in [ohlcv_path, oi_path]:
    size_kb = fpath.stat().st_size / 1024
    print(f"  {fpath.name}: {size_kb:.1f} KB")
print(f"\nTotal cost: ${total_cost:.4f}")
