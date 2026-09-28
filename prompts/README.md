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

**No build-specific text inside a module.** If only part of a module is covered by Gastbot, split the module (e.g. CORE 16 → 16 URL integrity + 16b link format). The script rejects `only:` markers.

## Layout

```
prompts/
  VERSION                     current prompt version (git tag prompt-vX.Y)
  gate.yaml                   which statuses merge; which build is linted how
  data_sources.yaml           data registry: Supabase tables/functions + platform data, and which build reaches them
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
data: general                  # or a list of sources from data_sources.yaml, e.g. [wines]
data_note: ''                  # optional: data gaps worth knowing
gastbot_covers:                # only if Gastbot already does this
  relation: conflict           # conflict | duplicate
  builtins: [response_language]  # keys from platform/gastbot_baseline.yaml the text repeats
  reason: Reply Translation (DC2-A-112)
source: DC2-A-60 CORE 04       # where the text comes from
deps: []                       # YouTrack issues the data depends on
```

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
