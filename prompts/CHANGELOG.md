# Prompt changelog

## prompt-v1.2 — 28.09.2026

Start of the data-linked prompt rework (**DC2-142**): data lives in Supabase, not in prompt text.

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

### Decisions 28.09.2026 (evening)

- **Duplicates of Gastbot built-ins are left out of the Gastbot build**, like conflicts (`verified` retired). Leaving them out is the live test of the built-in; if it fails, remove `gastbot_covers`. CORE 06 and 18 leave the Gastbot build; CORE 01 and 19 no longer reference §06.
- **Sweetness thresholds removed everywhere.** BLOCK 01b and BLOCK 09 use the dryness label from `wine_dryness` (normalized and enriched wine data, DC2-143). Customer changes to the formula come in as a new mapping.
- **`gastbot_compact` dropped** (modules, build, CI, docs). Recreate it from git history when the main prompt is ready.

- **CORE 02b AI disclosure** (new): the first greeting says Dionysus is an AI assistant (EU AI Act Art. 50, DC2-98).
- **CORE 10 Dates**: dates help to find, never to confirm; no past events; guest checks dates and prices on the page.
- **CORE 17**: recommendation list item = name — summary — link.
- **BLOCK 04 Price → CORE 10b, BLOCK 05 Booking → CORE 10c**: general rules without data dependency (FR-12, time-sensitive facts). CORE 03 reference updated; the reference check now covers suffixes (§10c, Block §06b).

- **Wine data**: view `wines_enriched` (wines + dryness + body) is the single wine source. BLOCK 01, 01b and 09 merged into **BLOCK 01 Wines** (description, field table, recommendation criteria, follow-ups, unmatched name, award year). Body only when "Vollmundig"; sugar/acid as numbers only on request.
- **Food pairing removed completely** (BLOCK 02 deleted; also out of the wine follow-ups and the CORE 08 intent list) — no data, no requirement. Test GB1-056 reworked.
- **Test coverage check** fixed for derived builds (it read the retired `targets`); test codes remapped (B04→C10b, B05→C10c, B09→B01, C06/C18→PLATFORM); new test GB1-101 for AI disclosure. A test for a module outside the checked build no longer fails.
- **Data sources**: `rheingau_rag_chunks_v2` (what the bot reads) separated from `rheingau_pages` (what it filters by). Old `rheingau_rag_chunks` (no embeddings) and view `rheingau_rag_context` dropped in Supabase; backup `archive.rheingau_rag_chunks_20260928`.
- **CORE 22**: "documented alcohol-free offers"; GDPR Art. 9 rationale moved to the CR-03 note.
- **`alcohol_free_offer`** flag added to `rheingau_pages` and both filter functions (empty until the page review is done).
- **BLOCK 03 Alcohol-free** (both builds, RAG): website pages only, "Alkoholfreier Wein" first, then other documented offers. **New BLOCK 03b** (full): exact filter `alcohol_free_offer = true`; 29 pages tagged after review.
- **Rule: what CORE says is not repeated in blocks** (decision 28.09.2026). BLOCK 06: "no live sourcing" removed (CORE 01/05/06/19). BLOCK 06b: maintenance sentence moved to the `historical_anchors` note in the registry.
- **BLOCK 07 Transport**: covers arrival, ferries, boats, cable cars, parking, camper stops; prefers specific transport pages; transport for an offer only if its page mentions it. CORE repetitions removed.
- **New BLOCK 07b** (full): transport filter by `transport_type` (71 reviewed pages: info, station, ferry, boat_landing, cable_car, parking, camper_stop, ebike_charging, taxi); city fixed for 7 pages.
- **CORE 14 Recommendations** = old CORE 14 + BLOCK 08 + DC2-A-146 + DC2-A-120 (large result sets): vague request → suggest directions; many matches → name the volume, max. two narrowing questions (activities: place/kind/stay; wines: dryness, then type/grape); options as in §09; connect and combine. BLOCK 08 deleted. CORE 09: 2–3 → 3–5 options.
- **BLOCK 10 Amenities**: "for accommodations" only (no flags elsewhere); empty flags breakfast_included, group_friendly, wheelchair_accessible removed from the list until filled (DC2-151).
- **BLOCK 11 Regional projects**: completion only as the page states it, older timelines flagged; "pages never cited" removed from the prompt — fixed in the data instead: 6 test/legal/confirmation pages deactivated and added to `rheingau_excluded_registry`; `match_rheingau_chunks` now returns only active pages.
- **Past events/experiences skipped in the data**: all three search functions skip events and experiences whose last date (`page_last_date(dates)`) is before today — a safety net for CORE 10; nothing deactivated, updated dates come back by themselves. On 28.09.2026: 41 events + 7 experiences hidden.
- **FR-07 removed** (conditional statements keep their exception): it was a chunking risk (DC2-A-75), not a requirement, and is already covered by the chunk rework (`rheingau_rag_chunks_v2`).
- **`fields:`** on every data module (Supabase `table.field`, metadata only — not in the prompt text); the gate checks each field against `data_sources.yaml`; the status report shows a "Supabase fields" column first.
- **Text pass (conciseness):** CORE 04 Language ~330 → ~80 words (any language, names unchanged); CORE 02 repeated sentence removed; CORE 03 rationale moved to the CR-01 note; FR-01 note on languages per build.
- **CORE 08 (answer cascade) deleted**: its steps were already in CORE 07, 15, 17, 19, 23 (and DC2-A-136 advises against step-by-step logic); "answer the actual question first" moved to **CORE 17**, link preference order to **CORE 15**; tests C08 → C17. **FR-03** reworded (link only where the answer has a source) and merged with **CR-05** (removed).
- **New BLOCK 00 Retrieval — SQL and search** (full): constraint questions → filter/SQL, open → search by meaning, both → hybrid; `NULL` = no information; structured field wins over text; no merging facts across pages. **FR-08** widened accordingly. BLOCK 03b trimmed to its field mapping.
- **One grounding rule: CORE 05 Grounding** (CORE 05 + 06 merged; 06 deleted): only the knowledge base provided; no internet, training or general/regional knowledge to fill gaps; else §19. The general "don't invent / only the knowledge base" wording removed from CORE 00, 13, 19, 23, 10b and BLOCK 01, 06 — their specific rules stay. "Prefer facts about the exact entity" added to CORE 07. CORE 05 stays in the Gastbot build (short, no platform-duplicate wording).
- **CORE 07 Entities** shortened to 3 rules (~60 words): ask when ambiguous; no facts moved between entities; no substitution by a similar entity. Synonym matching and "no new entities" dropped (search and CORE 05 cover them). Matching sentence removed from BLOCK 00.
- **CORE 19 Missing information** rewritten: say briefly that a detail is missing (no stock error phrases) and offer the next step — page, documented contact, or 3–5 documented alternatives. Resolves the contradiction with BLOCK 10 / CORE 14 (old rule: never say it is missing). Unmatched entities → CORE 07.
- **Missing-information repetitions removed** (CORE 19 covers the behaviour): CORE 10, 10b, 11 lines deleted; BLOCK 01 §6, 07b, 10 rule 2, 11 shortened to their specific part.
- **CORE 09 Recommendations & comparisons** = CORE 09 + CORE 13 merged (~65 words): no winner for taste questions unless the data states one; 3–5 options without ranking; compare only on documented facts. CORE 13 deleted; tests C13 → C09.
- **CORE 10 Dates, prices & booking** = CORE 10 + 10b + 10c merged (~110 words); 10b, 10c deleted; tests and the CORE 03 reference point to CORE 10.
- **CORE 11 Practical information** deleted: its list of useful details moved into CORE 17 (now "Answer format & lists"); the rest was CORE 05 / 17 repetition. Tests C11 → C17.
- **CORE 12 Follow-ups** shortened (~40 words); ambiguity rule is in CORE 07; CORE 23 continuity check removed.
- **No cross-references (§NN) in the prompt text** (DC2-A-136 advice; clearer for the model): CORE 01 Priorities rewritten as a plain order; CORE 05, 14, 15, 22, BLOCK 10 say the rule inline; CORE 21 meta sentence removed. CORE 14 tightened (vague and large requests merged, narrowing said once).
- **CORE 15 Links** = CORE 15 + 16 merged (only links from the knowledge base, exactly as given; most specific page; each URL once); CORE 16 deleted, tests C16 → C15. CORE 16b trimmed to one line.
- **CORE 17 Answer format, lists & links**: CORE 15 Links merged in (only knowledge-base links, exactly as given; page most specific to the question; each URL once); CORE 15 deleted, tests C15 → C17. BLOCK 07, CORE 19, CORE 23 unchanged (decision 29.09.2026).
- **CORE 20 Complaints** shortened (~45 words), example with placeholders; refund rule kept in both CORE 10 and 20 (different situations).
- **CORE 03**: new first line "Never ask for or encourage personal data" (moved from CORE 21); consent background moved to the CR-02 note.
- **FR-13 new** (29.09.2026): legal/privacy, newsletter, partner, press and job questions are in scope — answered from the matching pages with a link (the 12 pages must be loaded from the excluded registry). BLOCK 11 rule 2 dropped. CORE 21 deletion answer now links the Datenschutz page (https://www.rheingau.com/datenschutz, from the registry, not yet checked live).
- **CORE 21 Chat logging** shortened (~55 words): never ask permission, saved to improve the service, no deletion (link to the data protection page), no retention period. Consent explanation moved out of the prompt into new requirement **CR-06** (met in the frontend, DC2-101).
- **CORE 16b Markdown format** = CORE 16b (link format) + CORE 18 merged (full build only; Gastbot formats answers and links itself); CORE 18 deleted.
- **CORE 22 Health context** shortened (~40 words); "no follow-up questions about the condition" kept.
- **CORE 22 Health context** shortened (~40 words): just answer the question; no follow-up questions about the condition, no health advice, no comment on the health context (a neutral "Gern" is fine). Consent-flow sentence dropped (rationale in the CR-03 note).
- **CORE 16b renamed 17b** (Markdown format, full build only) and placed right after CORE 17 — it stays a separate module because Gastbot formats answers and links itself (decision 29.09.2026).
- **CORE 14 Recommendations** now includes CORE 09 ("best/cheapest": no single winner, compare on documented facts, scores only as the data states them); CORE 09 deleted, tests C09 → C14.
- **CORE 14 Recommendations moved** to directly after CORE 07 Entities (position only; label unchanged).
- **Core** deleted CORE 01 Priorities; dropped "Never ask permission to save the chat" from CORE 21 (covered by CR-02 / CR-06 notes)
- **Blocks** BLOCK 03 Alcohol-free shortened (~150 to ~100 words, same rules)
- **Core** CORE 23 Intent check shortened (categories and overrides were covered by CORE 10 / 17 and BLOCK 03)
- **Core/Blocks** CORE 10: removed price-total sentence and the booking-page sentence, shortened booking rule; BLOCK 00: "transport type" removed from the hard-constraint list
- **Core** CORE 14: narrowing limited to two questions, guest sets how far; concrete requests with many matches: show 3-5, say there is a lot, offer to narrow with available filters
- **Core** CORE 07 Entities rewritten as one paragraph: ambiguity question only for fact/link requests about a specific item; no 'entity' jargon
- **Blocks** BLOCK 01 point 1 shortened (~60 to ~30 words, same rules)
- **Blocks** BLOCK 01: point 6 (award year and institution) removed; the award row in the field table already says medal level and points
- **Blocks** BLOCK 06 Storytelling: purpose and moment stated (one short story about a sight, winery or tasting stand in the same place, with link); facts only from retrieved pages; BLOCK 06b cross-reference removed
- **Core** CORE 23 checks reordered (alcohol-free safety first, then intent, entity, recommendations, links, language, relevance)
- **Structure** modules regrouped into sections that follow Gastbot's prompt recommendations (DC2-A-136): 1 Role · 2 Sources & data · 3 Key rules · 4 Behavior · 5 Style & format · 6 Final check. Labels are now `section.module` (e.g. 3.3); files live in `prompts/modules/<section>/`; the assembler writes a section heading before the first module of each section (`prompts/sections.yaml`); test-question codes and requirement notes remapped; module ids unchanged
- **Structure** historical anchors moved next to storytelling (2.9 → 4.4); missing information 2.10 → 2.9; complaints 4.4 → 4.5
- **Requirements** `prompts/requirements.yaml` (DC2-147): BR / FR / CR / QR IDs; every module lists `requirements:`; the gate fails on missing or unknown IDs; the status report shows requirement → modules → builds. 

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
