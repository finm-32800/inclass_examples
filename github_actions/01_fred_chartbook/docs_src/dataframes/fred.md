
## Description

This dataframe contains US Gross Domestic Product from the Federal Reserve Economic Data (FRED) database. GDP is the most fundamental macroeconomic indicator used to assess the overall size and direction of the US economy. The data is re-pulled from FRED on every pipeline run.

## Data Dictionary

- **date**: `datetime64[ns]` Observation date (quarterly)
- **GDP**: `float64` US Nominal Gross Domestic Product (Billions of Dollars)
