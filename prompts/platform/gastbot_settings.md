# Gastbot settings for prompt-v1.0

Configuration that belongs in Gastbot, not in the prompt text. Source: Gastbot docs in YouTrack (DC2-A-112 custom system prompt, DC2-A-113 knowledge sections/RAG, DC2-A-114 Links Manager).
Status of every item: **DOCUMENTED BUT UNVERIFIED** — nobody on the team has confirmed it on the live bot yet (DC2-89, DC2-90).

## Custom system prompt

- Paste `prompts/dist/gastbot/system_prompt.md` as is. Precondition: the bot was created after 20.06.2026 (confirmed 22.09.2026, DC2-A-84).
- The prompt uses the platform variable `isFirstAssistantTurn` (module 02a). Enter it as written — the platform substitutes it.
- `followupQuestion` is **not** used in v1.0 (open decision, DC2-A-84).

## Advanced → Reply Translation

- Enable reply translation: **on**.
- Allowed reply languages: English, Dutch, Danish, Italian, French (German is always the fallback). Requirement: 6 languages DE/EN/NL/DA/IT/FR (DC2-A-1).
- Do-not-translate terms — replaces the "keep unchanged" list of CORE 04, which is not in the Gastbot build. Starter list, to extend from real conversations:
  - Dionysus, Rheingau, rheingau.com
  - Riesling, Spätburgunder, Sekt, Spätlese, Kabinett, Trocken, Halbtrocken, Feinherb
  - Kloster Eberbach, Schloss Johannisberg, Höllenberg, Gräfenberg, Kurfürstliche Burg, Brentanohaus, Abtei St. Hildegard, Freistaat Flaschenhals
  - Wisperforelle, Spundekäs', Handkäskuchen, Ringticket

## Links Manager

The prompt no longer formats links (CORE 16 link format is full-build only). Links the prompt relies on and that should exist in Links Manager:

- Newsletter signup on rheingau.com (CORE 03 redirect)
- Alkoholfreier Wein page (CORE 19 example)

## Knowledge

- V.1 scope: rheingau.com content only. How the site is loaded into Gastbot (URL import, text sections, PDF) is **UNKNOWN** — to confirm on the platform.
- No wine catalog, no SQL tools in Gastbot V.1.

## Verify on the live bot (turn each into a test case)

| Built-in | Prompt module that relies on it |
|---|---|
| German core answer + Reply Translation | CORE 04 removed |
| Links Manager placeholders | CORE 16 link format removed |
| Current time injected | CORE 10 |
| Context-only answers, no invention | CORE 06, 19 kept as fallback |
| Markdown output | CORE 17, 18 kept as fallback |
| `isFirstAssistantTurn` substitution | 02a |
