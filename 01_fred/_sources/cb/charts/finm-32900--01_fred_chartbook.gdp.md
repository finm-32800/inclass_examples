---
date: "2026-08-11 05:19:50"
tags: "FRED"
category: "Macroeconomic, Gdp"
---

# Chart: US GDP Over Time
Interactive line chart of US GDP, refreshed daily.

## Chart
```{raw} html
<iframe src="../../_static/finm-32900--01_fred_chartbook/gdp.html" height="500px" width="100%"></iframe>

<p style="text-align: center;">Sources: FRED</p>
```
[Full Screen Chart](../download_chart/finm-32900--01_fred_chartbook/gdp.html)





**Description:** This chart plots US Gross Domestic Product (GDP) over time. GDP is the total monetary value of all goods and services produced within a country's borders in a specific time period and is a broad measure of overall economic activity.

**Relevance for Economic Analysis:** GDP is the primary indicator used to gauge the health of a country's economy. It represents the size and growth rate of the economy.

**Direction of Risk:** Declining GDP indicates economic contraction, which may signal recession risk. Sustained GDP growth indicates a healthy, expanding economy.

**Formulas Used:** N/A

**Data Cleaning Information:** Data is sourced directly from FRED without additional transformations.

**What does this add that other charts might not?** The chart is regenerated every day by a scheduled GitHub Actions workflow, so it always reflects the latest FRED data without anyone re-running the pipeline by hand.



## Chart Specs

| Chart Name             | US GDP Over Time                                                   |
|------------------------|------------------------------------------------------------|
| Chart ID               | gdp                                               |
| Tags                   | Macroeconomic, Gdp                                      |
| Data Series Start Date |                                              |
| Data Frequency         | Quarterly                                              |
| Observation Period     |                                      |
| Lag in Data Release    |                                             |
| Data Release Timing    |                                          |
| Seasonal Adjustment    |                                     |
| Units                  | Billions of Dollars                                                  |
| HTML Chart             | [HTML](../download_chart/finm-32900--01_fred_chartbook/gdp.html)    |


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
| Data available up to (min)     |                                                              |
| Data available up to (max)     |                                                              |
| Dataframe Path                 | /home/runner/work/inclass_examples/inclass_examples/github_actions/01_fred_chartbook/_data/fred.parquet                                             |


**Linked Charts:**


- [finm-32900/01_fred_chartbook:gdp](../../charts/finm-32900--01_fred_chartbook.gdp.md)



## Pipeline Manifest

| Pipeline Name                   | FRED Chartbook: US GDP                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [finm-32900/01_fred_chartbook](../../index.md)              |
| Maintainer                      | Jeremy Bejarano               |
| Contributors                    |  |
| Repository                     |                   |
| Pipeline Web Page               | <a href="file:///home/runner/work/inclass_examples/inclass_examples/github_actions/01_fred_chartbook/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-08-11 05:19:50           |
| OS Compatibility                |  |
| Linked Dataframes               |  [finm-32900/01_fred_chartbook:fred](../dataframes/finm-32900--01_fred_chartbook/fred.md)<br>  |

