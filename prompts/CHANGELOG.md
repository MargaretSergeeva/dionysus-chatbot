# Prompt changelog

## prompt-v1.2 — 28.09.2026

Start of the data-linked prompt rework (**DC2-142**): data lives in Supabase, not in prompt text. Affects all three builds.

| Module | Change | Why |
|---|---|---|
| BLOCK 02 Food & wine pairings | Hardcoded pairing list removed; rule only: use pairings the knowledge base documents | No pairings table in Supabase; data belongs in data, not in the prompt (decision 28.09.2026) |
| BLOCK 03 Alcohol-free | States that the wine catalog has no alcohol-free wines; refers to the page "Alkoholfreier Wein" (`rheingau_pages` fb6568e77028a056) | `wines` has 0 alcohol-free rows (DC2-50, DC2-77); data status none |
| compact §4 Wine, food and history | Pairing and anchor lists removed; history only from website content | Same as BLOCK 02 / BLOCK 06 |
| BLOCK 06 Storytelling | Anchor list removed; rules only; history from page content | Data in Supabase, not in the prompt; works in Gastbot via its RAG |
| BLOCK 06b Historical anchors (new, full only) | Split from BLOCK 06: prefer rows of `historical_anchors` | Gastbot cannot query the table |
| BLOCK 09 Wine finder | Food-pairing follow-up: "fixed documented pairings" → "pairings documented in the knowledge base" | Follows BLOCK 02 |

### Architecture: one prompt, builds derived from data and platform coverage

- **Data registry** `prompts/data_sources.yaml`: every Supabase table/function and platform variable, with the builds that reach it (`wines`: full, Gastbot planned).
- Every module has `data:` (sources or `general`); the gate fails on unknown sources.
- **Builds derived by the script**: a module enters a build when all its data reaches it and Gastbot does not cover it. `targets`, `allow_overlap`, `overlap_reason` and `only:` markers retired; `gastbot_covers` (conflict | duplicate, verified, reason) replaces them. Report and manifests show why a module is left out.
- **Splits**: BLOCK 01 → 01 wine description rules (both builds) + 01b catalog logic (`wines`, full only). CORE 16 → 16 URL integrity + 16b link format (conflict with Gastbot Links Manager). CORE 23 keeps only build-neutral checks.
- **Duplicates**: CORE 17 and 19 rephrased so they no longer repeat Gastbot built-ins; CORE 06 and 18 are whole-module duplicates, unverified, kept in Gastbot.
- Builds: `gastbot` loses the sweetness thresholds (BLOCK 01b, no catalog in Gastbot); otherwise same content.

Next: requirement IDs (`requirements:` per module, DC2-147).

## prompt-v1.1 — 28.09.2026

Adds a third build, **`gastbot_compact`** — a short policy version of the Gastbot prompt, written after the Gastbot recommendations DC2-A-136 (short, high-level prompt; few emphatic prohibitions; no branching logic, question classification or "remember" instructions) and DC2-A-137 (intents). `full` and `gastbot` are unchanged from prompt-v1.0.

| | `gastbot` (v1.0) | `gastbot_compact` (v1.1) |
|---|---|---|
| Size | ~24,000 chars (~6,000 tokens) | ~5,300 chars (~1,300 tokens) |
| Sections | 31 | 6 (role → sources → key rules → wine/food/history → style → missing information) |
| `Never` / `Do not` | 27 / 40 | 1 / 4 |
| Cross-references `§NN` | 24 | 0 |
| "Critical" markers | 1 | 3 (facts only from content, alcohol-free, personal data) |

- Same behaviour policy, same 100 tests: each compact module lists the v1.0 modules it replaces (`covers`); `check_test_coverage.py` counts them.
- Dropped as too fine-grained for the platform: the step-by-step answer cascade (CORE 08), the long final checklist (CORE 23 → one sentence), the duplicate-link rule (CORE 15), the retention sentence (CORE 21), the GDPR rationale (CORE 22).
- Changed on purpose: when information is missing, compact says so briefly and offers the next step. v1.0 CORE 19 item 1 forbids saying that information is missing — this contradicts the test set and DC2-A-126; the test run decides.
- Plan: run `evaluation/gastbot_v1_questions.csv` on both Gastbot builds; keep the better one, remove the other in the next version.

## prompt-v1.0 — 28.09.2026

First version under version control. Base: **DC2-A-60** as of 25.09.2026 (CORE 01–23, BLOCKS 01–09; DC2-A-69 and DC2-A-70 already merged there) plus its unmerged child articles **DC2-A-126** and **DC2-A-130**.
Not included (draft articles, not children of DC2-A-60): DC2-A-115, DC2-A-117, DC2-A-120, DC2-A-124, DC2-A-129.
Note: YouTrack article DC2-A-35 "Dionysus Prompt V.1" (18.09.2026) is an older, unrelated draft.

### Structure

- DC2-A-60 split into one module per section (`core/`, `blocks/`); human-only notes (`platform_override`, "Platform note (gastbot)", issue IDs in headings, section group headings) moved out of the prompt text into front matter.
- Two builds: `full` (Dify) and `gastbot` (DC2-91 design; targets renamed from `architecture`/`platform`).

### Text changes against DC2-A-60

| Module | Change | Why |
|---|---|---|
| CORE 03 | Removed the sentence about merge behavior ("merges regardless of which domain blocks are supported") | Build rule, not model behavior |
| CORE 04 Language | Full build only | Conflicts with Gastbot German-first answer + Reply Translation (DC2-A-112) |
| CORE 06, 17, 18, 19 | Kept in the Gastbot build with `allow_overlap` | Duplicates of Gastbot built-ins; Gastbot baseline is unverified — keep as fallback (decision 28.09.2026) |
| CORE 13 | Removed "price" from the documented comparison attributes | Contradicted BLOCK 04 (never state a price as confirmed) |
| CORE 16 | Markdown link format and raw-URL rules: full build only | Conflict with Gastbot Links Manager (DC2-A-114) |
| CORE 19 | Items 4–5 (unmatched wine name, medal year/institution) moved to BLOCK 09; "catalog entry" → "knowledge-base entry" in item 3 | Wine-catalog rules; the Gastbot build has no catalog |
| CORE 19 | Example in item 1 no longer calls +49 (0) 6723 602720 the "Rheingau Tourist Information line"; phone numbers only when documented for that exact provider | On rheingau.com this number belongs to the Rheingauer Weinbauverband / Rheingauer Weinwerbung GmbH, not to a Tourist Information (checked 28.09.2026) |
| CORE 21 | Rewritten: no deletion promise; no Supabase/DC2 references; status `partially` | No deletion mechanism exists on any platform; no conversation logs exist yet (DC2-100, DC2-101, DC2-109) |
| CORE 23 | Language and link checks split per build | Same conflicts as CORE 04 and CORE 16 |
| BLOCK 03 | Removed the named products "Reset Riesling", "Reset Riesling Sparkling"; rule now requires the knowledge base to document 0.0 % | DC2-77. The products appear on rheingau.com (6 chunks) but not in the `wines` catalog; named products in the prompt bypass grounding |
| BLOCK 06 | "Current anchors (9)" → "(10)"; `historical_anchors` table wording full build only | The list and the table hold 10 anchors; Gastbot has no database access |
| BLOCK 09 | Full build only; absorbs CORE 19 items 4–5 | Needs the `wines` catalog |
| BLOCK 10 (new) | DC2-A-126 amenity NULL rule, translated DE→EN; full build only | Staged child of DC2-A-60; needs `rheingau_pages` amenity flags (DC2-131) |
| BLOCK 11 (new) | DC2-A-130 rules 1 and 3, translated DE→EN; full build only. Rule 2 (partner/press/newsletter/jobs) held | Staged child of DC2-A-60; rule 2 is out of scope per DC2-A-1 (decision 28.09.2026) |
| 02a (new) | First-turn greeting: `isFirstAssistantTurn` in Gastbot, plain rule in full | DC2-A-84 platform baseline row "§2/§18 first-turn greeting" |

### Open

- `followupQuestion` (Gastbot) vs. CORE 12 / BLOCK 09 follow-ups — not used until decided (DC2-A-84).
- Merge `partially` modules? `gate.yaml` merges them (DC2-91 open question). Only CORE 21 is `partially`.
- Test set: CORE 10 forbids stating dates; the 18.09 test CSV (DC2-A-37) expects dates in answers — expected answers need an update.
