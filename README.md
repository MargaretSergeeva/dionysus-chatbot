# Dionysus Chatbot

RAG chatbot for the Rheingau tourism platform (rheingau.com) — wine-finder search (763 wines) and regional tour/activity discovery, grounded in rheingau.com's own content (1,922 pages) and wine competition data.

This repo holds the chatbot's source of truth: the modular system prompt, the Supabase schema and retrieval functions, the data/publishing scripts and the test sets.

## What makes this project distinctive

- **Modular, versioned prompt** — behavior is built from small modules (one file per capability), not one static prompt. `scripts/assemble_prompt.py` builds two prompts from the same modules: `full` (own stack: Dify + Supabase) and `gastbot` (partner platform Gastbot). Each module is gated by data availability and by what the platform already does. See [`prompts/README.md`](prompts/README.md) and [`prompts/CHANGELOG.md`](prompts/CHANGELOG.md). Current version: see `prompts/VERSION`.
- **Prompt text names no tables** — data is described in words; physical names live in module headers and `prompts/data_sources.yaml`, so a module follows the data when it reaches a new build.
- **Core vs. conditional behavior** — always-on rules (PII, health data, AI disclosure) are kept apart from data-dependent modules.
- **Multilingual** — answers in the user's language (DE/EN/NL/DA/IT/FR).
- **Tests per module** — each test names the prompt modules it checks, so failures group by module (`scripts/check_test_coverage.py` enforces coverage).
- **Built-in compliance** — EU AI Act and GDPR rules are prompt modules (AI disclosure, PII, logging/deletion), not an afterthought.

## Repo structure

```
prompts/       modular system prompt (modules, adapters, data registry, gate, dist builds) — source of truth
schema/
  data/        one-off data fixes and lookup tables (SQL)
  functions/   Postgres retrieval functions (semantic, filter, hybrid) — see schema/functions/README.md
  views/       wines_enriched view (what the bot reads for wines)
scripts/       prompt assembler, test-coverage check, wine page/PDF builders, site ingest, Dify smoke test
evaluation/    test sets (gastbot_v1_questions.csv), run results (runs/), archive — see evaluation/README.md
.github/workflows/  prompt gate & build, Dify smoke test, wine page publishing, rheingau.com ingest
```

## Architecture

```
rheingau.com pages ──► scripts/add_excluded_pages_back.py ──► Supabase (Postgres + pgvector)
wine data (763) ─────► wines → wines_enriched view          rheingau_pages, rheingau_rag_chunks_v2, wines_*
                                                                   │
                         retrieval functions (schema/functions) ◄──┤
                                                                   ▼
prompts/modules ──► assemble_prompt.py ──► dist/full ───────► Dify (our stack)
                                      └──► dist/gastbot ────► Gastbot (partner platform, own RAG)
                                                                   ▲
wines_enriched ──► build_wine_page.py / build_wine_pdfs.py ────────┘  (GitHub Pages + PDFs for Gastbot)
```

Gastbot indexes rheingau.com with its own RAG and has no Supabase access; the wine catalog reaches it as a crawled GitHub Pages site and uploaded PDFs.

## Setup

```
pip install -r requirements.txt          # prompt tooling (pyyaml)
pip install requests beautifulsoup4      # only for the ingest / wine page scripts
```

Secrets are read from the environment (never committed): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (`sb_secret_…` or legacy service_role key), `COHERE_API_KEY` (embeddings), `DIFY_API_KEY` (smoke test). GitHub Actions use repository secrets of the same names.

Schema changes are applied to Supabase as migrations (the SQL files here are the source of truth); they are not run by hand against production.

## Common tasks

**Prompt** (details in `prompts/README.md`)

```
python scripts/assemble_prompt.py check                 # validate modules, lint both builds
python scripts/assemble_prompt.py build --target all    # write prompts/dist/<target>/
python scripts/assemble_prompt.py verify                # fail if committed dist is stale
python scripts/check_test_coverage.py --target gastbot --tests evaluation/gastbot_v1_questions.csv
```

A tag `prompt-vX.Y` publishes both builds as a GitHub Release.

**Wine pages for Gastbot** (after wine data changes)

- Run the *Publish wine page* workflow (builds `/wines/` pages per winery, a sitemap and a filterable table page for people, published with GitHub Pages), or run `scripts/build_wine_page.py` locally.
- `scripts/build_wine_pdfs.py` builds the wine catalog PDFs for Gastbot's Files source; re-upload them to Gastbot.

**rheingau.com content** — run the *Update Rheingau Website* workflow (leave "apply" unchecked for a dry run). Needs a machine that can reach rheingau.com.

**Testing** — send the questions in `evaluation/gastbot_v1_questions.csv` to the bot, record results under `evaluation/runs/`, and group failures by the `modules` column. `scripts/dify_smoke_test.py` checks the merged prompt against a live Dify app on every push to `main` that touches `prompts/`.

## Data sources

| Source | Content | Access |
| --- | --- | --- |
| die-besten-weine-hessens.de | 763 wine entries (grape, type, award, taste, alcohol %) | Custom scraper; loaded into Supabase `wines`, read through `wines_enriched` |
| rheingau.com | Main site content, tours, hiking and cycling routes, privacy/imprint pages | Scraped into `rheingau_pages` and `rheingau_rag_chunks_v2` (Cohere embeddings); Gastbot indexes it itself |

The registry of tables, views and functions and which build reaches them is `prompts/data_sources.yaml`.

## Project management

- Issues and Knowledge Base: [YouTrack — dionysus-chatbot-2026 (DC2)](https://dionysus-chatbot-2026.youtrack.cloud)
- Commits reference an issue ID (e.g. `DC2-129 …`) and auto-link to it
- Phases follow CPMAI: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment/Monitoring — see the Knowledge Base

## Governance

- Wine competition data is public information; no personal data is processed in the wine dataset
- Chatbot behavior for personal data, health-related requests, AI disclosure and chat logging is defined in `prompts/modules/1-role/` and `prompts/modules/3-key-rules/`
- EU AI Act risk classification and GDPR documentation: kept in the YouTrack Knowledge Base

## Team

- Project owner: Rozaliia Tarnovetckaia
- Development: Oksana Kalkutina, Margarita Sergeeva
- Client: Rheingau-Taunus Kultur und Tourismus GmbH
