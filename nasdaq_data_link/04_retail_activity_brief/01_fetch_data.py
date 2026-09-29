"""
Pull the full history of Nasdaq's Retail Trading Activity Tracker top-10 table.

NDAQ/RTAT10 is free for every registered key. For each trading day since
January 2016 it lists the ten tickers with the largest share of retail dollar
volume, with two fields (definitions from Nasdaq's product sheet):

    activity   dollars traded by retail investors in the ticker, divided by
               retail dollars traded across all tickers that day (0 to 1)
    sentiment  a score from -100 to +100 derived from retail net flows
               (buys minus sells) over the most recent 10 trading days;
               more positive means more net buying

About 27,000 rows. One SDK call with paginate=True fetches all of it.

Usage:
    python 01_fetch_data.py
"""

from pathlib import Path

import nasdaqdatalink
from decouple import Config, RepositoryEnv

# Load API key from repo-root .env
repo_root = Path(__file__).resolve().parents[2]
config = Config(RepositoryEnv(repo_root / ".env"))
nasdaqdatalink.ApiConfig.api_key = config("NASDAQ_DATA_API_KEY")

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

df = nasdaqdatalink.get_table("NDAQ/RTAT10", paginate=True)
df = df.sort_values(["date", "ticker"]).reset_index(drop=True)
df["sentiment"] = df["sentiment"].astype(int)  # pages concatenate as float; the field is an integer score

print(
    f"{len(df):,} rows, {df['date'].min().date()} .. {df['date'].max().date()}, "
    f"{df['date'].nunique():,} trading days, {df['ticker'].nunique()} distinct tickers"
)
print(df.tail(10).to_string(index=False))

out = OUTPUT_DIR / "rtat10.csv"
df.to_csv(out, index=False)
print("saved", out.relative_to(repo_root))
