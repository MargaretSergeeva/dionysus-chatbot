# Evaluation

Test sets for the Dionysus chatbot. Strategy: YouTrack **DC2-A-27** (question design), **DC2-A-132** (CI regression tests), tasks **DC2-137 … DC2-140**.

## gastbot_v1_questions.csv — 125 tests for the Gastbot build (prompt-v.1_Gastbot)

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
| `origin` | `TB-<id>` = team set row, `new` = added for v1.0, `new-wines` = wine catalog in Gastbot (29.09.2026), `DC2-A-45 #n` = confirmed customer scenario n, `TB-customer` = customer question sheet |

### Rules the expected answers follow (prompt-v1.0)

- **No dates or times for events** (module 3.6) — the team set expected dates; v1.0 answers give the event page instead.
- **No confirmed prices** (module 3.6) — even when a price is on the page.
- **No live status** (availability, today's menu, traffic, weather).
- **No invented details** — undocumented facts are named as undocumented, with the next step (module 2.9).

### Added 29.09.2026 (GB1-102 … GB1-125, DC2-129)

- **Wine catalog in Gastbot** (module 2.4, `new-wines`): single wine, body, missing fields, unknown wine name, follow-up, vague wine question. The wine page is the source (`source_url`).
- **Two V.1-limit tests** (GB1-103, GB1-104): exact filters and counts. RAG cannot filter or count; pass = honest partial answer. They show the customer what V.2 (Tools) adds.
- **All 9 confirmed customer scenarios from DC2-A-45** and uncovered questions from the customer sheet.

**Reading results by module:** every row names its modules (`modules`). Group fails by module to see which part of the prompt does not work; `PLATFORM:<builtin>` fails point to Gastbot settings, not the prompt.

### Archive

`archive/` keeps the older sets from DC2-A-37 and the `run_eval.py` template from DC2-A-39 as sources only. They are **not** test sets for the current prompt: they expect exact dates and prices (forbidden by 3.6), food pairings (removed) and old KB ids. The template posts to a local `/api/chat` that does not exist; the new runner is DC2-138.

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

## Review process (from 30.09.2026)

Team side stays Telegram + Excel; Margarita mirrors everything here (source of truth).

```
Oksana prompt ──► prompts/gastbot/prompt-v.X.Y_Gastbot.md  + git tag prompt-v.X.Y_Gastbot
Vova runs the fixed question set ──► file via Telegram
   python scripts/eval/intake.py <file> --track oksana/gastbot/vX.Y --prompt-tag prompt-v.X.Y_Gastbot
      ──► evaluation/runs/oksana/gastbot/vX.Y__<date>.csv (+ .meta.json)
   python scripts/eval/review_xlsx.py fill --run <that csv> --split
      ──► evaluation/review/…__Margarita.xlsx / …__Oksana.xlsx   (send back via Telegram, 50/50 by question_id)
reviewed Excel back:
   python scripts/eval/review_xlsx.py import <file.xlsx> --out evaluation/review/<run>__reviewed.csv
```

- **Question count: 125 (confirmed 30.09.2026).** Rozaliia's "120" was an outdated number; the repo set is the reference for all runs.
- **Fixed IDs**: `id` in `gastbot_v1_questions.csv` never changes across runs. `python scripts/eval/questions_tool.py compare <file>` lists IDs/texts that differ from another file (Margarita's Excel, Rozaliia's 120). The repo has 125; retire a row with `origin=retired` instead of deleting.
- **Reviewer split**: column `reviewer` (63 Margarita / 62 Oksana, balanced per category). Only empty cells are filled by `questions_tool.py assign`, so assignments stay stable.
- **Reference data**: `expected_answer` and `key_facts` (`;`-separated) per question — still empty; fill them for the judge (and for reviewers' ideal answers).
- **Review template**: `templates/review_template.xlsx` (regenerate with `review_xlsx.py template`). Locked: question_id, category, question, answer, reviewer. Editable: score, ideal_answer, fix_type (prompt/Vova/data/links), check_length, check_link_at_end, check_general_vs_specific, comment. **Score is inverted: 1 = super, 5 = bad.** Sheet protection has no password — it prevents accidents only.
- **Prompt rules as criteria** (Rozaliia): limited length, general link at the end, general question → general answer / specific → specific.
- **Tracks**: `oksana/gastbot/<ver>` and `margarita/dify/<ver>`; every run stores its prompt tag in the meta file.
- Intake accepts CSV/XLSX with an ID column (`question_id`, `id`, `ID`) and an answer column (`answer`, `actual_answer`, `Antwort`); it stops on unknown/duplicate/missing IDs.
- Setup: `pip install -r evaluation/requirements.txt`. Older flat run files (`runs/gastbot_2026-09-29_quick.*`) stay as they are.

### Private judge (Margarita only)

`rubric.md` (version in its header) + `python scripts/eval/judge.py --run <run csv>` → `judge/<track>/<ver>__<date>.judge.csv` with the same fields as the Excel plus `needs_manual` / `manual_reason`. Model and rubric version + hash are logged in the `.judge.meta.json`. Not shared with the team. Prices, dates and counts are flagged for Supabase/manual check, never trusted. Calibrate per run: `calibrate.py sample` picks ~10 rows to score by hand, `calibrate.py compare` shows agreement and bias; then adjust the rubric and bump its version.
Gastbot vs Dify differences partly come from retrieval (website + PDFs vs Dify knowledge base), not only the prompt.
