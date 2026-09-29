"""
Sweep a list of Nasdaq Data Link tables and report what this key can see.

There is no API endpoint that lists your entitlements (the old
``/api/v3/databases`` listing is gone), so this script probes a curated list of
table codes and classifies each one:

    current    recent rows exist AND a liquid ticker outside the vendors'
               ~30-name sample set returns rows: full, live access
    sample     a fixed slice of large caps, whether or not its dates reach
               today: the free preview, not the product
    stale      free table whose vendor stopped updating it
    unknown    no filterable date column, so recency cannot be tested
    forbidden  HTTP 403: the table exists, has no free sample, and you are
               not subscribed
    missing    HTTP 404: no such table

Two tests per table. Recency: any rows in the last RECENT_DAYS days? Canary:
any rows for CANARY_TICKER? The samples are the same ~30 large caps in every
vendor's tables, and for some tables (SHARADAR/SP500, SHARADAR/ACTIONS) the
sample window runs to today, so recency alone is not enough.

Writes output/access_sweep.csv and prints a summary grouped by verdict.
Roughly four API calls per table; the authenticated limit is 300 calls per
10 seconds, so the whole sweep takes about a minute.

Usage:
    python 02_sweep_tables.py
"""

import time
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
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
RECENT_DAYS = 180
SAMPLE_MAX_ENTITIES = 50  # a premium sample covers ~30 tickers
CANARY_TICKER = "NFLX"  # liquid, listed since 2002, not one of the ~30 sample names
# Tables whose universe is not US tickers need their own canary: something a
# subscriber sees and the free sample does not (the AR sample is ICE Cocoa only).
CANARY_OVERRIDES = {
    "AR/IVM": {"exchange_code": "CME", "futures_code": "ES"},
    "AR/IVS": {"exchange_code": "CME", "futures_code": "ES"},
    "EDI/ASAP": {"mic": "XNSE", "year": str(date.today().year)},
    "EDI/ASAF": {"market": "XNSE"},
}
PAUSE = 0.1  # seconds between calls

# Every code below existed on 2026-09-22. Add your own; unknown codes just
# come back as "missing".
TABLES = {
    # Licensed to the University of Chicago (Account > Data access via your organization)
    "NDAQ/USEDH": "U.S. Equity Daily History: unadjusted OHLCV, all US exchanges",
    "EDI/CUR": "Foreign Exchange Rates: 188 currencies vs USD, daily since 2000",
    "EDI/ASAP": "Asian End of Day Pricing: adjusted OHLCV, 9 Asian exchanges, since 2005",
    "EDI/ASAF": "Asian End of Day Pricing: adjustment factors (corporate actions)",
    "AR/IVM": "Futures Options: implied vol model (ATM, risk reversals, flies, skew betas)",
    "AR/IVS": "Futures Options: implied vol surfaces by delta",
    # Nasdaq
    "NDAQ/RTAT10": "Retail Trading Activity Tracker, daily top 10 (free)",
    "NDAQ/RTAT": "Retail Trading Activity Tracker, full universe",
    "NDAQ/IPO": "Nasdaq IPO announcements",
    # Sharadar (Core US Equities bundle)
    "SHARADAR/TICKERS": "Securities master (free)",
    "SHARADAR/INDICATORS": "Data dictionary for the Sharadar tables (free)",
    "SHARADAR/EVENTS": "8-K event codes (free)",
    "SHARADAR/SEP": "Equity prices, daily",
    "SHARADAR/SFP": "Fund (ETF) prices, daily",
    "SHARADAR/DAILY": "Daily valuation metrics (EV, market cap, P/E)",
    "SHARADAR/METRICS": "Beta, 52-week range, dividend yields",
    "SHARADAR/SF1": "Core US fundamentals",
    "SHARADAR/SF2": "Insider transactions (Forms 3/4/5)",
    "SHARADAR/SF3": "Institutional holdings (13F)",
    "SHARADAR/ACTIONS": "Corporate actions",
    "SHARADAR/SP500": "S&P 500 constituents, current and historical",
    # Zacks (FC, FR, MKTV, SHRS, HDM, MT = "North American Fundamentals Collection B")
    "ZACKS/MT": "Master table",
    "ZACKS/FC": "Fundamentals condensed",
    "ZACKS/FR": "Fundamental ratios",
    "ZACKS/MKTV": "Market value",
    "ZACKS/SHRS": "Shares outstanding",
    "ZACKS/EE": "Earnings estimates",
    "ZACKS/ES": "Earnings surprises",
    "ZACKS/EA": "Earnings announcement dates",
    "ZACKS/SS": "Sales surprises",
    "ZACKS/CP": "Company profiles",
    "ZACKS/HDM": "Dividend history",
    # QuoteMedia
    "QUOTEMEDIA/PRICES": "End-of-day US stock prices (vendor stopped updating June 2025)",
    "QUOTEMEDIA/DAILYPRICES": "Latest-day prices",
    "QUOTEMEDIA/TICKERS": "Ticker list",
    # Other premium vendors
    "EOD/PRICES": "End of Day US Stock Prices",
    "EOD/TICKERS": "End of Day US Stock Prices, ticker list",
    "MER/F1": "Mergent global fundamentals",
    "ETFG/FUND": "ETF Global fund flows and NAV",
    "ETFG/CONST": "ETF Global constituents",
    "ORATS/OPT": "ORATS option volatility surfaces",
    "ORATS/VOL": "ORATS volatility metrics",
    "IFT/NSA": "News sentiment",
    "FXCM/H1": "FXCM hourly FX rates",
    # Free "QDL" tables (the surviving Quandl free feeds)
    "QDL/BCHAIN": "Bitcoin blockchain statistics",
    "QDL/BITFINEX": "Bitfinex crypto prices",
    "QDL/ML": "BofA Merrill Lynch corporate bond yields and indices",
    "QDL/ODA": "IMF World Economic Outlook",
    "QDL/OPEC": "OPEC reference basket oil price",
    "QDL/LME": "London Metal Exchange warehouse stocks",
    "QDL/FON": "CFTC commitments of traders, futures only",
    "QDL/JODI": "JODI oil statistics",
    "QDL/FRED": "FRED mirror",
    # Other free tables
    "ZILLOW/DATA": "Zillow home values and rents",
    "ZILLOW/INDICATORS": "Zillow indicator codes",
    "ZILLOW/REGIONS": "Zillow region codes",
    "WIKI/PRICES": "Wiki EOD stock prices (ended 2018-03-27)",
    "SCF/PRICES": "Stevens continuous futures (ended 2022-06)",
}

DATE_PREFERENCE = [
    "date", "tradedate", "pricedate", "datekey", "filingdate", "calendardate",
    "per_end_date", "reportdate", "ex_date", "exdate", "lastupdated",
]

session = requests.Session()


def get(path, **params):
    time.sleep(PAUSE)
    return session.get(f"{BASE}/{path}", params={"api_key": API_KEY, **params}, timeout=60)


def pick_date_column(filters, columns):
    """A date-like column we are allowed to filter on, else any date-like column."""
    for name in DATE_PREFERENCE:
        if name in filters:
            return name, True
    for name in filters:
        if "date" in name:
            return name, True
    for name in columns:
        if name == "date" or name.endswith("date"):
            return name, False
    return None, False


def probe(code):
    row = {"table": code, "description": TABLES[code]}

    r = get(f"{code}/metadata.json")
    if r.status_code == 404:
        return {**row, "status": 404, "verdict": "missing"}
    if r.status_code != 200:
        return {**row, "status": r.status_code, "verdict": f"error {r.status_code}"}
    meta = r.json()["datatable"]
    columns = [c["name"] for c in meta["columns"]]
    date_col, filterable = pick_date_column(meta["filters"], columns)
    pk0 = (meta["primary_key"] or columns)[0]  # a few tables declare no primary key
    row.update(
        name=meta["name"],
        premium=meta["premium"],
        vendor_refreshed=(meta.get("status") or {}).get("refreshed_at", "")[:10],
        date_column=date_col,
        entity_column=pk0,
    )

    # First page, unfiltered: how many rows, entities, and what date span?
    cols = [pk0] + ([date_col] if date_col and date_col != pk0 else [])
    r = get(f"{code}.json", **{"qopts.columns": ",".join(cols), "qopts.per_page": 10000})
    row["status"] = r.status_code
    if r.status_code == 403:
        return {**row, "verdict": "forbidden"}
    if r.status_code != 200:
        return {**row, "verdict": f"error {r.status_code}"}
    j = r.json()
    data = j["datatable"]["data"]
    row["rows_first_page"] = len(data)
    row["more_pages"] = j["meta"].get("next_cursor_id") is not None
    row["entities_first_page"] = len({x[0] for x in data})
    if date_col:
        di = cols.index(date_col)
        dates = sorted(str(x[di])[:10] for x in data if x[di] is not None)
        if dates:
            row["min_date_p1"], row["max_date_p1"] = dates[0], dates[-1]

    # Canary: the free samples are a fixed set of ~30 large caps (roughly the
    # Dow 30 plus TSLA and V). A liquid ticker outside that set returning
    # nothing is the clearest sample signal, and it works even when the
    # sample's dates run to today.
    canary = None
    ticker_col = next((c for c in ("ticker", "symbol") if c in meta["filters"]), None)
    canary_filter = CANARY_OVERRIDES.get(code) or ({ticker_col: CANARY_TICKER} if ticker_col else None)
    if canary_filter:
        r = get(f"{code}.json", **canary_filter, **{"qopts.per_page": 1})
        canary = r.status_code == 200 and bool(r.json()["datatable"]["data"])
        row["canary_rows"] = canary

    # Recency: any rows in the last RECENT_DAYS days?
    recent = None
    if date_col and filterable:
        cutoff = str(date.today() - timedelta(days=RECENT_DAYS))
        r = get(f"{code}.json", **{f"{date_col}.gte": cutoff, "qopts.per_page": 1})
        recent = r.status_code == 200 and bool(r.json()["datatable"]["data"])
        row["recent_rows"] = recent

    small_slice = bool(meta["premium"]) and not row["more_pages"] and row["entities_first_page"] <= SAMPLE_MAX_ENTITIES
    if canary is False or small_slice:
        row["verdict"] = "sample"
    elif recent is None:
        row["verdict"] = "unknown"
    elif recent:
        row["verdict"] = "current"
    else:
        row["verdict"] = "sample" if meta["premium"] else "stale"
    return row


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    results = []
    for i, code in enumerate(TABLES, 1):
        res = probe(code)
        results.append(res)
        print(f"[{i:>2}/{len(TABLES)}] {res['verdict']:9} {code:24} {res.get('max_date_p1', ''):10} {res['description']}")

    df = pd.DataFrame(results)
    order = ["current", "sample", "stale", "unknown", "forbidden", "missing"]
    df["verdict"] = pd.Categorical(df["verdict"], categories=order + sorted(set(df["verdict"]) - set(order)))
    df = df.sort_values(["verdict", "table"]).reset_index(drop=True)
    out = OUTPUT_DIR / "access_sweep.csv"
    df.to_csv(out, index=False)

    print("\n" + "=" * 72)
    print(f"Verdicts as of {date.today()} (RECENT_DAYS={RECENT_DAYS})")
    print("=" * 72)
    show = ["verdict", "table", "premium", "canary_rows", "recent_rows", "max_date_p1", "vendor_refreshed", "rows_first_page", "more_pages", "entities_first_page"]
    with pd.option_context("display.width", 200, "display.max_rows", 200):
        print(df[show].to_string(index=False))
    print(f"\nFull table written to {out}")
    print("\nHow to read this:")
    print("  current   Recent rows exist and the canary ticker is present: live data for the whole universe.")
    print(f"  sample    Your key sees a fixed slice of ~30 large caps (no {CANARY_TICKER}), sometimes with dates to today.")
    print("            That is what 'premium data with no subscription' looks like. It is NOT an error.")
    print("  forbidden The table has no preview at all; only subscribers get any rows.")
    print("If everything premium says 'sample', no subscription is linked to this key. Ask the person who")
    print("administers your institution's Nasdaq Data Link account to add you; the products then appear")
    print("under Account > Data Feeds on data.nasdaq.com, and this sweep flips them to 'current'.")


if __name__ == "__main__":
    main()
