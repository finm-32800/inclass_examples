"""
Compare Databento's symbology types: parent vs raw_symbol.

Shows how the same underlying product (E-mini S&P 500) can be
referenced different ways depending on your use case.

Usage:
    python 01_symbology_types.py
"""

from dotenv import load_dotenv
from pathlib import Path
import databento as db

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

client = db.Historical()

# ── Parent symbology: ES.FUT (all ES futures) ───────────────────
print("=" * 60)
print("Symbology: parent — ES.FUT (all E-mini S&P 500 futures)")
print("=" * 60)

data_parent = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    symbols=["ES.FUT"],
    stype_in="parent",
    schema="trades",
    start="2024-08-01",
    end="2024-08-02",
    limit=5,
)

df_parent = data_parent.to_df()
print(df_parent[["symbol", "price", "size"]].to_string())
print()

# ── Raw symbol: specific contract (e.g., ESU4 = Sep 2024) ───────
print("=" * 60)
print("Symbology: raw_symbol — ESU4 (September 2024 contract)")
print("=" * 60)

data_raw = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    symbols=["ESU4"],
    stype_in="raw_symbol",
    schema="trades",
    start="2024-08-01",
    end="2024-08-02",
    limit=5,
)

df_raw = data_raw.to_df()
print(df_raw[["symbol", "price", "size"]].to_string())
print()

# ── Summary ──────────────────────────────────────────────────────
print("=" * 60)
print("Comparison:")
print(f"  parent (ES.FUT):       Returns trades from ALL active ES contracts")
print(f"  raw_symbol (ESU4):     Returns trades from ONE specific contract")
print()
print("Other symbology types:")
print("  continuous (ES.c.0):   Front-month contract (rolls automatically)")
print("  instrument_id (3403):  Numeric exchange ID (most compact)")
print("=" * 60)
