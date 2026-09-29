#!/usr/bin/env bash
# Raw Tables-API calls with curl, on a free table so any registered key works.
#
# Usage:
#   bash 01_curl_tables.sh
# The key is read from NASDAQ_DATA_API_KEY, falling back to the repo-root .env.
set -euo pipefail

if [[ -z "${NASDAQ_DATA_API_KEY:-}" ]]; then
  set -a; source "$(dirname "$0")/../../.env"; set +a
fi
: "${NASDAQ_DATA_API_KEY:?Set NASDAQ_DATA_API_KEY in your shell or in the repo-root .env}"

BASE="https://data.nasdaq.com/api/v3/datatables"
TABLE="NDAQ/RTAT10"      # Retail Trading Activity Tracker, daily top 10 (free)
SINCE=$(python -c "import datetime as d; print(d.date.today() - d.timedelta(days=14))")

# The key can go in the URL (?api_key=...) or in this header. The header keeps
# it out of shell history, server logs, and screenshots, so use the header.
AUTH=(-H "X-Api-Token: $NASDAQ_DATA_API_KEY")

echo "1. Metadata: columns, filters, primary key, last refresh"
curl -s "${AUTH[@]}" "$BASE/$TABLE/metadata.json" | python -m json.tool | head -30
echo "   ..."

echo; echo "2. Filters (column=value, column.gte=), column selection, page size"
curl -s "${AUTH[@]}" "$BASE/$TABLE.json?ticker=TSLA&date.gte=$SINCE&qopts.columns=date,ticker,activity,sentiment&qopts.per_page=5" | python -m json.tool

echo; echo "3. CSV instead of JSON: swap the extension (comma lists filter on several values)"
curl -s "${AUTH[@]}" "$BASE/$TABLE.csv?ticker=TSLA,NVDA&date.gte=$SINCE&qopts.per_page=6"

echo; echo "4. Pagination: a page that is not the last one carries meta.next_cursor_id"
PAGE1=$(curl -s "${AUTH[@]}" "$BASE/$TABLE.json?ticker=TSLA&qopts.columns=date,activity&qopts.per_page=3")
echo "$PAGE1" | python -c "import json,sys; j=json.load(sys.stdin); print('   rows:', j['datatable']['data']); print('   next_cursor_id:', j['meta']['next_cursor_id'])"
CURSOR=$(echo "$PAGE1" | python -c "import json,sys; print(json.load(sys.stdin)['meta']['next_cursor_id'])")
echo "   ...pass it back as qopts.cursor_id to get the next page:"
curl -s "${AUTH[@]}" "$BASE/$TABLE.json?ticker=TSLA&qopts.columns=date,activity&qopts.per_page=3&qopts.cursor_id=$CURSOR" \
  | python -c "import json,sys; j=json.load(sys.stdin); print('   rows:', j['datatable']['data'])"

echo; echo "5. Bulk export: qopts.export=true returns a pre-signed link to a zip, not the rows"
curl -s "${AUTH[@]}" "$BASE/$TABLE.json?qopts.export=true" \
  | python -c "import json,sys; f=json.load(sys.stdin)['datatable_bulk_download']['file']; print('   status:', f['status']); print('   snapshot:', f['data_snapshot_time']); print('   link:', f['link'][:70] + '...')"
