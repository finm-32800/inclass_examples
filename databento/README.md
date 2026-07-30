# Databento: SDK vs API

This directory teaches how to pull market data from [Databento](https://databento.com/) while illustrating the difference between using a **Python SDK** and making **raw API calls** (HTTP/curl).

The Historical client is shown both ways — through the SDK and through the underlying HTTP API — so you can see what the SDK abstracts away. Databento also has a Live client for real-time streaming, but our subscription does not license it; see [No live-data license](#no-live-data-license) below.

All four examples are also merged into a single notebook,
[`01_databento_ipynb.py`](01_databento_ipynb.py) (jupytext percent format).
The repo-root `dodo.py` converts and executes it (`doit
run_notebooks:01_databento_ipynb`), and the executed
`01_databento_ipynb.ipynb` is committed so the course textbook can embed it
without re-running any queries. If you change the notebook source, re-run the
doit task and commit the refreshed `.ipynb` alongside it.

## Cost Warning

Databento charges per query. Every script in this directory uses `limit=10` to keep costs negligible. The SDK examples call `metadata.get_cost` (free) before fetching data and skip the download if the cost is non-zero, so you never spend money by accident.

## Setup

1. Install the Python package:
   ```bash
   pip install databento python-dotenv pandas requests
   ```

2. Set your API key in the repo-root `.env` file:
   ```
   DATABENTO_API_KEY=db-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   The `.env.example` at repo root already has this variable defined.

3. For bash scripts, export the key in your shell:
   ```bash
   export DATABENTO_API_KEY="db-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

## Dataset

All examples use **GLBX.MDP3** (CME Globex), which covers E-mini S&P 500 futures (ES) and other CME products. Students have subscriptions to this dataset.

## Examples

| Directory | Topic | Protocol |
|-----------|-------|----------|
| `01_historical_sdk` | Fetch historical trades via Python SDK | SDK |
| `02_historical_api` | Same query via curl and HTTP requests | HTTP REST |
| `03_schemas_and_symbology` | Data schemas and symbol types | SDK |
| `04_treasury_futures_brief` | Treasury futures market brief (charts + table) | SDK |

Work through them in order. The first pair (01+02) runs the same query two ways — SDK first, then the raw HTTP protocol underneath — so you can see exactly what the SDK abstracts away.

## No live-data license

Databento has two modes of access, and **we only have the historical one**:

- **Historical** (`db.Historical()`) — archived data, billed per query. This is
  what every example here uses, and it all works.
- **Live** (`db.Live()`) — real-time streaming over a persistent TCP
  connection, billed per subscription. **Our subscription does not include
  this.**

An API key with historical access only will authenticate against the live
gateway and then be rejected:

```
BentoError: A live data license is required to access GLBX.MDP3.
```

That message is about entitlement, not a bad key — the same key keeps working
for every historical example here. Because we cannot run them, the two live
streaming examples that used to live in this directory (`03_live_sdk` and
`04_live_raw_tcp`, covering `db.Live()` and the raw CRAM/TCP wire protocol)
have been removed. They are still in git history if a live license is ever
added — find the commit that deleted them, then restore from its parent:

```bash
# 1. Find the deletion commit
git log --diff-filter=D --oneline -- databento/03_live_sdk databento/04_live_raw_tcp

# 2. Restore both modules from the commit just before it
git checkout <commit>^ -- databento/03_live_sdk databento/04_live_raw_tcp
```

## SDK vs API — What's the Difference?

| | SDK (`databento` package) | Raw API (curl) |
|---|---|---|
| **Auth** | Pass key to constructor or set env var | HTTP Basic Auth |
| **Data format** | Auto-decoded to DataFrames | Raw JSON or binary DBN |
| **Price scaling** | Automatic (human-readable floats) | Raw fixed-point integers (multiply by 1e-9) |
| **Integer encoding** | Native Python `int` | JSON encodes 64-bit ints as *strings* |
| **Error handling** | Python exceptions | HTTP status codes |
