"""Pull the latest Treasury futures prices from Databento.

The API key is read from the DATABENTO_API_KEY environment variable, which
works identically in two settings:

  - Locally: `python-dotenv` loads it from the repo-root `.env` file.
  - GitHub Actions: the workflow passes the repository secret as an
    environment variable to this step. The key never appears in the code,
    the logs, or the git history.

Usage:
    python 01_pull_prices.py
"""

import os
from pathlib import Path

import databento as db
import pandas as pd
from dotenv import load_dotenv

# Load API key from repo-root .env (no-op in CI, where the variable is
# already set by the workflow)
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

if not os.environ.get("DATABENTO_API_KEY"):
    raise SystemExit(
        "ERROR: DATABENTO_API_KEY is not set.\n"
        "  Locally: add it to the repo-root .env file (see .env.example).\n"
        "  In GitHub Actions: add it as a repository secret and pass it as an\n"
        "  environment variable to this step:\n"
        "      env:\n"
        "        DATABENTO_API_KEY: ${{ secrets.DATABENTO_API_KEY }}"
    )

client = db.Historical()  # reads DATABENTO_API_KEY from the environment

# ── Configuration ────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "_output"
OUTPUT_DIR.mkdir(exist_ok=True)

DATASET = "GLBX.MDP3"

# Treasury futures across the curve, ordered by tenor
PRODUCTS = ["ZT", "ZF", "ZN", "TN", "ZB", "UB"]
TENORS = {
    "ZT": "2Y",
    "ZF": "5Y",
    "ZN": "10Y",
    "TN": "Ultra 10Y",
    "ZB": "30Y",
    "UB": "Ultra Bond",
}

# Continuous front-month symbols.
#
# We use ".v.0" (roll by VOLUME), not ".c.0" (roll by CALENDAR). The distinction
# matters a lot for Treasury futures:
#
#   .c.0  rolls only when the front contract expires. ZT and ZF stay listed
#         through the end of their delivery month, so .c.0 keeps pointing at a
#         contract that everyone has already rolled out of.
#   .v.0  rolls when volume migrates to the next expiration, which is the
#         contract whose price people actually mean by "the 10-year future."
SYMBOLS = [f"{p}.v.0" for p in PRODUCTS]

# ── Date range: last 10 days, clamped to what's available ────────
# Daily bars lag the clock: tick schemas update intraday, but ohlcv-1d only
# extends through the last completed session. Ask the (free) metadata API for
# the range of the *specific schema* we want — using the dataset's overall
# end would request bars that don't exist yet and fail with a 422.
range_info = client.metadata.get_dataset_range(dataset=DATASET)
available_end = pd.Timestamp(range_info["schema"]["ohlcv-1d"]["end"]).tz_localize(None)
end = min(pd.Timestamp.now("UTC").tz_localize(None), available_end)
start = end - pd.Timedelta(days=10)  # wide enough to span weekends/holidays

# ── Cost guard (free call) ───────────────────────────────────────
# On a subscription plan this prints $0.00; the guard is kept as a habit so
# that a badly-scoped query can never run up a surprise bill.
cost = client.metadata.get_cost(
    dataset=DATASET,
    symbols=SYMBOLS,
    stype_in="continuous",
    schema="ohlcv-1d",
    start=start,
    end=end,
)
print(f"Estimated cost: ${cost:.4f}")
if cost > 1.00:
    raise SystemExit(f"Aborting: estimated cost ${cost:.2f} exceeds $1.00 limit.")

# ── Pull daily bars and keep the latest close per product ────────
df = client.timeseries.get_range(
    dataset=DATASET,
    symbols=SYMBOLS,
    stype_in="continuous",
    schema="ohlcv-1d",
    start=start,
    end=end,
).to_df()

# The dataframe is indexed by ts_event; take the literal last row per symbol.
latest = df.sort_index().reset_index().groupby("symbol").tail(1).copy()
latest["product"] = latest["symbol"].str.split(".").str[0]
latest["date"] = latest["ts_event"].dt.date
latest["tenor"] = latest["product"].map(TENORS)

# Order by position on the curve
latest["order"] = latest["product"].map({p: i for i, p in enumerate(PRODUCTS)})
latest = latest.sort_values("order").drop(columns="order").reset_index(drop=True)

out_path = OUTPUT_DIR / "latest_prices.parquet"
latest[["product", "tenor", "symbol", "date", "close", "volume"]].to_parquet(out_path)
print(f"Saved {len(latest)} rows to {out_path}")
print(latest[["product", "tenor", "date", "close"]].to_string(index=False))
