"""Create an interactive GDP chart and save it as a standalone HTML file.

The generation timestamp is stamped onto the chart so you can verify on the
published site that the scheduled GitHub Actions run actually refreshed it.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from pull_fred import load_fred
from settings import config

OUTPUT_DIR = Path(config("OUTPUT_DIR"))


def create_gdp_chart(df):
    """Build a single-series GDP line chart."""
    generated_at = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M UTC")
    fig = px.line(
        df,
        x="date",
        y="GDP",
        title=(
            "US Gross Domestic Product"
            f"<br><sup>Billions of dollars, quarterly. Source: FRED. "
            f"Last updated {generated_at}.</sup>"
        ),
        color_discrete_sequence=["#2a78d6"],
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Billions of dollars",
        showlegend=False,
        template="plotly_white",
    )
    return fig


if __name__ == "__main__":
    df = load_fred()
    fig = create_gdp_chart(df)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "gdp_chart.html"
    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"Saved chart to {out_path}")
