"""
Tables API with `requests`: filters, column selection, cursor pagination, bulk export.

Same endpoints as 01_curl_tables.sh, written the way you would in a pipeline:
loop on meta.next_cursor_id until it is null, build one DataFrame, and pull the
whole table as a zip through the export endpoint.

Usage:
    python 02_requests_pagination.py
"""

import io
import time
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
from decouple import Config, RepositoryEnv

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
config = Config(RepositoryEnv(repo_root / ".env"))
API_KEY = config("NASDAQ_DATA_API_KEY")

BASE = "https://data.nasdaq.com/api/v3/datatables"
TABLE = "NDAQ/RTAT10"  # Retail Trading Activity Tracker, daily top 10 (free)
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers["X-Api-Token"] = API_KEY  # header auth keeps the key out of URLs and logs


def fetch_table(table, **params):
    """Return every row matching `params` as one DataFrame, following cursors."""
    frames, cursor, page = [], None, 0
    while True:
        query = dict(params)
        if cursor:
            query["qopts.cursor_id"] = cursor
        r = session.get(f"{BASE}/{table}.json", params=query, timeout=60)
        r.raise_for_status()
        j = r.json()
        columns = [c["name"] for c in j["datatable"]["columns"]]
        frames.append(pd.DataFrame(j["datatable"]["data"], columns=columns))
        page += 1
        cursor = j["meta"].get("next_cursor_id")
        print(f"  page {page}: {len(frames[-1])} rows, next cursor: {'yes' if cursor else 'none'}")
        if not cursor:
            return pd.concat(frames, ignore_index=True)


# ── 1. Metadata ──────────────────────────────────────────────────────
print("=" * 60 + f"\n1. Metadata for {TABLE}\n" + "=" * 60)
meta = session.get(f"{BASE}/{TABLE}/metadata.json", timeout=60).json()["datatable"]
print("name:       ", meta["name"])
print("filters:    ", meta["filters"], "(only these columns accept =, .gte, .lte, ...)")
print("primary key:", meta["primary_key"])
print("columns:    ", [(c["name"], c["type"]) for c in meta["columns"]])
print("refreshed:  ", meta["status"]["refreshed_at"])

# ── 2. Filtered query, paginated ─────────────────────────────────────
print("\n" + "=" * 60 + "\n2. Filter + columns, small pages so the cursor shows up\n" + "=" * 60)
since = str(date.today() - timedelta(days=365))
df = fetch_table(
    TABLE,
    ticker="TSLA,NVDA",
    **{"date.gte": since, "qopts.columns": "date,ticker,activity,sentiment", "qopts.per_page": 200},
)
df["date"] = pd.to_datetime(df["date"])
print(df.head())
print("total rows:", len(df))
print(df.groupby("ticker")["activity"].agg(["count", "mean", "max"]).round(4))

# ── 3. Bulk export ───────────────────────────────────────────────────
print("\n" + "=" * 60 + "\n3. Bulk export: qopts.export=true\n" + "=" * 60)
for attempt in range(12):
    r = session.get(f"{BASE}/{TABLE}.json", params={"qopts.export": "true"}, timeout=60)
    r.raise_for_status()
    export = r.json()["datatable_bulk_download"]["file"]
    print(f"  status={export['status']!r}  snapshot={export['data_snapshot_time']}")
    if export["status"] == "fresh":
        break
    time.sleep(10)  # 'creating' / 'regenerating': the zip is being built server-side
else:
    raise SystemExit("export never became fresh; try again later")

zip_bytes = requests.get(export["link"], timeout=300).content  # pre-signed S3 URL: no key needed
zip_path = OUTPUT_DIR / f"{TABLE.replace('/', '_')}.zip"
zip_path.write_bytes(zip_bytes)
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
    names = z.namelist()
    full = pd.read_csv(z.open(names[0]))
print(f"  saved {zip_path.relative_to(repo_root)} ({len(zip_bytes) / 1e6:.2f} MB) containing {names}")
print(f"  full table: {len(full):,} rows x {full.shape[1]} cols, {full['date'].min()} .. {full['date'].max()}")
