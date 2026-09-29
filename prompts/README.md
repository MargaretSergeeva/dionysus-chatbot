# Dionysus — system prompt modules

Source of truth for the Dionysus chatbot system prompt. The prompt is built from small modules, not edited as one document.
Process: YouTrack **DC2-A-95** (Prompt Iterative Assembly). Traceability: **DC2-A-84**. Structure: **DC2-A-50**. Tasks: **DC2-91**, **DC2-122**.

Until prompt-v1.0 the live prompt lived only in YouTrack (**DC2-A-60** + child articles). From prompt-v1.0 on, this folder is the source of truth; DC2-A-60 links here.

## One prompt, two builds

The main prompt is one set of modules (`core/`, `blocks/`, `adapters/`). The script derives two builds from it. The short Gastbot build (`gastbot_compact`, prompt-v1.1) was dropped in prompt-v1.2; recreate it from git history once the main prompt is ready.

| Build | Used by | Gets a module when |
|---|---|---|
| `full` | our own stack — Dify + Supabase (Plan B) | all its `data` reaches `full` |
| `gastbot` | partner platform Gastbot, custom system prompt field | all its `data` reaches `gastbot` **and** Gastbot does not already do it (`gastbot_covers`) |

**Two reasons a module is left out of Gastbot** — both shown in `dist/status_report.md` and the manifests:
- **Data not available** — `prompts/data_sources.yaml` lists which build reaches which data. Gastbot has rheingau.com through its own RAG, but no Supabase tables yet. When a table reaches Gastbot (e.g. the wine catalog is uploaded to the platform), move `gastbot` from `planned` to `builds` — the modules follow, no text changes.
- **Platform-covered** — `gastbot_covers.relation: conflict` (Gastbot does it differently: answer language, link format, greeting) → never in Gastbot. `relation: duplicate` (Gastbot does the same) → also never in Gastbot: leaving it out is how the live test shows whether Gastbot really provides it. If the test fails, remove `gastbot_covers` and the module goes back in (decision 28.09.2026).

**Naming convention.** Prompt text never names tables, views or functions — they differ per build (Gastbot has its own RAG and, later, an uploaded wine table). It says what the data is in words ("the wine data", "the structured filter"). The physical names live in the module header (`data`, `fields`) and in `data_sources.yaml`. Column names may appear in rule tables: they are the shared contract, so a wine upload to Gastbot keeps the column names of `wines_enriched`. The gate fails when a module text names a registered table, view or function.

**No build-specific text inside a module.** If only part of a module is covered by Gastbot, split the module (e.g. answer format and link rules 5.1 + Markdown format 5.2). The script rejects `only:` markers.

## Layout

```
prompts/
  VERSION                     current prompt version (git tag prompt-vX.Y)
  gate.yaml                   which statuses merge; which build is linted how
  requirements.yaml           requirement IDs (BR/FR/CR/QR) — machine-readable list behind DC2-A-84
  data_sources.yaml           data registry: Supabase tables/functions + platform data, and which build reaches them
  sections.yaml               section names (label '2.4' = section 2, module 4)
  modules/
    0-preamble/               unlabeled start of the prompt
    1-role/                   1.x role, greeting, AI disclosure, language
    2-sources/                2.x sources & data: grounding, entities, retrieval, wines, transport, amenities, regional projects, missing information
    3-key-rules/              3.x PII, health, alcohol-free (safety + filter), chat logging, dates/prices/booking
    4-behavior/               4.x recommendations, follow-ups, storytelling, historical anchors, complaints
    5-style-format/           5.x answer format, Markdown
    6-final-check/            6 final response check (always last)
  adapters/gastbot/           Gastbot-only text (platform variables)
  adapters/dify/              full-build equivalents of Gastbot-only text
  platform/gastbot_baseline.yaml   Gastbot built-ins + conflict patterns
  platform/gastbot_settings.md     Gastbot settings that are configuration, not prompt text
  dist/                       generated — never edit by hand
    full/system_prompt.md, full/manifest.json
    gastbot/system_prompt.md, gastbot/manifest.json
    status_report.md
```

## Module front matter

```yaml
id: core-04-language           # unique, stable, never renumbered
title: LANGUAGE
status: supported              # supported | partially | blocked | unknown | draft
data: [rheingau_pages]         # Supabase tables/views from data_sources.yaml, or `general`
via: [filter_rheingau_pages]   # optional: Supabase functions the full build calls to read that data
fields: [rheingau_pages.city]  # table.field the module uses (required when data is a table/view)
requirements: [FR-01]          # IDs from requirements.yaml, at least one
issues: [DC2-131, DC2-A-96]    # YouTrack issues / articles connected to this module only
gastbot_covers:                # only if Gastbot already does this
  relation: conflict           # conflict | duplicate
  builtins: [response_language]  # keys from platform/gastbot_baseline.yaml the text repeats
  reason: Reply Translation (DC2-A-112)
```

The label and the order come from the **file name**: `2.8_regional-projects.md` is module 8 of section 2 (`position = 2*1000 + 8*10`;
`adapters/dify` adds 1; `00_` is the preamble; `6_` the final check). Where a module's text comes from and its data notes are in
`CHANGELOG.md`, "Module history". `via` documents which function the full build calls; it does not decide which build gets the module (`data` does).

Builds are never written by hand. `targets`, `allow_overlap`, `overlap_reason` and `only:` markers are retired (DC2-142).
References such as `§19` or `Block §03` are checked: a build fails if it references a module it does not include.

## Commands

```bash
pip install -r requirements.txt
python scripts/assemble_prompt.py check     # gate + Gastbot lint + reference check
python scripts/assemble_prompt.py build     # write prompts/dist/
python scripts/assemble_prompt.py verify    # CI: fail if prompts/dist is stale
```

## Change a module

1. Create a branch `feature/DC2-<id>-<slug>` from the YouTrack issue.
2. Edit the module (or add one). Update DC2-A-84 when a data status changes.
3. Run `build`, commit the modules **and** `prompts/dist/`, reference the issue in the commit message.
4. Open a PR. CI (`Prompt gate & build`) must pass.
5. After merge, a release is a tag: `git tag prompt-vX.Y && git push origin prompt-vX.Y` — CI attaches all three prompts to a GitHub Release.

## Deploy

- **Gastbot:** paste `prompts/dist/gastbot/system_prompt.md` into the custom system prompt field; apply `platform/gastbot_settings.md`. Advanced routing stays off (RAG only).
- **Dify:** `prompts/dist/full/system_prompt.md` is the system prompt; the smoke test (`.github/workflows/dify-smoke-test.yml`) sends it on every push to `main`.
