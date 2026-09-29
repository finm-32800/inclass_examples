# Nasdaq Data Link: Tables API, entitlements, SDK vs HTTP

This directory teaches how to pull data from [Nasdaq Data Link](https://data.nasdaq.com/)
(formerly Quandl) and, before that, how to find out **what your key is actually
entitled to**. Nothing on the website tells you; the API does, if you ask it the
right question.

Like the [`databento/`](../databento/) examples, each query is shown both through
the **Python SDK** (`nasdaq-data-link`) and as the **raw HTTP call** underneath,
so you can see what the SDK abstracts away.

## Two APIs, one of them dead

Nasdaq Data Link has two data structures and two REST APIs:

| | URL | Status (Sept 2026) |
|---|---|---|
| **Time-series** ("datasets") | `/api/v3/datasets/VENDOR/CODE` | **Retired.** Every call returns an HTML 403 from the bot-protection layer; the database listing `/api/v3/databases` returns `410 Gone`. The SDK's `nasdaqdatalink.get()` wraps this API and now raises a 403 `DataLinkError`. |
| **Tables** ("datatables") | `/api/v3/datatables/VENDOR/TABLE` | Works. Everything here uses it. |

Most tutorials on the web (and the SDK README) still lead with `get("WIKI/AAPL")`
style time-series calls. They will not work. Use `get_table()`.

The old documentation site, `docs.data.nasdaq.com`, now redirects to a page that
404s. The surviving references are the SDK's own guides on GitHub:
[FOR_ANALYSTS.md](https://github.com/Nasdaq/data-link-python/blob/main/FOR_ANALYSTS.md)
and [FOR_DEVELOPERS.md](https://github.com/Nasdaq/data-link-python/blob/main/FOR_DEVELOPERS.md).

## What our key can see

Checked with `01_check_access/02_sweep_tables.py` twice: on 2026-09-22 with a
bare registered key, and on 2026-09-23 after the University of Chicago
licence was attached to the account. Both result files are kept in
[`01_check_access/reference/`](01_check_access/reference/); diff them to see
exactly what a licence changes. The account page *Data access via your
organization* now lists five products: Asian End of Day Pricing, Foreign
Exchange Rates, Futures Options, North American Fundamentals Collection B, and
U.S. Equity Daily History.

- **Licensed, full universe, live**
  - `NDAQ/USEDH`, U.S. Equity Daily History: unadjusted daily OHLCV plus FIGIs
    for every US-listed symbol (10,000+ per day, all exchanges), history back
    to 2002 for long-lived names, updated through the previous trading day.
    Filter on `symbol` (not `ticker`), `date`, `composite_figi`,
    `share_class_figi`.
  - `EDI/CUR`, Foreign Exchange Rates: 188 currency codes quoted against USD,
    daily since 2000, updated today. Filter on `code` and `date`.
  - Zacks "North American Fundamentals Collection B": `ZACKS/FC` (condensed
    fundamentals), `ZACKS/FR` (ratios), `ZACKS/MKTV` (market value),
    `ZACKS/SHRS` (shares outstanding), `ZACKS/HDM` (dividends), `ZACKS/MT`
    (master table). Full universe, fiscal periods through mid-2026.
  - `QUOTEMEDIA/PRICES` and `QUOTEMEDIA/DAILYPRICES` also opened up, but the
    vendor stopped updating them on 2025-06-03. Use `NDAQ/USEDH` instead.
  - Asian End of Day Pricing: `EDI/ASAP` (adjusted daily OHLCV, bid/ask,
    volume and value for every equity on NSE and BSE India, Shanghai,
    Shenzhen, Beijing, Singapore, Osaka and Nagoya) and `EDI/ASAF` (the
    adjustment factors behind it, one row per corporate action). Thousands of
    symbols per exchange per day, from 2005 (Singapore) or 2006 (India, China). Hong Kong and Tokyo are listed in the docs but
    return nothing: they need a separate exchange licence. The pricing table is
    partitioned by `year`, so always pass `year=` with your filters.
  - Futures Options (publisher Applied Research, the OptionWorks feed):
    `AR/IVM` (per contract and expiry: futures price, ATM implied vol, 25- and
    10-delta risk reversals and butterflies, and six skew-polynomial betas)
    and `AR/IVS` (the same keys with the implied vol at every 5 deltas from
    1-delta puts to 1-delta calls). 58 exchange/contract pairs on CME, CBOT,
    NYMEX, COMEX, ICE and Euronext, daily from January 2007 for the big
    contracts (ES, Treasuries) and later for others, plus
    constant-maturity rows (`expiration` of `1W`, `1M`, `2M`, `3M`, `6M`,
    `9M`, `1Y`) next to the listed expiries.
- **Free tables, full history**: `NDAQ/RTAT10` (retail trading activity, top
  10, updated daily), `SHARADAR/TICKERS` (securities master), `QDL/BCHAIN` and
  `QDL/BITFINEX` (crypto, to June 2026), `QDL/ODA` (IMF WEO), `QDL/ML` (BofA
  corporate bond yields, to Feb 2025), `ZILLOW/*` (to mid 2025). Some free
  tables are no longer updated: `WIKI/PRICES` ends 2018, `SCF/PRICES` ends
  2022, `QDL/OPEC` ends Jan 2024.
- **Premium tables, sample only** (not on the licence): everything from
  Sharadar except `TICKERS` (prices, fundamentals, insiders, corporate actions,
  events, S&P 500 constituents), the Zacks estimates and surprises tables
  (`ZACKS/EE`, `ES`, `EA`, `SS`, `CP`), ORATS, Mergent, ETF Global, and the
  full-universe `NDAQ/RTAT`. These answer HTTP 200 with the *same ~30 large
  caps* (roughly the Dow 30 plus TSLA and V). For most tables the sample window
  ended in 2017 or 2018; for a few (`SHARADAR/SP500`, `SHARADAR/ACTIONS`,
  `SHARADAR/EVENTS`, `SHARADAR/METRICS`) it runs to today. That is the free
  preview every registered account gets, even though the vendor's metadata
  shows the table refreshed today.
- **Premium tables, no preview**: `EOD/PRICES`, `SHARADAR/SF3` (13F holdings),
  `ETFG/CONST`, `QDL/FRED`. These return 403.

**The trap:** a 200 from a premium table looks like access. It is not. Two
queries settle it: ask for rows from the last few months, and ask for a liquid
ticker outside the sample set (the scripts use `NFLX`). A subscription passes
both; a sample fails at least one. `01_check_access/` turns that into a script.

**How a licence shows up:** premium products are licensed to the institution
and attached to individual accounts by whoever administers the institution's
Nasdaq Data Link account. Before that happened, the account's *Data Feeds* page
was empty and every premium table served the sample. The day after, the
licensed tables flipped from `sample` to `current` in the sweep with no change
to the key or the code. Nothing on the API side announces the change; you have
to ask.

## Setup

1. Install the Python package:
   ```bash
   pip install nasdaq-data-link python-decouple pandas requests matplotlib
   ```

2. Set your API key in the repo-root `.env` file (the variable is already in
   `.env.example`):
   ```
   NASDAQ_DATA_API_KEY=xxxxxxxxxxxxxxxxxxxx
   ```
   Your key is on <https://data.nasdaq.com/account/profile>. The SDK's own
   environment variable is `NASDAQ_DATA_LINK_API_KEY`; these examples keep the
   course-wide name and pass the key explicitly with
   `nasdaqdatalink.ApiConfig.api_key = ...`.

3. The bash script reads the same `.env` if `NASDAQ_DATA_API_KEY` is not already
   exported in your shell.

## Examples

| Directory | Topic | Protocol |
|-----------|-------|----------|
| `01_check_access` | What can this key see? Sample vs subscription, retired API | HTTP REST |
| `02_tables_api_http` | Tables API anatomy: filters, columns, cursor pagination, CSV, bulk export | curl + `requests` |
| `03_python_sdk` | Same query with `get_table()`; SDK extras; what `get()` does now | SDK vs HTTP |
| `04_retail_activity_brief` | Retail trading activity brief: 3 charts + summary table from a free table | SDK |

Work through them in order. Every example uses a free table so it runs on any
registered key; when a subscription is attached, swap in the premium table of
your choice.

## Licensed tables: quick reference

| Table | Filterable columns | Example |
|---|---|---|
| `NDAQ/USEDH` | `symbol`, `date`, `composite_figi`, `share_class_figi` | `symbol=NVDA&date.gte=2026-01-01` |
| `EDI/CUR` | `code`, `date` | `code=EUR,JPY,GBP&date.gte=2026-01-01` (rate = units per USD) |
| `ZACKS/FC`, `ZACKS/FR` | `ticker`, `per_end_date`, `per_type` | `ticker=NVDA&per_type=Q&per_end_date.gte=2024-01-01` |
| `ZACKS/MKTV`, `ZACKS/SHRS` | `ticker`, `per_end_date`, `per_type` | `ticker=NVDA&per_type=Q` |
| `ZACKS/HDM` | `m_ticker`, `ex_date`, `action_type` | `ex_date.gte=2026-09-01` |
| `ZACKS/MT` | `ticker`, `m_ticker`, ... | `ticker=NVDA` |
| `EDI/ASAP` | `mic`, `pricefilesymbol`, `exchgcd`, `pricedate`, `year` | `mic=XNSE&year=2026&pricefilesymbol=EQRELIANCE` |
| `EDI/ASAF` | `market`, `symbol`, `sectycd`, `exdate` | `market=XNSE&exdate.gte=2026-09-01` |
| `AR/IVM`, `AR/IVS` | `exchange_code`, `futures_code`, `option_code`, `expiration`, `date` | `exchange_code=CME&futures_code=ES&expiration=1M&date.gte=2026-01-01` |

Every row of `AR/IVM` carries the whole skew: implied vol at moneyness `x =
ln(strike / futures)` is `atm + beta1*x + ... + beta6*x^6`, valid between
`min_money` and `max_money`.

## Tables API cheat sheet

```
https://data.nasdaq.com/api/v3/datatables/VENDOR/TABLE.json      rows (JSON)
https://data.nasdaq.com/api/v3/datatables/VENDOR/TABLE.csv       rows (CSV)
https://data.nasdaq.com/api/v3/datatables/VENDOR/TABLE/metadata.json
```

| Parameter | Meaning |
|---|---|
| `api_key=KEY` (query) or `X-Api-Token: KEY` (header) | Authentication. Prefer the header; it keeps the key out of URLs, logs and screenshots. |
| `ticker=AAPL` / `ticker=AAPL,MSFT` | Equality filter, comma list for several values. Only columns listed under `filters` in the metadata accept filters. |
| `date.gte=2026-01-01`, `.gt`, `.lte`, `.lt` | Range filters on a filterable column. |
| `qopts.columns=date,ticker,close` | Return only these columns. |
| `qopts.per_page=10000` | Page size; 10,000 is the maximum. |
| `qopts.cursor_id=...` | Next page. Each response carries `meta.next_cursor_id`; `null` means last page. |
| `qopts.export=true` | Instead of rows, return a pre-signed link to a zip of the whole (filtered) table. Poll until `status` is `fresh`. |

Rate limits documented for the REST API: 300 calls per 10 seconds, 2,000 per 10
minutes and 50,000 per day for a registered key, more for premium subscribers,
and the table exporter at most 10 times per hour. The `X-RateLimit-Limit` and
`X-RateLimit-Remaining` response headers report the limit that applies to you.

## SDK vs HTTP

| | SDK (`nasdaq-data-link`) | Raw HTTP |
|---|---|---|
| **Auth** | `ApiConfig.api_key`, env var, or `~/.nasdaq/data_link_apikey` | `api_key` query param or `X-Api-Token` header |
| **Filters** | keyword args: `ticker=["A","B"]`, `date={"gte": "..."}` | `ticker=A,B&date.gte=...` |
| **Pagination** | `paginate=True` follows cursors for you | loop on `meta.next_cursor_id` |
| **Types** | `date` parsed to `datetime64` | everything is JSON: dates are strings |
| **Bulk export** | `export_table()` polls and downloads the zip | `qopts.export=true`, poll, download the link |
| **Errors** | `DataLinkError` subclasses | HTTP status codes plus `quandl_error.message` |
