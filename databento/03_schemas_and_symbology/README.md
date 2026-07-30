# 06 Schemas and Symbology

A conceptual capstone tying together the data model concepts from earlier examples: how Databento organizes data (schemas) and identifies instruments (symbology).

## What you'll learn

- The four symbology types and when to use each
- The schema hierarchy from tick-level to daily bars
- How to choose the right schema and symbology for your use case

## Symbology Types

| Type | Example | Use case |
|------|---------|----------|
| `raw_symbol` | `ESH4`, `ESU4` | Specific contract by exchange ticker |
| `parent` | `ES.FUT` | All contracts for a product (e.g., all ES futures) |
| `continuous` | `ES.c.0` | Front-month (rolling), no manual roll management |
| `instrument_id` | `3403` | Numeric ID from the exchange, most compact |

### Reading a `raw_symbol`

CME futures tickers follow the format **Root + Month Code + Year Digit**. For example, `ESU4` = **ES** (E-mini S&P 500) + **U** (September) + **4** (2024).

**Futures month codes:**

| F | G | H | J | K | M | N | Q | U | V | X | Z |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |

ES futures trade on a quarterly cycle, so you'll only see **H** (Mar), **M** (Jun), **U** (Sep), **Z** (Dec).

### Reading a `parent` symbol

Format: **Root.AssetClass**. The suffix indicates the instrument type:

- `ES.FUT` — all E-mini S&P 500 **futures** (outrights and spreads)
- `ES.OPT` — all E-mini S&P 500 **options**

### Reading a `continuous` symbol

Format: **Root.Rule.Rank**, where:

- **Rule** selects the roll method: `c` = calendar (nearest expiry), `v` = volume (highest daily volume), `n` = open interest (highest OI)
- **Rank** selects which contract: `0` = front month, `1` = second nearest, `2` = third nearest, etc.

Examples: `ES.c.0` = front-month ES by expiry date; `ES.v.0` = most-traded ES contract by volume.

### `instrument_id`

Numeric IDs assigned by the exchange. Compact but less portable — some venues remap IDs daily.

## Schema Hierarchy

```
Most granular                              Least granular
     |                                          |
     v                                          v
    mbo  →  mbp-10  →  mbp-1  →  trades  →  ohlcv-1s  →  ohlcv-1m  →  ohlcv-1d
 (L3 book)  (L2 depth)  (L1 top)  (last sale)  (1s bars)   (1m bars)   (daily)
```

More granular = more data = higher cost. Choose the coarsest schema that meets your needs.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# Compare symbology types
python 01_symbology_types.py

# Compare schema granularity
python 02_schema_comparison.py
```

## Key points

- `parent` is the most convenient for getting "all ES futures" without knowing specific tickers
- `continuous` is ideal for backtesting — it handles contract rolls automatically
- `raw_symbol` is what you'd use on a trading desk (specific contract)
- Start with `ohlcv-1m` or `trades` for most research; only use `mbo`/`mbp-10` if you need order book depth

## Try it

- In `01_symbology_types.py`, try `NQ.FUT` (Nasdaq futures) as the parent symbol
- In `02_schema_comparison.py`, add `ohlcv-1h` as a fourth schema level
- Use `continuous` symbology with `ES.c.0` to get front-month data
