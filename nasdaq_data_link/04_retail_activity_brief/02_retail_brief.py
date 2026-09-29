"""
Retail activity brief from NDAQ/RTAT10: three charts and a summary table.

    output/01_activity_share.png   monthly mean retail dollar-volume share: TSLA, NVDA, AAPL
    output/02_days_in_top10.png    the 15 tickers that appear most often in the daily top 10
    output/03_tsla_sentiment.png   TSLA retail sentiment, quarterly mean, above/below zero
    output/summary.csv             the 10 most frequent tickers and their averages

Run 01_fetch_data.py first.

Usage:
    python 02_retail_brief.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DATA = OUTPUT_DIR / "rtat10.csv"
if not DATA.exists():
    raise SystemExit("output/rtat10.csv not found: run 01_fetch_data.py first")

# ── Palette ──────────────────────────────────────────────────────────
# Categorical slots in fixed order (never re-assigned when a series is dropped),
# one sequential hue for magnitude, a blue/red pair for above/below zero.
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"TSLA": "#2a78d6", "NVDA": "#eb6834", "AAPL": "#1baf7a"}
SEQUENTIAL = "#2a78d6"
DIVERGING = {"up": "#2a78d6", "down": "#e34948"}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "figure.dpi": 150,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
})


def style(ax, grid_axis):
    """Recessive chrome: no box, hairline solid gridlines on one axis, no tick marks."""
    for side in ("top", "right", "left" if grid_axis == "y" else "bottom"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def headline(fig, text, subtitle):
    fig.text(0.06, 0.95, text, fontsize=13, fontweight="semibold", color=INK, va="top")
    fig.text(0.06, 0.895, subtitle, fontsize=9.5, color=INK2, va="top")


def data_per_px(ax):
    inv = ax.transData.inverted()
    (x0, y0), (x1, y1) = inv.transform([(0, 0), (1, 1)])
    return abs(x1 - x0), abs(y1 - y0)


def rounded_bar(ax, pos, value, color, orient="h", thickness_px=22, radius_px=4):
    """A bar from the baseline (0) to `value`, 4px-rounded at the data end, square at the baseline.

    Call only after the axes limits and the figure layout are final: the
    rounding is computed in pixels from the current data-to-pixel transform.
    """
    xpp, ypp = data_per_px(ax)
    rx, ry = radius_px * xpp, radius_px * ypp
    aspect = ypp / xpp  # makes the rounding circular on screen
    if orient == "h":
        t = min(0.72, thickness_px * ypp)
        x0, w = (0, value) if value >= 0 else (value, -value)
        if w < 2 * rx:
            ax.add_patch(Rectangle((x0, pos - t / 2), w, t, fc=color, ec="none"))
            return
        ax.add_patch(FancyBboxPatch((x0, pos - t / 2), w, t, boxstyle=f"round,pad=0,rounding_size={rx}",
                                    mutation_aspect=aspect, fc=color, ec="none"))
        square_x = 0 if value >= 0 else value + rx
        ax.add_patch(Rectangle((square_x, pos - t / 2), w - rx, t, fc=color, ec="none"))
    else:
        t = min(0.72, thickness_px * xpp)
        y0, h = (0, value) if value >= 0 else (value, -value)
        if h < 2 * ry:
            ax.add_patch(Rectangle((pos - t / 2, y0), t, h, fc=color, ec="none"))
            return
        ax.add_patch(FancyBboxPatch((pos - t / 2, y0), t, h, boxstyle=f"round,pad=0,rounding_size={rx}",
                                    mutation_aspect=aspect, fc=color, ec="none"))
        square_y = 0 if value >= 0 else value + ry
        ax.add_patch(Rectangle((pos - t / 2, square_y), t, h - ry, fc=color, ec="none"))


df = pd.read_csv(DATA, parse_dates=["date"])
first, last = df["date"].min().date(), df["date"].max().date()
n_days = df["date"].nunique()

# ── Chart 1: retail share over time, three series ────────────────────
monthly = (
    df[df["ticker"].isin(SERIES)]
    .assign(month=lambda d: d["date"].dt.to_period("M").dt.to_timestamp())
    .pivot_table(index="month", columns="ticker", values="activity", aggfunc="mean")
)
fig, ax = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(left=0.06, right=0.94, top=0.8, bottom=0.1)
headline(fig, "Retail dollar-volume share, monthly average",
         f"Share of all retail dollar volume on days the ticker was in the daily top 10, {first} to {last}. Gaps: months with no top-10 day.")
ends = []
for tk, color in SERIES.items():
    s = monthly[tk]
    ax.plot(s.index, s.values, color=color, lw=2, solid_capstyle="round", solid_joinstyle="round", label=tk)
    tail = s.dropna().iloc[-1:]
    ax.plot(tail.index, tail.values, "o", ms=8, mfc=color, mec=SURFACE, mew=2, zorder=5)
    ends.append([tk, tail.index[0], float(tail.values[0])])
ax.set_xlim(monthly.index.min(), monthly.index.max() + pd.DateOffset(months=5))
ax.set_ylim(0, monthly.max().max() * 1.12)
ax.yaxis.set_major_locator(MultipleLocator(0.05))
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
style(ax, "y")
# direct end labels in ink, nudged apart if they would collide
ends.sort(key=lambda e: e[2])
min_gap = ax.get_ylim()[1] * 0.06
for i in range(1, len(ends)):
    if ends[i][2] - ends[i - 1][2] < min_gap:
        ends[i][2] = ends[i - 1][2] + min_gap
for tk, x, y in ends:
    ax.annotate(tk, (x, y), xytext=(10, 0), textcoords="offset points", va="center", color=INK2, fontsize=9.5)
ax.legend(frameon=False, loc="upper left", ncol=3, handlelength=1.6, labelcolor=INK2)
fig.savefig(OUTPUT_DIR / "01_activity_share.png")
plt.close(fig)

# ── Chart 2: who is in the top 10 most often ─────────────────────────
counts = df["ticker"].value_counts().head(15).sort_values()
fig, ax = plt.subplots(figsize=(8, 6.4))
fig.subplots_adjust(left=0.12, right=0.95, top=0.83, bottom=0.08)
headline(fig, "Most frequent tickers in the retail top 10",
         f"Trading days in the daily top 10 by retail dollar volume, {first} to {last} ({n_days:,} days)")
ax.set_xlim(0, counts.max() * 1.1)
ax.set_ylim(-0.6, len(counts) - 0.4)
ax.set_yticks(range(len(counts)))
ax.set_yticklabels(counts.index, color=INK2)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
style(ax, "x")
fig.canvas.draw()  # layout is final: pixel-based rounding is now exact
for i, n in enumerate(counts.values):
    rounded_bar(ax, i, n, SEQUENTIAL, "h")
for i in range(len(counts) - 3, len(counts)):  # label the top three only
    ax.text(counts.iloc[i] + counts.max() * 0.012, i, f"{counts.iloc[i]:,}", va="center", color=INK2, fontsize=9)
fig.savefig(OUTPUT_DIR / "02_days_in_top10.png")
plt.close(fig)

# ── Chart 3: TSLA sentiment above / below zero ───────────────────────
tsla = df.loc[df["ticker"] == "TSLA"].set_index("date")["sentiment"]
quarterly = tsla.resample("QE").mean()
fig, ax = plt.subplots(figsize=(10, 4.6))
fig.subplots_adjust(left=0.06, right=0.97, top=0.78, bottom=0.12)
headline(fig, "TSLA retail sentiment, quarterly mean",
         "Daily score from -100 to +100 built from retail net flows (buys minus sells) over the prior 10 trading days")
lim = max(abs(quarterly.min()), abs(quarterly.max())) * 1.2
ax.set_xlim(-0.7, len(quarterly) - 0.3)
ax.set_ylim(-lim, lim)
ax.axhline(0, color=AXIS, lw=1)
years = [i for i, ts in enumerate(quarterly.index) if ts.quarter == 1]
ax.set_xticks(years)
ax.set_xticklabels([quarterly.index[i].year for i in years])
style(ax, "y")
fig.canvas.draw()
for i, v in enumerate(quarterly.values):
    rounded_bar(ax, i, v, DIVERGING["up"] if v >= 0 else DIVERGING["down"], "v")
ax.legend(handles=[Patch(color=DIVERGING["up"], label="net buying"), Patch(color=DIVERGING["down"], label="net selling")],
          frameon=False, loc="upper left", ncol=2, labelcolor=INK2)
fig.savefig(OUTPUT_DIR / "03_tsla_sentiment.png")
plt.close(fig)

# ── Summary table ────────────────────────────────────────────────────
top = df["ticker"].value_counts().head(10).index
summary = (
    df[df["ticker"].isin(top)]
    .groupby("ticker")
    .agg(days_in_top10=("date", "count"), mean_activity=("activity", "mean"),
         mean_sentiment=("sentiment", "mean"), first_day=("date", "min"), last_day=("date", "max"))
    .loc[top]
)
summary.insert(1, "share_of_days", summary["days_in_top10"] / n_days)
summary.to_csv(OUTPUT_DIR / "summary.csv")
print(f"RTAT10: {len(df):,} rows, {n_days:,} trading days, {first} to {last}\n")
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 120):
    print(summary.assign(first_day=summary.first_day.dt.date, last_day=summary.last_day.dt.date))
print("\nwrote", ", ".join(p.name for p in sorted(OUTPUT_DIR.iterdir()) if p.suffix in (".png", ".csv")))
