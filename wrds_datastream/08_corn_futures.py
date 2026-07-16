"""
Case study: Corn futures (CBOT) from the LSEG Datastream futures library.

Applies the full workflow from scripts 01-06 to a single product:
    1. Find recent Corn contracts (contrcode = 3247) in wrds_contract_info
    2. Pull daily settlement prices from wrds_fut_contract
    3. Splice a front-month continuous series (roll on last trade date)
    4. Compute summary statistics and save a two-panel plot:
       price history + today's term structure

Corn contrcode found via 03_search_products.py (search "corn"):
3247 is CBOT Corn, with listed contracts out to Dec 2029. Prices are
in US cents per bushel; one contract covers 5,000 bushels.

Outputs (written to _output/ next to this script):
    corn_futures.png        - price history + term structure
    corn_futures_stats.txt  - summary statistics
    corn_front_month.csv    - the spliced front-month daily series

Usage:
    python 08_corn_futures.py
"""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import wrds

from decouple import Config, RepositoryEnv
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
config = Config(RepositoryEnv(repo_root / ".env"))
WRDS_USERNAME = config("WRDS_USERNAME")

OUTPUT_DIR = Path(__file__).resolve().parent / "_output"
OUTPUT_DIR.mkdir(exist_ok=True)

LIBRARY = "tr_ds_fut"
CORN_CONTRCODE = 3247  # CBOT Corn (see 03_search_products.py)
DATE_CUTOFF = "2024-01-01"

BLUE = "#2a78d6"
AQUA = "#1baf7a"

# ── Step 1: Find recent Corn contracts ───────────────────────────
print("=" * 60)
print("Connecting to WRDS")
print("=" * 60)
db = wrds.Connection(wrds_username=WRDS_USERNAME)

query = f"""
SELECT futcode, contrname, contrdate, lasttrddate
FROM {LIBRARY}.wrds_contract_info
WHERE contrcode = {CORN_CONTRCODE}
  AND lasttrddate >= '{DATE_CUTOFF}'
ORDER BY lasttrddate
"""
contracts = db.raw_sql(query)
contracts["lasttrddate"] = pd.to_datetime(contracts["lasttrddate"])
print(f"\nCorn contracts with last trade >= {DATE_CUTOFF}: {len(contracts)}")

# ── Step 2: Pull daily settlement prices ─────────────────────────
futcode_list = ",".join(str(int(f)) for f in contracts["futcode"])
query = f"""
SELECT futcode, date_, settlement, volume
FROM {LIBRARY}.wrds_fut_contract
WHERE futcode IN ({futcode_list})
  AND date_ >= '{DATE_CUTOFF}'
  AND settlement IS NOT NULL
ORDER BY date_
"""
prices = db.raw_sql(query)
db.close()

prices["date_"] = pd.to_datetime(prices["date_"])
prices = prices.merge(
    contracts[["futcode", "contrname", "contrdate", "lasttrddate"]], on="futcode"
)
latest_date = prices["date_"].max()
print(f"Price records: {len(prices)}")
print(f"Date range: {prices['date_'].min().date()} to {latest_date.date()}")

# ── Step 3: Splice a front-month continuous series ───────────────
# On each date, take the contract closest to expiry that is still
# trading (lasttrddate >= date). This is the standard "front month"
# series; it jumps at each roll, so use it for levels, not returns
# across rolls (a fully adjusted series would splice returns instead).
live = prices[prices["lasttrddate"] >= prices["date_"]]
front = (
    live.sort_values(["date_", "lasttrddate"])
    .groupby("date_")
    .first()
    .reset_index()
)

# ── Step 4: Summary statistics ───────────────────────────────────
front = front.sort_values("date_").set_index("date_")
returns = front["settlement"].pct_change().dropna()

latest = front.iloc[-1]
year_ago = front["settlement"].asof(latest_date - pd.DateOffset(years=1))
stats_lines = [
    "Corn futures (CBOT, contrcode 3247) - front-month series",
    f"Sample: {front.index.min().date()} to {front.index.max().date()}  ({len(front)} trading days)",
    "",
    f"Latest settlement ({front.index.max().date()}): {latest['settlement']:.2f} cents/bushel",
    f"  (contract {latest['contrname'].strip()}, expires {latest['lasttrddate'].date()})",
    f"1-year change:          {100 * (latest['settlement'] / year_ago - 1):+.1f}%",
    f"Sample min / max:       {front['settlement'].min():.2f} / {front['settlement'].max():.2f}",
    f"Daily return mean:      {100 * returns.mean():+.3f}%",
    f"Daily return std:       {100 * returns.std():.3f}%",
    f"Annualized volatility:  {100 * returns.std() * 252 ** 0.5:.1f}%",
    f"Worst / best day:       {100 * returns.min():+.1f}% / {100 * returns.max():+.1f}%",
    f"Median daily volume:    {front['volume'].median():,.0f} contracts",
]
stats_text = "\n".join(stats_lines)
print()
print(stats_text)

(OUTPUT_DIR / "corn_futures_stats.txt").write_text(stats_text + "\n")
front.to_csv(OUTPUT_DIR / "corn_front_month.csv")

# ── Step 5: Plot price history + term structure ──────────────────
term = (
    prices[prices["date_"] == latest_date]
    .sort_values("lasttrddate")
    .reset_index(drop=True)
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.25), width_ratios=[3, 2])

ax1.plot(front.index, front["settlement"], color=BLUE, linewidth=1.8)
ax1.annotate(
    f"{latest['settlement']:.0f}",
    xy=(front.index[-1], latest["settlement"]),
    xytext=(6, -3), textcoords="offset points", color=BLUE, fontweight="bold",
)
ax1.set_title("Front-month settlement price", loc="left", fontweight="bold")
ax1.set_ylabel("US cents per bushel")
ax1.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

ax2.plot(
    term["lasttrddate"], term["settlement"],
    color=AQUA, linewidth=1.8, marker="o", markersize=5,
)
ax2.set_title(f"Term structure on {latest_date.date()}", loc="left", fontweight="bold")
ax2.set_xlabel("Contract expiry")
ax2.xaxis.set_major_locator(mdates.YearLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

for ax in (ax1, ax2):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="0.9", linewidth=0.8)
    ax.set_axisbelow(True)
fig.suptitle(
    "Corn futures (CBOT) - LSEG Datastream via WRDS (tr_ds_fut)",
    x=0.01, ha="left", fontsize=13,
)
fig.tight_layout(rect=(0, 0, 1, 0.96))

plot_path = OUTPUT_DIR / "corn_futures.png"
fig.savefig(plot_path, dpi=150)
print(f"\nSaved: {plot_path}")
print(f"Saved: {OUTPUT_DIR / 'corn_futures_stats.txt'}")
print(f"Saved: {OUTPUT_DIR / 'corn_front_month.csv'}")
