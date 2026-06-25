"""Moving-average crossover demo.

The *same* script ships in all four environment examples
(conda-only, conda+pip, uv, pixi). Only the way you install and run it
changes — the code and its third-party dependencies stay identical.

Dependencies: numpy, pandas, matplotlib.

Generates a deterministic random-walk price series, computes 20- and
50-day moving averages, flags the most recent golden/death cross, prints
a summary table, and saves a chart to `prices.png`.
"""

import matplotlib

matplotlib.use("Agg")  # no display needed; write straight to a file

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def simulate_prices(n_days: int = 250, seed: int = 32900) -> pd.DataFrame:
    """A reproducible geometric random walk, ~1 trading year of closes."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-01-01", periods=n_days)
    daily_returns = rng.normal(loc=0.0004, scale=0.012, size=n_days)
    close = 100.0 * np.exp(np.cumsum(daily_returns))
    return pd.DataFrame({"date": dates, "close": close}).set_index("date")


def add_signals(prices: pd.DataFrame) -> pd.DataFrame:
    out = prices.copy()
    out["ma_20"] = out["close"].rolling(20).mean()
    out["ma_50"] = out["close"].rolling(50).mean()
    out["spread"] = out["ma_20"] - out["ma_50"]
    out["regime"] = np.where(out["spread"] >= 0, "bullish", "bearish")
    return out


def find_last_cross(df: pd.DataFrame) -> str:
    sign = np.sign(df["spread"].dropna())
    flips = sign.ne(sign.shift()).fillna(False)
    crosses = sign[flips].iloc[1:]  # drop the first (no prior sign to cross)
    if crosses.empty:
        return "No crossover in the sample window."
    when = crosses.index[-1].date()
    kind = "golden cross (bullish)" if crosses.iloc[-1] > 0 else "death cross (bearish)"
    return f"Most recent signal: {kind} on {when}."


def main() -> None:
    prices = add_signals(simulate_prices())

    print("=" * 56)
    print("Moving-average crossover demo")
    print(f"  numpy      {np.__version__}")
    print(f"  pandas     {pd.__version__}")
    print(f"  matplotlib {matplotlib.__version__}")
    print("=" * 56)
    print(prices.tail(5).round(2).to_string())
    print()
    print(find_last_cross(prices))

    ax = prices[["close", "ma_20", "ma_50"]].plot(
        figsize=(10, 5), title="Synthetic price with 20/50-day moving averages"
    )
    ax.set_ylabel("price")
    ax.figure.tight_layout()
    ax.figure.savefig("prices.png", dpi=120)
    print("\nSaved chart to prices.png")


if __name__ == "__main__":
    main()
