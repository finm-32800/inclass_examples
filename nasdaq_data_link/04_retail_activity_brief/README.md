# 04 Retail Activity Brief

Build a short brief on retail trading activity from `NDAQ/RTAT10`, Nasdaq's
Retail Trading Activity Tracker (daily top 10). Two scripts: one pulls the full
history with the SDK, the other turns it into three charts and a summary table.

## The data

Nasdaq builds RTAT from public SIP data and estimates it covers about $30B a
day of retail order flow, roughly 45% of US retail volume, across 9,500+
stocks, ADRs and ETPs. The free table lists, for every trading day since
January 2016, the ten tickers with the largest share of that flow:

| Field | Definition (from Nasdaq's product sheet) |
|---|---|
| `activity` | dollars traded by retail investors in the ticker, divided by retail dollars traded across all tickers that day; 0 to 1 |
| `sentiment` | score from -100 to +100 derived from retail net flows (buys minus sells) over the most recent 10 trading days; more positive means more net buying |

The premium table `NDAQ/RTAT` has the same two fields for the full universe.

## What you'll learn

- Fetching a whole table with `get_table(..., paginate=True)`
- Working with a **top-N-per-day** panel: a ticker is only present on days it
  made the cut, so every average is conditional on being in the top 10
- Three chart forms picked by the data's job: trend over time (lines with direct
  end labels), ranked magnitude (horizontal bars, one hue), and above/below zero
  (columns with a blue/red pair around a zero baseline)

## Setup

```bash
pip install -r requirements.txt
```

Make sure `NASDAQ_DATA_API_KEY` is set in the repo-root `.env` file.

## Run

```bash
python 01_fetch_data.py     # output/rtat10.csv, about 27,000 rows
python 02_retail_brief.py   # output/*.png and output/summary.csv
```

| Output | Content |
|---|---|
| `01_activity_share.png` | Monthly mean retail dollar-volume share for TSLA, NVDA and AAPL |
| `02_days_in_top10.png` | The 15 tickers that appear most often in the daily top 10 |
| `03_tsla_sentiment.png` | TSLA retail sentiment, quarterly mean, above and below zero |
| `summary.csv` | The 10 most frequent tickers: days present, share of days, mean activity and sentiment |

## Key points

- Gaps in the line chart are real: a month with no top-10 day for that ticker
  has no observation. Do not fill them.
- Colors do one job each: three fixed categorical hues for the three named
  series, a single blue for the ranking, and a blue/red pair for the sign of
  sentiment. The palette was checked for colour-vision-deficiency separation
  and contrast before use.
- The bar helper draws bars 22px thick with a 4px rounded data end; it needs the
  axes limits and figure layout to be final before it is called, which is why
  the script calls `fig.canvas.draw()` first.

## Try it

- Swap `TSLA` for `GME` in the sentiment chart and look at early 2021
- Compute, per year, how many distinct tickers made the top 10 at least once
- If a subscription to `NDAQ/RTAT` is ever attached to the key, change one
  string in `01_fetch_data.py` and rerun for the full universe
