# 07 Treasury Futures Market Brief

Build a market brief for Treasury futures across the yield curve. Combines two Databento queries (daily OHLCV + open interest statistics) into 4 charts and a summary table.

## What you'll learn

- How to use **continuous contracts** (`ZN.c.0`) for clean daily price series
- How to use **parent symbology** (`ZN.FUT`) with the **statistics schema** to get open interest
- How to filter statistics records by `stat_type` and aggregate across expirations
- How to combine multiple data schemas into a single analytical output
- Matplotlib charting patterns for financial data

## Products

| Symbol | Product | Tenor |
|--------|---------|-------|
| ZT | 2-Year T-Note | 2Y |
| ZF | 5-Year T-Note | 5Y |
| ZN | 10-Year T-Note | 10Y |
| TN | Ultra 10-Year T-Note | Ultra 10Y |
| ZB | 30-Year T-Bond | 30Y |

## Setup

```bash
pip install -r requirements.txt
```

Make sure `DATABENTO_API_KEY` is set in the repo-root `.env` file.

## Run

**Step 1 — Fetch data** (makes API calls, saves Parquet files to `output/`):
```bash
python 01_fetch_data.py
```

**Step 2 — Generate the brief** (reads local files, produces charts):
```bash
python 02_market_brief.py
```

## Output

After running both scripts, the `output/` directory contains:

| File | Description |
|------|-------------|
| `ohlcv_daily.parquet` | Daily OHLCV bars for all 5 products |
| `open_interest.parquet` | Aggregated open interest by product and date |
| `chart_indexed_prices.png` | Price performance normalized to 100 |
| `chart_curve_spreads.png` | 10s-2s and 30s-5s raw price spreads |
| `chart_volume_oi.png` | Average volume vs latest open interest |
| `chart_rolling_vol.png` | 20-day rolling annualized volatility |

The market snapshot table is printed to the console.

## Key concepts

- **Continuous vs parent symbology:** `ZN.c.0` gives you the front-month contract (auto-rolling), while `ZN.FUT` gives you all active expirations. Use continuous for price series, parent for aggregate statistics like total open interest.
- **OHLCV vs statistics schemas:** OHLCV gives price bars; statistics provides exchange-published figures like open interest, settlement prices, and volume summaries.
- **stat_type filtering:** The statistics schema returns many stat types. Open interest is `stat_type == 9`. Always filter to the type you need.

## Try it

- Add `UB.c.0` (Ultra T-Bond) as a 6th product
- Switch from `ohlcv-1d` to `ohlcv-1h` for intraday analysis
- Compute DV01-weighted spreads instead of raw price spreads
- Add a chart showing the term structure of open interest across expirations
