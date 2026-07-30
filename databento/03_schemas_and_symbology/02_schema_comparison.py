"""
Compare Databento schemas: trades vs ohlcv-1s vs ohlcv-1m.

Fetches the same time window at three levels of granularity to show
the tradeoff between detail and data volume.

Usage:
    python 02_schema_comparison.py
"""

from dotenv import load_dotenv
from pathlib import Path
import databento as db

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

client = db.Historical()

# Common parameters
PARAMS = dict(
    dataset="GLBX.MDP3",
    symbols=["ES.FUT"],
    stype_in="parent",
    start="2024-08-01T14:30:00",  # 30 min window during market hours
    end="2024-08-01T15:00:00",
    limit=10,
)

# ── Schema 1: trades (tick-by-tick) ──────────────────────────────
print("=" * 60)
print("Schema: trades (every individual trade)")
print("=" * 60)

data_trades = client.timeseries.get_range(schema="trades", **PARAMS)
df_trades = data_trades.to_df()
print(df_trades[["symbol", "price", "size"]].to_string())
print(f"  → {len(df_trades)} records (limited to {PARAMS['limit']})")
print()

# ── Schema 2: ohlcv-1s (1-second bars) ──────────────────────────
print("=" * 60)
print("Schema: ohlcv-1s (1-second OHLCV bars)")
print("=" * 60)

data_1s = client.timeseries.get_range(schema="ohlcv-1s", **PARAMS)
df_1s = data_1s.to_df()
print(df_1s[["symbol", "open", "high", "low", "close", "volume"]].to_string())
print(f"  → {len(df_1s)} records (limited to {PARAMS['limit']})")
print()

# ── Schema 3: ohlcv-1m (1-minute bars) ──────────────────────────
print("=" * 60)
print("Schema: ohlcv-1m (1-minute OHLCV bars)")
print("=" * 60)

data_1m = client.timeseries.get_range(schema="ohlcv-1m", **PARAMS)
df_1m = data_1m.to_df()
print(df_1m[["symbol", "open", "high", "low", "close", "volume"]].to_string())
print(f"  → {len(df_1m)} records (limited to {PARAMS['limit']})")
print()

# ── Summary ──────────────────────────────────────────────────────
print("=" * 60)
print("Schema hierarchy (most → least granular):")
print("  trades    — every tick (highest volume, highest cost)")
print("  ohlcv-1s  — 1-second bars")
print("  ohlcv-1m  — 1-minute bars")
print("  ohlcv-1h  — 1-hour bars")
print("  ohlcv-1d  — daily bars (lowest volume, lowest cost)")
print()
print("Rule of thumb: use the coarsest schema that meets your needs.")
print("=" * 60)
