# Data pipeline

Every step that cleans, normalizes, enriches or anonymizes data lives here as a script — not only in Supabase.
A re-import must be able to run the whole chain again. Plan and inventory: YouTrack **DC2-162**.

Rules
- One file per step, numbered in run order; each names its YouTrack issue in the header.
- Re-runnable: running a step twice gives the same result (`on conflict`, `if not exists`, guarded updates).
- Raw source columns are never overwritten by derived values — derived data goes into its own columns/tables.
- Before a destructive change: back up the old values into `archive.<table>_<yyyymmdd>`.
- Applied to Supabase as a migration with the same name; the file here is the source of truth.

## wines/ — wine catalog (→ view `wines_enriched`, `schema/views/wines_enriched.sql`)

| Step | File | Issue | In | Out |
|---|---|---|---|---|
| 1 | `01_import.py` (placeholder) | DC2-162 | Weinfinder die-besten-weine-hessens.de | `wines` raw columns |
| 2 | `02_normalize.sql` ⚠ not in run_all yet | DC2-10, 11, 12 | `wines` raw + lookup tables | `rebsorte_normalized`, `rebsorte_array`, `weinart_normalized`, `weinname_normalized`, `synonyms` |
| 3 | `03_lage_cleanup.sql` | — (01.10.2026) | `wines.lage_weinberg` | Lage without trailing " -" |
| 4 | `04_dryness.sql` | DC2-143 | `restzucker_g_l`, `saeure_g_l` | `wine_dryness` (EU 2019/33 Annex III) |
| 5 | `05_body.sql` | DC2-144 | `alkohol_pct`, `saeure_g_l` | `wine_body` (only "Vollmundig") |

Run 3–5: `SUPABASE_DB_URL=… pipeline/wines/run_all.sh`. Step 2 differs from the live data (see its header) and runs only after that is resolved.
Steps 4 and 5 were checked on 01.10.2026: their rules reproduce the existing `wine_dryness` (763 rows) and `wine_body` (16 rows) exactly. Afterwards: GitHub Action *Publish wine page* and the Gastbot wine PDFs (`scripts/build_wine_pdfs.py`).

## rheingau_pages/ — website content (→ `rheingau_pages`, `rheingau_rag_chunks_v2`)

| Step | File | Issue | What it sets |
|---|---|---|---|
| 1 | `01_city_plz_map.sql` | DC2-150 | city from postal code |
| 2 | `02_transport_type.sql` | DC2-142 | `transport_type` for 71 reviewed pages |
| 3 | `03_alcohol_free_offer.sql` | DC2-142 | `alcohol_free_offer` for 29 reviewed pages |
| 4 | `04_excluded_pages.sql` | DC2-133, 152 | pages excluded from the bot |

Still to bring in (DC2-162): crawl + chunking + embeddings, amenity flags, past-event filter, regional projects.

## privacy/ — guest data (planned)

PII anonymization of logged `sessions` / `messages` (DC2-109), retention (DC2-100). Runs on a schedule, not on import.
