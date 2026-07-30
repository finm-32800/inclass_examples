"""
Side-by-side comparison: raw HTTP requests vs Databento SDK.

Runs the SAME query both ways so you can see exactly what the SDK abstracts.

Usage:
    python 02_curl_vs_sdk.py
"""

from dotenv import load_dotenv
from pathlib import Path
import os
import json
import requests
import databento as db

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

API_KEY = os.environ["DATABENTO_API_KEY"]

# Common query parameters
DATASET = "GLBX.MDP3"
SYMBOL = "ES.FUT"
SCHEMA = "trades"
START = "2024-08-01"
END = "2024-08-02"
LIMIT = 5

# ── Method 1: Raw HTTP (what curl does) ─────────────────────────
print("=" * 60)
print("Method 1: Raw HTTP POST (requests library)")
print("=" * 60)

response = requests.post(
    "https://hist.databento.com/v0/timeseries.get_range",
    auth=(API_KEY, ""),  # HTTP Basic Auth: key as username, empty password
    data={
        "dataset": DATASET,
        "symbols": SYMBOL,
        "stype_in": "parent",
        "schema": SCHEMA,
        "start": START,
        "end": END,
        "encoding": "json",
        "limit": LIMIT,
    },
)
response.raise_for_status()

# The response is newline-delimited JSON (one record per line)
lines = response.text.strip().split("\n")
for line in lines:
    record = json.loads(line)
    # Two gotchas in the raw JSON that the SDK hides from you:
    #
    # 1. 64-bit integers are encoded as STRINGS ("5587750000000"), because JSON
    #    numbers are doubles and would lose precision. Cast with int() first.
    # 2. ts_event lives in the record header ("hd"), not at the top level.
    #    Only ts_recv is top-level.
    raw_price = int(record["price"])
    actual_price = raw_price * 1e-9  # fixed-point -> dollars
    ts_event = record["hd"]["ts_event"]
    print(f"  ts={ts_event}  price={raw_price} (raw) -> ${actual_price:.2f}")

# ── Method 2: SDK (what you'll normally use) ─────────────────────
print()
print("=" * 60)
print("Method 2: Databento SDK")
print("=" * 60)

client = db.Historical()

data = client.timeseries.get_range(
    dataset=DATASET,
    symbols=[SYMBOL],
    stype_in="parent",
    schema=SCHEMA,
    start=START,
    end=END,
    limit=LIMIT,
)

df = data.to_df()
for _, row in df.iterrows():
    print(f"  ts={row.name}  price=${row['price']:.2f} (auto-scaled)")

# ── Summary ──────────────────────────────────────────────────────
print()
print("=" * 60)
print("Key differences:")
print("  HTTP:  Manual auth, raw JSON, prices need 1e-9 scaling")
print("  SDK:   Auto auth, DataFrames, prices auto-scaled")
print("=" * 60)
