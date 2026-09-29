# 01 Check Access

Find out what your Nasdaq Data Link key can actually see. Run this before
anything else: it settles in a minute what the account pages on the website
do not tell you.

## What you'll learn

- The **entitlement model**: free tables, premium tables with a free sample, and
  premium tables with no sample at all
- Why a **HTTP 200 from a premium table does not mean you are subscribed**, and
  the two queries that do tell you (recent rows, and a ticker outside the
  ~30-name sample set)
- How to read a table's **metadata** (`premium`, `filters`, `primary_key`,
  `status.refreshed_at`) and the rate-limit response headers
- What the **retired time-series API** looks like from the outside (HTML 403,
  `410 Gone`), so you recognise it when an old tutorial sends you there

## Setup

```bash
pip install -r requirements.txt
```

Make sure `NASDAQ_DATA_API_KEY` is set in the repo-root `.env` file.

## Run

```bash
python 01_check_key.py       # six short checks, one table each
python 02_sweep_tables.py    # ~50 tables, writes output/access_sweep.csv
```

`01_check_key.py` confirms the key works, pulls last week's rows from a free
table, then shows the trap: `SHARADAR/SEP` answers 200 with 2,460 rows for 30
tickers, all from September to December 2018, zero rows for the last 180 days
and zero rows for `NFLX`, while the vendor's metadata says the table was
refreshed today.

`02_sweep_tables.py` repeats that test over a curated list of tables and prints
one verdict per table:

| Verdict | Meaning |
|---|---|
| `current` | rows in the last 180 days **and** rows for the canary ticker `NFLX`: full, live access (free table, or a subscription is attached) |
| `sample` | a fixed slice of ~30 large caps, whether its dates end in 2018 or run to today: the free preview only |
| `stale` | free table the vendor stopped updating |
| `unknown` | no filterable date column, so recency cannot be tested; look at the row counts |
| `forbidden` | HTTP 403: exists, has no preview, only subscribers get rows |
| `missing` | HTTP 404: no such table |

If every premium table says `sample`, no subscription is linked to your key.
Ask whoever administers your institution's Nasdaq Data Link account to attach
you to the licensed products; they then show up under *Data Feeds* in your
account and the sweep flips them to `current`. The two files in
[`reference/`](reference/) are this sweep run the day before and the day after
that happened for the course key: `NDAQ/USEDH`, `EDI/CUR` and the Zacks
Collection B tables went from `sample` (or absent) to `current`; Sharadar,
which is not on the licence, stayed `sample`.

## Key points

- There is **no endpoint that lists your entitlements**. The old
  `/api/v3/databases` listing is gone (`410`), so the sweep probes a hand-made
  list. Add table codes to `TABLES` as you discover them; unknown codes just
  report `missing`.
- The metadata endpoint is public for every table, including ones you cannot
  read. Its `premium` flag says whether a table is *sold*, not whether *you* have it.
- Recency alone is not enough: the Sharadar S&P 500, corporate-actions and
  events samples carry dates up to today for the same ~30 names. The canary
  ticker catches those. Pick a canary that is liquid, old enough to be in stale
  tables, and not in the sample set; `NFLX` fits.
- The verdicts are heuristics on two probes plus row counts; the CSV keeps
  every signal so you can judge edge cases yourself.

## Try it

- Change `RECENT_DAYS` to 30 and see which free tables become `stale`
- Change `CANARY_TICKER` to `AAPL` and watch every sample flip to `current`: that
  is the mistake the canary exists to prevent
- Add `SHARADAR/SF3B` and `ZACKS/EPS` to `TABLES` and check what comes back
- Once a subscription is attached to your key, re-run the sweep and diff the
  two `access_sweep.csv` files
