"""
Check what your Nasdaq Data Link API key can actually see.

Nasdaq Data Link has two data structures:

* Time-series ("datasets", ``/api/v3/datasets/VENDOR/CODE``): retired. Every
  call now returns an HTML 403 from the bot-protection layer, and the database
  listing returns ``410 Gone``. Nothing in this directory uses it.
* Tables ("datatables", ``/api/v3/datatables/VENDOR/TABLE``): what works today.

The trap this script exposes: a *premium* table answers HTTP 200 to any
registered key, because each premium product ships a free sample (about 30
large-cap tickers over a short window that ended years ago). A 200 therefore
proves nothing about your subscription. The reliable test is to ask for recent
rows and see whether any come back.

Usage:
    python 01_check_key.py
"""

from datetime import date, timedelta
from pathlib import Path

import requests
from decouple import Config, RepositoryEnv

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
config = Config(RepositoryEnv(repo_root / ".env"))
API_KEY = config("NASDAQ_DATA_API_KEY")

BASE = "https://data.nasdaq.com/api/v3"
FREE_TABLE = "NDAQ/RTAT10"  # Retail Trading Activity Tracker, daily top 10 (free)
PREMIUM_TABLE = "SHARADAR/SEP"  # Sharadar Equity Prices (premium, has a sample)
LOCKED_TABLE = "EOD/PRICES"  # premium, no free sample at all
CANARY_TICKER = "NFLX"  # liquid, listed since 2002, not one of the ~30 names in the free samples
RECENT_DAYS = 180


def get(path, **params):
    """GET a path with the key attached. Never print the URL: it contains the key."""
    return requests.get(f"{BASE}/{path}", params={"api_key": API_KEY, **params}, timeout=60)


def section(title):
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


# ── 1. Is the key valid at all? ──────────────────────────────────────
section(f"1. Key check: metadata for {FREE_TABLE}")
r = get(f"datatables/{FREE_TABLE}/metadata.json")
print("status:", r.status_code)
ratelimit = {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")}
print("rate-limit headers:", ratelimit or "(none on this endpoint)")
if r.status_code != 200:
    raise SystemExit(f"Key rejected: {r.text[:200]}")
meta = r.json()["datatable"]
print(f"table: {meta['name']!r}  premium={meta['premium']}  refreshed_at={meta['status']['refreshed_at']}")

# ── 2. Free table: full, current history ─────────────────────────────
section(f"2. Free table {FREE_TABLE}: rows from the last 14 days")
since = str(date.today() - timedelta(days=14))
r = get(f"datatables/{FREE_TABLE}.json", **{"ticker": "TSLA", "date.gte": since, "qopts.per_page": 3})
print("rate-limit headers:", {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")})
rows = r.json()["datatable"]["data"]
print(f"status: {r.status_code}, rows since {since}: {len(rows)}")
for row in rows:
    print("  ", row)

# ── 3. Premium table: HTTP 200, but is it just the sample? ───────────
section(f"3. Premium table {PREMIUM_TABLE}: HTTP 200 does not mean subscribed")
meta = get(f"datatables/{PREMIUM_TABLE}/metadata.json").json()["datatable"]
print(f"vendor metadata: premium={meta['premium']}, refreshed_at={meta['status']['refreshed_at']}")

r = get(f"datatables/{PREMIUM_TABLE}.json", **{"qopts.columns": "ticker,date", "qopts.per_page": 10000})
j = r.json()
data = j["datatable"]["data"]
tickers = sorted({row[0] for row in data})
dates = sorted(row[1] for row in data)
print(f"status: {r.status_code}")
print(
    f"unfiltered first page: {len(data)} rows, {len(tickers)} tickers, "
    f"dates {dates[0]} .. {dates[-1]}, more pages: {j['meta'].get('next_cursor_id') is not None}"
)
print("tickers:", " ".join(tickers))

cutoff = str(date.today() - timedelta(days=RECENT_DAYS))
recent = get(f"datatables/{PREMIUM_TABLE}.json", **{"date.gte": cutoff, "qopts.per_page": 1}).json()["datatable"]["data"]
canary = get(f"datatables/{PREMIUM_TABLE}.json", ticker=CANARY_TICKER, **{"qopts.per_page": 1}).json()["datatable"]["data"]
print(f"\nrows on/after {cutoff}:            {'YES' if recent else 'NONE'}")
print(f"rows for {CANARY_TICKER} (outside the sample set): {'YES' if canary else 'NONE'}")
if recent and canary:
    print("Both tests pass: your key sees live data for the whole universe, so a subscription is attached.")
else:
    print("Your key sees only the free sample: a fixed set of large caps, "
          f"newest row {dates[-1]}, while the vendor refreshed the table on {meta['status']['refreshed_at'][:10]}.")
    print("Some samples run to today (SHARADAR/SP500, SHARADAR/ACTIONS), which is why the canary ticker test matters.")

# ── 4. Premium table with no sample: the only true 'forbidden' ───────
section(f"4. Locked premium table {LOCKED_TABLE}")
r = get(f"datatables/{LOCKED_TABLE}.json", **{"qopts.per_page": 1})
print("status:", r.status_code)
print("message:", r.json().get("quandl_error", {}).get("message", r.text[:200]))

# ── 5. A table that does not exist ───────────────────────────────────
section("5. Nonexistent table NDAQ/NOPE")
r = get("datatables/NDAQ/NOPE.json")
print("status:", r.status_code, "|", r.json().get("quandl_error", {}).get("message"))

# ── 6. The retired time-series API ───────────────────────────────────
section("6. Retired time-series API (/datasets, /databases)")
for path in ("datasets/LBMA/GOLD.json", "databases.json"):
    r = get(path)
    ct = r.headers.get("content-type", "").split(";")[0]
    print(f"GET /{path:24} -> {r.status_code}  content-type={ct}")
print("An HTML 403 and a 410 Gone: the old time-series endpoints are no longer served.")
