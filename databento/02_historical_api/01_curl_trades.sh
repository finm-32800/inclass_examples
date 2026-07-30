#!/usr/bin/env bash
#
# Fetch ES trades from Databento using curl (raw HTTP REST API).
#
# This does the same thing as 01_historical_sdk/01_get_trades.py,
# but using curl instead of the Python SDK.
#
# Usage:
#   export DATABENTO_API_KEY="db-..."
#   bash 01_curl_trades.sh

# "set" is a shell built-in that changes the behavior of the current shell.
# It toggles runtime options that control how the script executes.
# Use "-" to enable an option, "+" to disable it (e.g., set +e disables -e).
#
# -e: exit immediately if any command fails
# -u: treat unset variables as errors   
# -o pipefail: fail the pipeline if any command in it fails (not just the last)
set -euo pipefail

# Require API key in environment
export $(grep DATABENTO_API_KEY ../../.env)
# ":" is a shell no-op (do nothing). We need it because "${VAR:?message}" is a
# parameter expansion, not a standalone command—without ":", the shell would try
# to execute the *value* of the variable as a command. The ":" safely discards
# the expanded value while still triggering the :? check, which aborts with
# "message" if the variable is unset or empty.
: "${DATABENTO_API_KEY:?Set DATABENTO_API_KEY in your environment}"

echo "Fetching ES trades via curl..."
echo "==============================="
echo

# HTTP Basic Auth: API key is the username, password is empty.
# The -u flag sets the Authorization header: base64(key:)
curl -s \
  -u "${DATABENTO_API_KEY}:" \
  -X POST \
  "https://hist.databento.com/v0/timeseries.get_range" \
  -d "dataset=GLBX.MDP3" \
  -d "symbols=ES.FUT" \
  -d "stype_in=parent" \
  -d "schema=trades" \
  -d "start=2024-08-01" \
  -d "end=2024-08-02" \
  -d "encoding=json" \
  -d "limit=10" 

echo
echo "Note: prices in the raw JSON are fixed-point integers."
echo "Multiply by 1e-9 to get the actual price."
echo "The SDK does this automatically."

# --------------------------------------------------------------------------
# Sample output (first record):
# --------------------------------------------------------------------------
#
# {
#   "ts_recv":  "1722470400079196344",    # Exchange receive timestamp (nanoseconds since Unix epoch)
#   "hd": {                                # Header — metadata attached to every message
#     "ts_event":     "1722470400078950957",  # Event timestamp at the matching engine (ns)
#     "rtype":        0,                      # Record type (0 = MBP-0 / trade)
#     "publisher_id": 1,                      # Publisher / venue ID (1 = CME)
#     "instrument_id": 118                    # Numeric instrument ID for this contract
#   },
#   "action": "T",      # Message action: "T" = Trade
#   "side":   "B",      # Aggressor side: "B" = buyer initiated, "A" = seller initiated
#   "depth":  0,        # Book depth level (0 for trades)
#   "price":  "5587750000000",   # Fixed-point price: 5587750000000 * 1e-9 = 5587.75
#   "size":   5,        # Number of contracts traded
#   "flags":  0,        # Bit flags (e.g. last message in packet)
#   "ts_in_delta": 14913,   # Capture latency: ts_recv - ts_event (nanoseconds)
#   "sequence": 45877799    # Exchange sequence number — detect gaps / ordering
# }
#
# --------------------------------------------------------------------------
# How to read the key fields:
# --------------------------------------------------------------------------
#
# TIMESTAMPS — Both ts_recv and ts_event are nanoseconds since 1970-01-01 UTC.
#   1722470400 seconds ≈ 2024-08-01 00:00:00 UTC (the start of our query window).
#   The fractional nanoseconds capture sub-microsecond precision.
#
# PRICE — Databento stores prices as fixed-point integers to avoid floating-point
#   rounding. Divide by 1e9 to get dollars:
#     5587750000000 * 1e-9 = $5,587.75 (ES futures price)
#     5587500000000 * 1e-9 = $5,587.50
#   The Python SDK does this conversion automatically.
#
# SIDE — The aggressor side of the trade:
#   "B" = a buy order hit a resting ask  (buyer aggressed)
#   "A" = a sell order hit a resting bid  (seller aggressed)
#
# SIZE — Contract quantity. ES trades in multiples of 1 contract
#   ($50 × index per contract).
#
# ts_in_delta — Nanoseconds between ts_event and ts_recv. Tells you
#   how long the message took to travel from the matching engine to
#   the feed handler (~14–15 μs in these records).
#
# --------------------------------------------------------------------------
