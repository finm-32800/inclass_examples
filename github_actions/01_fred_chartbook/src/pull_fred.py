"""Pull US GDP from FRED (Federal Reserve Economic Data).

FRED data via pandas-datareader needs no API key, which is why this
subexample can run on GitHub Actions with no secrets at all (contrast
with `../02_databento_secret/`).
"""

from pathlib import Path

import pandas as pd
import pandas_datareader.data as web
from settings import config

DATA_DIR = Path(config("DATA_DIR"))
START_DATE = config("START_DATE")
END_DATE = config("END_DATE")


# Define the series to pull from FRED
series_to_pull = {
    "GDP": "Gross Domestic Product",
}


def pull_fred(start_date=START_DATE, end_date=END_DATE):
    """
    Pull economic data from FRED.

    Lookup series code, e.g., like this:
    https://fred.stlouisfed.org/series/GDP

    Parameters
    ----------
    start_date : str or datetime
        Start date for the data pull
    end_date : str or datetime
        End date for the data pull

    Returns
    -------
    pd.DataFrame
        DataFrame with a `date` column and one column per FRED series
    """
    df = web.DataReader(list(series_to_pull.keys()), "fred", start_date, end_date)
    # Store the date as a regular column named "date" so that downstream
    # tools (like chartbook's `date_col` setting) can find it.
    df = df.rename_axis("date").reset_index()
    return df


def load_fred(data_dir=DATA_DIR):
    """
    Load previously saved FRED data from parquet file.

    Must first run this module as main to pull and save data.

    Parameters
    ----------
    data_dir : Path
        Directory containing the fred.parquet file

    Returns
    -------
    pd.DataFrame
        DataFrame with FRED time series data
    """
    file_path = Path(data_dir) / "fred.parquet"
    df = pd.read_parquet(file_path)
    return df


if __name__ == "__main__":
    df = pull_fred(START_DATE, END_DATE)
    filedir = Path(DATA_DIR)
    filedir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(filedir / "fred.parquet")
    df.to_csv(filedir / "fred.csv", index=False)
    print(f"Saved FRED data to {filedir}")
    print(f"Series: {list(series_to_pull.keys())}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
