# CLAUDE.md

Orientation for AI assistants working in this repo. Start with `README.md`, then `prompts/README.md` (most important), `prompts/CHANGELOG.md` (recent decisions) and `evaluation/README.md`.

## What the project is

Dionysus is a RAG chatbot for rheingau.com (Rheingau tourism): wine search (763 wines) and discovery of tours and activities (1,922 pages). Two builds come from one set of prompt modules:

- `full` — our own stack (Dify + Supabase)
- `gastbot` — partner platform Gastbot, which has its own RAG and no Supabase access

## Rules

- **Prompt source of truth:** edit only `prompts/modules/`. Never edit `prompts/dist/` by hand; rebuild with `python scripts/assemble_prompt.py build --target all`, then run `check` and `verify`.
- **No table, view or function names in prompt text.** Describe data in words. Physical names go only in module headers and `prompts/data_sources.yaml`. The gate fails otherwise.
- **No build-specific text inside a module.** Split the module instead.
- **Gastbot gating:** a module reaches Gastbot only if its data reaches Gastbot and the platform does not already do the same thing.
- **Wine column names are German** (`weingut`, `rebsorte`, `lage`, …) and shared by the prompt, the wine pages and the view `wines_enriched`.
- **Schema changes:** the SQL in `schema/` is the source of truth. Apply it as Supabase migrations, not by hand against production. Check existing tables first.
- **Tests:** every module needs a test (`python scripts/check_test_coverage.py --target gastbot --tests evaluation/gastbot_v1_questions.csv`).
- **Secrets** come only from the environment, never from files in the repo.

## Workflow

- GitHub: `MargaretSergeeva/dionysus-chatbot`. Work on a branch and open a PR; do not push to `main`.
- YouTrack project DC2: commit messages start with the issue ID (e.g. `DC2-129 …`). Requirements and decisions are in Knowledge Base articles (DC2-A-nn).
- Supabase holds the data and the retrieval functions (`schema/functions/README.md`).

## Easy to get wrong

- Gastbot's RAG cannot filter or count; those tests expect honest partial answers.
- After wine data changes, run the *Publish wine page* workflow and re-upload the wine PDFs (`scripts/build_wine_pdfs.py`) to Gastbot.
- Scraping rheingau.com only works from a machine that can reach the site; the cloud workspace cannot.
- Prompt rules: no event dates, no confirmed prices, no live status (availability, weather, traffic).

## Open points

The wine scraper and the EU AI Act / GDPR documentation are not in this repo; ask where they live before documenting them.
