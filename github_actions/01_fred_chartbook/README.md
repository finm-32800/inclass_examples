# 01: FRED Chartbook, Rebuilt Daily by GitHub Actions

A minimal pydoit + chartbook pipeline that pulls US GDP from FRED and builds an
HTML documentation site. A scheduled GitHub Actions workflow (at the repo root:
[.github/workflows/deploy_examples_site.yml](../../.github/workflows/deploy_examples_site.yml))
re-runs it every day and publishes the result to GitHub Pages.

## What You Will Learn

- How a `doit` pipeline (pull → chart → build site) becomes a scheduled job
  that refreshes a public site with no human in the loop
- How chartbook turns a `chartbook.toml` manifest plus markdown stubs into a
  full documentation website (`chartbook build -f` → `docs/`)
- Why this example needs **no API key**: FRED data via `pandas-datareader` is
  keyless, so the workflow runs with no secrets (contrast with
  [../02_databento_secret/](../02_databento_secret/))

## Key Concepts

- **Dynamic end date.** `settings.py` sets `END_DATE = today`, so every run
  pulls data through the current day. The chart subtitle stamps the generation
  time so you can verify on the live site that the schedule fired.
- **`uptodate: [False]`.** The pull/chart/build tasks are never "up to date"
  from doit's perspective — fresh data is the whole point of the daily run.
- **Current chartbook manifest format.** This `chartbook.toml` uses the
  chartbook ≥ 0.1.1 format (`[project]`, `[charts.gdp]`, `[dataframes.fred]`).
  The older example in
  [pydoit/04_jupytext_notebooks](../../pydoit/04_jupytext_notebooks/) uses the
  legacy `[config]`/`chartbook_format_version` format — don't mix them up.

## How to Run Locally

```bash
cd github_actions/01_fred_chartbook
pip install -r requirements.txt
doit
```

Then open `docs/index.html` in a browser. Intermediate outputs:
`_data/fred.parquet` (the pull), `_output/gdp_chart.html` (the chart),
`docs/` (the full site — this is what gets deployed).

## Try It

1. Add the unemployment rate: put `"UNRATE"` in `series_to_pull`, create a
   `chart_unrate.py`, add `[charts.unrate]` to `chartbook.toml` plus a docs
   stub, and wire a new task into `dodo.py`.
2. Run `doit` twice in a row. Which tasks re-run anyway, and why? (See
   `uptodate` above.)
3. Change the workflow cron to `0 */6 * * *` (every 6 hours) and check the
   Actions tab after it fires.
