"""Turn the latest Treasury futures prices into a single standalone HTML page.

Runs entirely from the local parquet file — no API access needed.

Usage:
    python 02_make_page.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

OUTPUT_DIR = Path(__file__).resolve().parent / "_output"

df = pd.read_parquet(OUTPUT_DIR / "latest_prices.parquet")

as_of = pd.to_datetime(df["date"]).max().strftime("%Y-%m-%d")
generated_at = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M UTC")

labels = [f"{row.product} ({row.tenor})" for row in df.itertuples()]

fig = go.Figure(
    go.Bar(
        x=labels,
        y=df["close"],
        text=[f"{v:,.3f}" for v in df["close"]],
        textposition="outside",
        marker_color="#2a78d6",
        hovertemplate="%{x}<br>Settlement: %{y:,.4f}<extra></extra>",
    )
)
fig.update_layout(
    title=(
        "US Treasury Futures — Latest Prices"
        f"<br><sup>Front-month (volume-rolled) daily close as of {as_of}. "
        f"Source: Databento, CME Globex. Generated {generated_at}.</sup>"
    ),
    yaxis_title="Price (points)",
    template="plotly_white",
    showlegend=False,
)

out_path = OUTPUT_DIR / "index.html"
fig.write_html(out_path, include_plotlyjs="cdn")
print(f"Saved page to {out_path}")
