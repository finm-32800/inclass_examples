# 02: API Keys as GitHub Actions Secrets (Databento)

The simplest possible authenticated data pull in CI: fetch the latest US
Treasury futures prices from Databento and render one standalone HTML bar
chart. The point of the example is not the chart — it's how the API key
travels: repo secret → workflow env → environment variable → SDK, without
ever appearing in code, logs, or git history.

## What You Will Learn

- How to store an API key as a **GitHub Actions repository secret** and pass
  it to a step as an environment variable
- How the *same* environment variable works locally (loaded from `.env` by
  `python-dotenv`) and in CI (injected by the workflow) with zero code changes
- The Databento cost-guard habit: estimate with the free
  `metadata.get_cost` call before pulling, abort if it's unexpectedly large

## Key Concepts

- **Secrets never touch the repo.** `.env` is gitignored; in CI the value
  lives in the repo's encrypted secret store, and GitHub masks it in logs.
  The workflow step passes it explicitly:

  ```yaml
  env:
    DATABENTO_API_KEY: ${{ secrets.DATABENTO_API_KEY }}
  ```

- **Fail loudly when the key is missing.** `01_pull_prices.py` checks the
  variable up front and prints instructions for both settings, instead of
  letting the SDK fail with a cryptic authentication error.
- **Clamp the end date.** The daily cron can fire before yesterday's bars are
  published, so the script asks the (free) metadata API for the dataset's
  available range and never requests past it.
- **`.v.0` continuous contracts.** Prices are for the volume-rolled
  front-month contract — the one people actually mean by "the 10-year
  future." See the comment in `01_pull_prices.py`.

## Setup

1. Copy the repo-root `.env.example` to `.env` and fill in
   `DATABENTO_API_KEY` (get one at https://databento.com).
2. For CI: add the same value as a repository secret:

   ```bash
   gh secret set DATABENTO_API_KEY --repo <owner>/<repo>
   ```

## How to Run Locally

```bash
cd github_actions/02_databento_secret
pip install -r requirements.txt
doit
```

Then open `_output/index.html` in a browser.

## Try It

1. Temporarily rename `DATABENTO_API_KEY` in your `.env` and run
   `python 01_pull_prices.py` — read the error message. This is the failure
   mode you'd see in CI if the secret were missing.
2. Add S&P 500 futures: append `"ES"` to `PRODUCTS` with tenor label
   `"S&P 500"`. (Watch the y-axis — ES trades near 6,000 while Treasuries
   trade near 100. What does that do to the chart? See the one-axis rule.)
3. Switch `.v.0` to `.c.0` and compare the ZT and ZF prices around a
   quarterly roll date.
