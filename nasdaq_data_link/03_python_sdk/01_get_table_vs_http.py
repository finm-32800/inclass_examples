"""
Side-by-side: the nasdaq-data-link SDK vs raw HTTP, running the SAME query.

One query both ways, so you can see what the SDK abstracts: auth, cursor
pagination, DataFrame construction, type conversion. Then the SDK-only
conveniences (table metadata, export_table) and what the retired
time-series get() does now.

Usage:
    python 01_get_table_vs_http.py
"""

from datetime import date, timedelta
from pathlib import Path

import nasdaqdatalink
import pandas as pd
import requests
from decouple import Config, RepositoryEnv

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
config = Config(RepositoryEnv(repo_root / ".env"))
API_KEY = config("NASDAQ_DATA_API_KEY")

TABLE = "NDAQ/RTAT10"  # Retail Trading Activity Tracker, daily top 10 (free)
TICKERS = ["TSLA", "NVDA"]
SINCE = str(date.today() - timedelta(days=365))
COLUMNS = ["date", "ticker", "activity", "sentiment"]
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Method 1: raw HTTP ───────────────────────────────────────────────
print("=" * 60 + "\nMethod 1: raw HTTP (requests)\n" + "=" * 60)
BASE = "https://data.nasdaq.com/api/v3/datatables"
session = requests.Session()
session.headers["X-Api-Token"] = API_KEY

frames, cursor = [], None
while True:
    params = {
        "ticker": ",".join(TICKERS),
        "date.gte": SINCE,
        "qopts.columns": ",".join(COLUMNS),
        "qopts.per_page": 10000,
    }
    if cursor:
        params["qopts.cursor_id"] = cursor
    r = session.get(f"{BASE}/{TABLE}.json", params=params, timeout=60)
    r.raise_for_status()
    j = r.json()
    frames.append(pd.DataFrame(j["datatable"]["data"], columns=[c["name"] for c in j["datatable"]["columns"]]))
    cursor = j["meta"].get("next_cursor_id")
    if not cursor:
        break
http_df = pd.concat(frames, ignore_index=True)
print(f"{len(http_df)} rows over {len(frames)} page(s)")
print("dtypes straight off the wire:", dict(http_df.dtypes.astype(str)))  # date is a string
http_df["date"] = pd.to_datetime(http_df["date"])

# ── Method 2: the SDK ────────────────────────────────────────────────
print("\n" + "=" * 60 + "\nMethod 2: nasdaq-data-link SDK\n" + "=" * 60)
# The SDK would also read NASDAQ_DATA_LINK_API_KEY or ~/.nasdaq/data_link_apikey.
# We keep the course-wide .env variable and hand it over explicitly.
nasdaqdatalink.ApiConfig.api_key = API_KEY

sdk_df = nasdaqdatalink.get_table(
    TABLE,
    ticker=TICKERS,  # a list becomes the comma-separated filter
    date={"gte": SINCE},  # a dict becomes date.gte=...
    qopts={"columns": COLUMNS},
    paginate=True,  # follow next_cursor_id for you
)
print(f"{len(sdk_df)} rows")
print("dtypes from the SDK:", dict(sdk_df.dtypes.astype(str)))  # date parsed already
print(sdk_df.head())

# ── Same data? ───────────────────────────────────────────────────────
key = ["date", "ticker"]
a = http_df.sort_values(key).reset_index(drop=True)
b = sdk_df.sort_values(key).reset_index(drop=True)[a.columns]
pd.testing.assert_frame_equal(a, b, check_dtype=False, check_names=False)
print("\nSame rows both ways: yes")

# ── SDK extras ───────────────────────────────────────────────────────
print("\n" + "=" * 60 + "\nSDK extras\n" + "=" * 60)
dt = nasdaqdatalink.Datatable(TABLE)
print("data_fields():", dt.data_fields())

zip_path = OUTPUT_DIR / "rtat10_tsla.zip"
nasdaqdatalink.export_table(TABLE, ticker="TSLA", filename=str(zip_path))  # bulk export, filtered
print(f"export_table wrote {zip_path.relative_to(repo_root)} ({zip_path.stat().st_size / 1e3:.0f} kB)")
print(pd.read_csv(zip_path).tail(3))

# ── The retired time-series API ──────────────────────────────────────
print("\n" + "=" * 60 + "\nnasdaqdatalink.get() (time-series API, retired)\n" + "=" * 60)
try:
    nasdaqdatalink.get("LBMA/GOLD", rows=1)
except nasdaqdatalink.DataLinkError as e:
    print(f"{type(e).__name__}: {str(e)[:110]}")
print("get() wraps /api/v3/datasets, which no longer serves data. Use get_table().")
