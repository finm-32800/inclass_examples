# 03 Python SDK

The same query as `02_tables_api_http`, run side by side through raw HTTP and
through `nasdaqdatalink.get_table()`, then the SDK-only conveniences.

## What you'll learn

- How SDK keyword arguments map to the query string: a list becomes a comma
  list, `date={"gte": ...}` becomes `date.gte=...`, `qopts={"columns": [...]}`
  becomes `qopts.columns=...`
- What `paginate=True` does (follows `next_cursor_id` for you) and what the SDK
  adds on top of the wire format (`date` parsed to `datetime64`)
- `Datatable(...).data_fields()` for metadata and `export_table()` for bulk zips
- Why `nasdaqdatalink.get()` now raises: it wraps the retired time-series API

## Setup

```bash
pip install -r requirements.txt
```

Make sure `NASDAQ_DATA_API_KEY` is set in the repo-root `.env` file. The SDK
would also accept `NASDAQ_DATA_LINK_API_KEY` in the environment or a
`~/.nasdaq/data_link_apikey` file; the script sets `ApiConfig.api_key`
explicitly so the course-wide variable is the only one you need.

## Run

```bash
python 01_get_table_vs_http.py
```

## Key points

- `get_table()` returns a pandas DataFrame directly. Both methods return the
  same rows; the script asserts it.
- `paginate=True` stops after `ApiConfig.page_limit` pages and warns if more
  remain. For anything large, filter harder or use `export_table()`.
- `export_table()` accepts the same filters as `get_table()` plus
  `filename=`; it polls the export until the zip is ready, then downloads it.
- The SDK raises `DataLinkError` subclasses (`ForbiddenError`, `NotFoundError`,
  `LimitExceededError`, ...); the message carries the same text as the
  API's `quandl_error.message`.

## Try it

- Add `qopts={"columns": [...], "per_page": 100}` and watch the page count change
- Call `get_table("SHARADAR/SEP", ticker="AAPL", date={"gte": "2026-01-01"})` and
  confirm it returns an empty frame on a free-tier key (the sample ends in 2018)
- Call `get_table("EOD/PRICES", ticker="AAPL")` and catch the `ForbiddenError`
- Pull the 1-month constant-maturity ATM vol for E-mini S&P 500 options and
  plot it: `get_table("AR/IVM", exchange_code="CME", futures_code="ES",
  expiration="1M", date={"gte": "2020-01-01"}, qopts={"columns": ["date", "atm", "rr25"]}, paginate=True)`
