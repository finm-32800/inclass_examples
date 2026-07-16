# WRDS Datastream: Futures Library Exploration

Guided exploration of the WRDS LSEG Datastream Futures library (`tr_ds_fut`). The library is poorly documented, so these scripts teach you how to **browse, search, and retrieve** data hands-on — progressing from surveying the library structure to pulling prices and analyzing term structures.

## Scripts

| Script | What You Learn |
|--------|---------------|
| `01_explore_library.py` | Survey tables, schemas, row counts, and sample rows |
| `02_browse_products.py` | List all available futures products with contract counts and date ranges |
| `03_search_products.py` | Search by keyword (commodities, treasuries, equity indices) |
| `04_contract_metadata.py` | Inspect individual contracts: `contrcode → futcode` relationship |
| `05_pull_prices.py` | Fetch settlement prices (complete retrieval workflow) |
| `06_term_structure.py` | Compare term structures: commodity vs. Treasury futures |
| `07_pull_commodities_and_treasuries.py` | Reference: pull 21 commodities + 4 Treasury futures |
| `08_corn_futures.py` | Case study: Corn — front-month series, summary stats, and a price + term-structure plot saved to `_output/` |

Run them in order — each builds on what the previous one reveals.

## Key Concepts

**Library structure (`tr_ds_fut`):**

- `wrds_cseries_info` — Continuous series metadata (small catalog table)
- `wrds_contract_info` — Individual contract metadata: `contrcode` (product type), `futcode` (specific contract), delivery dates
- `wrds_fut_contract` — Daily prices by `futcode`: settlement, open, high, low, volume
- `dsfutcalcserval` — Calculated series values (continuous contracts)

**Key relationships:**

```
contrcode (product type, e.g. Gold = 2020)
    └── wrds_contract_info (one row per contract, has futcode + delivery date)
            └── wrds_fut_contract (daily prices per futcode)
```

**Data retrieval pattern:**

1. Search `wrds_contract_info` to find `contrcode` values for your product
2. Get `futcode` values for specific contracts
3. Pull prices from `wrds_fut_contract` using those `futcode` values

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your repo-root `.env` file has:
   ```
   WRDS_USERNAME=your_username
   ```

3. Run scripts in order:
   ```bash
   python 01_explore_library.py
   python 02_browse_products.py
   python 03_search_products.py
   python 04_contract_metadata.py
   python 05_pull_prices.py
   python 06_term_structure.py
   python 07_pull_commodities_and_treasuries.py
   python 08_corn_futures.py
   ```

   You will be prompted for your WRDS password on first connection (it gets cached via `.pgpass`).
