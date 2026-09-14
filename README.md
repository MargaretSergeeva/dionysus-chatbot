# Dionysus Chatbot

Data engineering and RAG pipeline supporting the Rheingau/Wiesbaden destination management chatbot. Scrapes and normalizes wine competition data ([die-besten-weine-hessens.de](https://www.die-besten-weine-hessens.de)) and tour content ([Outdooractive](https://www.outdooractive.com)), stores it in Postgres with pgvector for semantic search, and feeds a multilingual (DE/EN/NL/DA/IT/FR) chatbot.

Built as a praktikum project following the **CPMAI** lifecycle, with EU AI Act / GDPR documentation included.

## Project management

- Issue tracking & Knowledge Base: [YouTrack — dionysus-chatbot-2026 (DC2)](https://dionysus-chatbot-2026.youtrack.cloud)
- Commits referencing an issue ID (e.g. `DC2-14 add wine scraper`) auto-link to that issue
- Project follows CPMAI phases: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment/Monitoring — see Knowledge Base for phase docs

## Architecture

```
Source sites (Weinfinder, Outdooractive)
        │
        ▼
   scraper/           raw HTML/JSON snapshots
        │
        ▼
   pipeline/          cleaning & normalization (capitalization, missing fields)
        │
        ▼
   Postgres            curated tables + pgvector embeddings
        │
        ▼
   Chatbot platform    retrieval-augmented answers (structured filters + semantic search)
```

## Repo structure

```
/scraper/          scripts to fetch Weinfinder & Outdooractive data
/pipeline/          cleaning/normalization scripts, run before loading to Postgres
/schema/            SQL schema definitions (raw + curated tables, pgvector setup)
/docs/              project brief, requirements, AI Act & GDPR documentation
/data/              sample/snapshot CSVs (not full production data)
```

## Setup

1. Clone the repo
2. Create a free Postgres instance (Supabase or Neon) and enable the `pgvector` extension
3. Copy `.env.example` to `.env` and fill in your database connection string
4. Install dependencies: `pip install -r requirements.txt`
5. Run the schema migration: `psql $DATABASE_URL -f schema/init.sql`

## Running the pipeline

```bash
# 1. Scrape raw data
python scraper/weinfinder.py
python scraper/outdooractive.py

# 2. Clean and normalize
python pipeline/clean_wines.py

# 3. Load into Postgres + generate embeddings
python pipeline/load_to_db.py
```

## Data sources

| Source | Content | Access method |
|---|---|---|
| die-besten-weine-hessens.de | 763 wine entries (grape, type, award, taste, alcohol %) | Custom scraper (JS-rendered, not sitemap-crawlable) |
| Outdooractive | Hiking/cycling tours for Rheingau | Custom scraper (JS-rendered) |
| rheingau.com | Main site content (wanderwege, radfahren) | Platform's built-in sitemap import |

## Governance

- EU AI Act risk classification and GDPR data processing notes: see `/docs/ai-act-gdpr.md`
- Wine competition data is public information; no personal data is processed in the wine dataset

## Team

- Project owner: Rozaliia Tarnovetckaia
- Development: Oksana Kalkutina, Margarita Sergeeva
- Client: Rheingau-Taunus Kultur und Tourismus GmbH
