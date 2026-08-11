# Dataframe: `finm-32900/01_fred_chartbook:fred` - FRED GDP


## Description

This dataframe contains US Gross Domestic Product from the Federal Reserve Economic Data (FRED) database. GDP is the most fundamental macroeconomic indicator used to assess the overall size and direction of the US economy. The data is re-pulled from FRED on every pipeline run.

## Data Dictionary

- **date**: `datetime64[ns]` Observation date (quarterly)
- **GDP**: `float64` US Nominal Gross Domestic Product (Billions of Dollars)



## DataFrame Glimpse

```
Rows: 318
Columns: 2
$ date <datetime[μs]> 2026-04-01 00:00:00
$ GDP           <f64> 32475.21


```

## Dataframe Manifest

| Dataframe Name                 | FRED GDP                                                          |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [fred](../dataframes/finm-32900--01_fred_chartbook/fred.md)                                       |
| Sources                        | FRED                                          |
| Providers                      | Federal Reserve Bank of St. Louis                                        |
| Provider Links                 | https://fred.stlouisfed.org/                                   |
| Tags                           | Macroeconomic, Gdp                                             |
| Access Types                   |                                       |
| How is data pulled?            | Web API via Python                                                   |
| Data available up to (min)     | 2026-04-01 00:00:00                                                             |
| Data available up to (max)     | 2026-04-01 00:00:00                                                             |
| Dataframe Path                 | /home/runner/work/inclass_examples/inclass_examples/github_actions/01_fred_chartbook/_data/fred.parquet                                             |


**Linked Charts:**


- [finm-32900/01_fred_chartbook:gdp](../../charts/finm-32900--01_fred_chartbook.gdp.md)



## Pipeline Manifest

| Pipeline Name                   | FRED Chartbook: US GDP                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [finm-32900/01_fred_chartbook](../../../index.md)              |
| Maintainer                      | Jeremy Bejarano               |
| Contributors                    |  |
| Repository                     |                   |
| Pipeline Web Page               | <a href="file:///home/runner/work/inclass_examples/inclass_examples/github_actions/01_fred_chartbook/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-08-11 05:19:50           |
| OS Compatibility                |  |
| Linked Dataframes               |  [finm-32900/01_fred_chartbook:fred](../../dataframes/finm-32900--01_fred_chartbook/fred.md)<br>  |


