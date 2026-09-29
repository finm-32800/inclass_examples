# 02 Tables API over HTTP

The Tables API called directly, first with `curl`, then with `requests`. Uses
`NDAQ/RTAT10` (Nasdaq's Retail Trading Activity Tracker, daily top 10), which
is free for every registered key and updated every trading day.

## What you'll learn

- The anatomy of a Tables-API URL: vendor, table, `.json` or `.csv`, filters,
  `qopts.*`
- Which columns accept filters (only the ones the metadata lists under `filters`)
- **Cursor pagination**: `meta.next_cursor_id` in, `qopts.cursor_id` out, until
  it comes back `null`
- **Bulk export**: `qopts.export=true` returns a pre-signed link to a zip, not rows
- Sending the key as the `X-Api-Token` header instead of a query parameter

## Setup

```bash
pip install -r requirements.txt
```

Make sure `NASDAQ_DATA_API_KEY` is set in the repo-root `.env` file. The bash
script sources that file if the variable is not already exported.

## Run

```bash
bash 01_curl_tables.sh
python 02_requests_pagination.py
```

The Python script fetches a year of TSLA and NVDA rows in pages of 200 (small
on purpose, so the cursor shows up), builds one DataFrame, then downloads the
whole table through the export endpoint into `output/NDAQ_RTAT10.zip`.

## Key points

- Filters go straight in the query string: `ticker=TSLA,NVDA&date.gte=2026-01-01`.
  `date.gte` works because `date` is in the table's `filters` list; `activity.gte`
  would be rejected with a 422.
- A page holds at most 10,000 rows. Any bigger result set needs the cursor
  loop or the export.
- The export link points at S3 and is already signed: fetch it **without** the
  API key, and within its expiry window (30 minutes).
- Dates arrive as strings. Converting them is your job; the SDK does it for you
  (see `03_python_sdk`).

## Try it

- Replace the table with `QDL/BITFINEX` (free) and filter
  `code=BTCUSD&date.gte=2026-01-01`
- Request `qopts.per_page=10001` and read the error
- Drop the `X-Api-Token` header and see the 403 an anonymous request gets
- Pull a year of Reliance Industries from the NSE: `EDI/ASAP.csv?mic=XNSE&year=2026&pricefilesymbol=EQRELIANCE&qopts.columns=pricedate,close,tradedvolume`
  (the `year` filter matters: the table is partitioned on it)
