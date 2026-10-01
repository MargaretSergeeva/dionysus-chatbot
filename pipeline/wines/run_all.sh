#!/usr/bin/env bash
# Runs the wine steps 03–05 in order against Supabase. Every step is re-runnable.
# Needs: SUPABASE_DB_URL (Postgres connection string, Supabase → Project Settings → Database) and psql.
# Step 01 (import) runs separately when a new catalog arrives.
set -euo pipefail
cd "$(dirname "$0")"
: "${SUPABASE_DB_URL:?set SUPABASE_DB_URL}"
# 02_normalize.sql is left out until its differences to the live data are resolved (see its header, DC2-162).
for f in 03_lage_cleanup.sql 04_dryness.sql 05_body.sql; do
  echo "== $f"
  psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -q -f "$f"
done
echo "done — then run 'Publish wine page' and rebuild the Gastbot wine PDFs"
