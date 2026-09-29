# Evaluation

Test sets for the Dionysus chatbot. Strategy: YouTrack **DC2-A-27** (question design), **DC2-A-132** (CI regression tests), tasks **DC2-137 … DC2-140**.

## gastbot_v1_questions.csv — 100 tests for prompt-v1.0 on Gastbot

Scope: Gastbot V.1 — rheingau.com content through Gastbot's RAG only (no wine catalog, no SQL tools).
Built 28.09.2026 from the team set "TEST_BOT – 100 Testfragen" (DC2-A-37, 19.09.2026; 72 questions reused, column `origin` = `TB-<id>`) plus 28 new tests for modules and platform built-ins the old set did not cover.
Facts in `expected_behavior` / `must_include` were checked against the Supabase copy of rheingau.com (`rheingau_pages`, `rheingau_rag_chunks_v2`) on 28.09.2026. Gastbot indexes the site itself — a failing fact test can also mean Gastbot's index differs from ours.

| Column | Meaning |
|---|---|
| `id` | `GB1-NNN` |
| `category` | topic group (German, as in the team set) |
| `language` | language of the question; non-German rows test Reply Translation |
| `context` | earlier turns for multi-turn tests (`User: … \| Assistant: …`); empty = first message |
| `question` | message to send |
| `test_type` | what the test stresses |
| `modules` | prompt modules under test: module labels such as `1.4` (Language) or `3.3` (Alcohol-free safety), `PLATFORM:<builtin>` = Gastbot built-in |
| `expected_behavior` | pass criterion for a human or LLM judge |
| `must_include` / `must_not_include` | `;`-separated keywords for an automatic check (case-insensitive substring) |
| `source_url` | page the answer should come from (when one page is expected) |
| `origin` | `TB-<id>` = team set row, `new` = added for v1.0 |

### Rules the expected answers follow (prompt-v1.0)

- **No dates or times for events** (module 3.6) — the team set expected dates; v1.0 answers give the event page instead.
- **No confirmed prices** (module 3.6) — even when a price is on the page.
- **No live status** (availability, today's menu, traffic, weather).
- **No invented details** — undocumented facts are named as undocumented, with the next step (module 2.10).

## Module coverage

Every module of a build must have at least one test. CI checks this:

```bash
python scripts/check_test_coverage.py --target gastbot --tests evaluation/gastbot_v1_questions.csv
```

When a module is added or its status becomes `supported`, add tests for it in the same PR — otherwise CI fails. This links testing to the prompt modules: a new module ships only with its tests.

## Running the tests (until DC2-138 automates it)

Gastbot has no API access for us yet, so the tests run by hand — on the `gastbot` build:

1. Open a new chat for each row (multi-turn rows: send the `context` turns first).
2. Record the answer and a verdict (`pass` / `fail` + short reason) in a copy of the CSV named `runs/<build>_<YYYY-MM-DD>.csv` (e.g. `runs/gastbot_2026-10-02.csv`) with extra columns `actual_answer`, `verdict`, `notes`.
3. For each fail, note whether retrieval (wrong/missing page) or generation (right page, wrong answer) failed (DC2-A-27 §5).
4. Compare pass rates per category and per module; keep the better build.

The Dify build (`full`) will run the same questions automatically via the Dify API once DC2-138 … DC2-140 are done.
