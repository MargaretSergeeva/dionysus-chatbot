# Dionysus Chatbot

Data pipeline and RAG chatbot for the Rheingau tourism platform (rheingau.com) — wine-finder search and regional tour/activity discovery.

Dionysus is a RAG-based chatbot for the Rheingau-Taunus destination management platform, covering wine-finder search (763 wine entries) and regional tour/activity discovery sourced from rheingau.com itself.

## What makes this project distinctive

- **Modular, versioned prompt architecture** — instead of one static system prompt, behavior is built from small, independently-versioned prompt blocks (one file per capability: wine filtering, alcohol-free search, pairing suggestions, etc.), each tagged `supported`/`partial`/`blocked` by data readiness. A merge script assembles only supported blocks into the live prompt — features ship or roll back independently, without touching the rest.
- **Core vs. conditional behavior separation** — always-on behavioral rules (e.g. the PII-handling guardrail) are kept apart from data-dependent prompt blocks, since they don't toggle with data status.
- **Three-tool PM constellation** — GitHub (code/source of truth), YouTrack DC2 (issues, requirements, phase docs, traceability), Supabase/Postgres+pgvector (curated data + embeddings) — cross-linked by convention (commits reference issue IDs, new files link their YouTrack article and vice versa).
- **Multilingual retrieval** — DE/EN/NL/DA/IT/FR chatbot answers grounded in semantic search over wine competition data and rheingau.com's own tour/activity content.
- **Built-in compliance** — EU AI Act risk classification and GDPR documentation live alongside deployment, not bolted on after.

## Project management

- Issue tracking & Knowledge Base: [YouTrack — dionysus-chatbot-2026 (DC2)](https://dionysus-chatbot-2026.youtrack.cloud)
- Commits referencing an issue ID (e.g. `DC2-14 add wine scraper`) auto-link to that issue
- Project follows CPMAI phases: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment/Monitoring — see Knowledge Base for phase docs

## Architecture

```
Source sites (Weinfinder, rheingau.com)
        │
        ▼
   scraper/           raw HTML/JSON snapshots
        │
        ▼
   pipeline/          cleaning & normalization
        │
        ▼
   Postgres (Supabase) curated tables + pgvector embeddings
        │
        ▼
   Chatbot platform    retrieval-augmented answers (structured filters + semantic search)
        │
        ▼
   compliance/         EU AI Act & GDPR checks applied at deployment
```

## Repo structure (proposed — CPMAI-aligned)

```
/docs/business-understanding/
/docs/data-understanding/
/pipeline/                  cleaning/normalization scripts (Data Preparation)
/modeling/
  /modeling/schema/         SQL schema + pgvector setup (or keep /schema/ top-level — TBD)
  /modeling/prompts/        modular prompt blocks (moved from /prompts/)
/evaluation/                 testing
/deployment/
  /deployment/compliance/   EU AI Act & GDPR docs (moved from /docs/ai-act-gdpr.md)
```

## Setup

1. Clone the repo
2. Create a free Postgres instance (Supabase or Neon) and enable the `pgvector` extension
3. Copy `.env.example` to `.env` and fill in your database connection string
4. Install dependencies: `pip install -r requirements.txt`
5. Run the schema migration: `psql $DATABASE_URL -f schema/init.sql`

## Running the pipeline

```
# 1. Scrape raw data
python scraper/weinfinder.py
python scraper/rheingau_site.py

# 2. Clean and normalize
python pipeline/clean_wines.py

# 3. Load into Postgres + generate embeddings
python pipeline/load_to_db.py
```

## Data sources

| Source                      | Content                                                  | Access method                                       |
| ---------------------------- | --------------------------------------------------------- | ------------------------------------------------------ |
| die-besten-weine-hessens.de | 763 wine entries (grape, type, award, taste, alcohol %)  | Custom scraper (JS-rendered, not sitemap-crawlable) |
| rheingau.com                | Main site content, tours, wanderwege, radfahren         | Platform's built-in sitemap import                  |

## Governance

- EU AI Act risk classification and GDPR data processing notes: see `/deployment/compliance/ai-act-gdpr.md`
- Wine competition data is public information; no personal data is processed in the wine dataset

## Team

- Project owner: Rozaliia Tarnovetckaia
- Development: Oksana Kalkutina, Margarita Sergeeva
- Client: Rheingau-Taunus Kultur und Tourismus GmbH
