# Gastbot settings for prompt-v1.0 / v1.1

Configuration that belongs in Gastbot, not in the prompt text. Source: Gastbot docs in YouTrack (DC2-A-112 custom system prompt, DC2-A-113 knowledge sections/RAG, DC2-A-114 Links Manager, DC2-A-136 model recommendations, DC2-A-137 intents/routing — the last two added 28.09.2026).
Status of every item: **DOCUMENTED BUT UNVERIFIED** — nobody on the team has confirmed it on the live bot yet (DC2-89, DC2-90).

## Custom system prompt

- Paste `prompts/dist/gastbot/system_prompt.md` as is. Precondition: the bot was created after 20.06.2026 (confirmed 22.09.2026, DC2-A-84).
- The prompt uses the platform variable `isFirstAssistantTurn` (module 02a). Enter it as written — the platform substitutes it.
- `followupQuestion` is **not** used in v1.0 (open decision, DC2-A-84).

## Advanced → Reply Translation

- Enable reply translation: **on**.
- Allowed reply languages: English, Dutch, Danish, Italian, French (German is always the fallback). Requirement: 6 languages DE/EN/NL/DA/IT/FR (DC2-A-1).
- Do-not-translate terms — replaces the "keep unchanged" list of module 1.4 (Language), which is not in the Gastbot build. Starter list, to extend from real conversations:
  - Dionysus, Rheingau, rheingau.com
  - Riesling, Spätburgunder, Sekt, Spätlese, Kabinett, Trocken, Halbtrocken, Feinherb
  - Kloster Eberbach, Schloss Johannisberg, Höllenberg, Gräfenberg, Kurfürstliche Burg, Brentanohaus, Abtei St. Hildegard, Freistaat Flaschenhals
  - Wisperforelle, Spundekäs', Handkäskuchen, Ringticket

## Links Manager

The prompt no longer formats links (the link format in module 5.2 is full-build only). Links the prompt relies on and that should exist in Links Manager:

- Newsletter signup on rheingau.com (module 3.1 redirect)
- Alkoholfreier Wein page (module 2.9 example)

## Intents / Advanced routing (DC2-A-137)

- V.1 scope is RAG only → **Advanced routing: off**. Only the Default intent is used; its prompt is the custom system prompt above.
- Gastbot supports a **Tools intent** (tools, integrations, databases, live data) selected by advanced routing. It has its **own system prompt**; the main system prompt is **not** added to it. A future tools build (wine finder, amenity/city filters via Supabase) therefore needs a separate, self-contained prompt that repeats the essential core rules (persona, grounding, PII, alcohol-free, price/date rules).
- Which tool types Gastbot can call (HTTP/REST, database connectors) is **UNKNOWN** — to confirm before planning V.2 on Gastbot.
- Detection descriptions (when to pick Default vs Tools) describe *when*, not *how to answer*.

## Prompt size and style (DC2-A-136)

The platform recommends a short, high-level prompt: role, sources, key limits, style, fallback; few emphatic prohibitions; no branching logic, question classification or "remember" instructions; strict logic belongs to the platform. prompt-v1.0 `gastbot` is ~24,000 characters with 67 prohibitions (`Never`/`Do not`), 45 conditions and 24 cross-references — **well above that guidance**. prompt-v1.1 had a short build `gastbot_compact` (~5,300 characters); dropped in prompt-v1.2 until the main prompt is ready — recreate it then from git history (tag/commit before DC2-142).

## Knowledge

- V.1 scope: rheingau.com content only. How the site is loaded into Gastbot (URL import, text sections, PDF) is **UNKNOWN** — to confirm on the platform.
- No wine catalog, no SQL tools in Gastbot V.1.
- Knowledge quality matters more than the prompt (DC2-A-136): one topic per section, short explicit facts, critical facts in text sections (not only PDF). Option: export the curated `rheingau_pages` (one page = one section) from Supabase into Gastbot, so both bots use the same cleaned data.

## Verify on the live bot (turn each into a test case)

| Built-in | Prompt module that relies on it |
|---|---|
| German core answer + Reply Translation | module 1.4 removed |
| Links Manager placeholders | module 5.2 removed |
| Current time injected | module 3.6 |
| Context-only answers, no invention | modules 2.1, 2.9 kept as fallback |
| Markdown output | module 5.1 kept as fallback |
| `isFirstAssistantTurn` substitution | 02a |
