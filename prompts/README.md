# Dionysus — system prompt modules

Source of truth for the Dionysus chatbot system prompt. The prompt is built from small modules, not edited as one document.
Process: YouTrack **DC2-A-95** (Prompt Iterative Assembly). Traceability: **DC2-A-84**. Structure: **DC2-A-50**. Tasks: **DC2-91**, **DC2-122**.

Until prompt-v1.0 the live prompt lived only in YouTrack (**DC2-A-60** + child articles). From prompt-v1.0 on, this folder is the source of truth; DC2-A-60 links here.

## Two builds from one set of modules

| Build | Used by | Includes |
|---|---|---|
| `full` | our own stack — Dify (Plan B) | every merged module, incl. language rules, wine catalog (`wines`), SQL tool rules |
| `gastbot` | Gastbot custom system prompt field | only modules targeted at Gastbot; linted against `platform/gastbot_baseline.yaml` |

Gastbot V.1 scope: rheingau.com content through Gastbot's own RAG only — no wine catalog, no SQL filters.
A module leaves the Gastbot build only when it **conflicts** with Gastbot (answer language, link formatting).
Harmless **duplicates** of Gastbot built-ins stay in (`allow_overlap`) until a live test proves Gastbot provides them — the Gastbot baseline is documented, not verified (decision 28.09.2026).

## Layout

```
prompts/
  VERSION                     current prompt version (git tag prompt-vX.Y)
  gate.yaml                   which statuses merge; which build is linted how
  core/                       CORE 01–23 — platform-independent behavior (§23 is always last)
  blocks/                     BLOCK 01–11 — domain and data-dependent rules
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
id: core-04-language           # unique
label: '04'                    # heading label: '04' (core), 'BLOCK 03' (block), '02a' (adapter)
title: LANGUAGE
position: 40                   # order in the assembled prompt
status: supported              # supported | partially | blocked | unknown | draft
targets: [full]                # builds that include the module
source: DC2-A-60 CORE 04       # where the text comes from
deps: []                       # YouTrack issues the data depends on
allow_overlap: []              # Gastbot built-ins repeated on purpose
overlap_reason: ''             # required with allow_overlap
```

Text for one build only: `<!-- only:gastbot --> … <!-- /only -->` or `<!-- only:full --> … <!-- /only -->`.
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
5. After merge, a release is a tag: `git tag prompt-vX.Y && git push origin prompt-vX.Y` — CI attaches both prompts to a GitHub Release.

## Deploy

- **Gastbot:** paste `prompts/dist/gastbot/system_prompt.md` into the custom system prompt field; apply `platform/gastbot_settings.md`.
- **Dify:** `prompts/dist/full/system_prompt.md` is the system prompt; the smoke test (`.github/workflows/dify-smoke-test.yml`) sends it on every push to `main`.
