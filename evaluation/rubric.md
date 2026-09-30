---
rubric_version: rubric-v0.1
---
# Judge rubric (private — Margarita only)

The rubric is the team's Excel columns plus Rozaliia's prompt rules. The judge returns the same fields as the reviewer template, so its output and the manual review can be compared row by row. It is **not** shown to the team and is **not** a competition. The manual 50 % review still happens as agreed.

## Score — INVERTED: 1 = super, 5 = bad

| Score | Meaning |
|---|---|
| 1 | Super: correct, grounded, right scope, meets all criteria, nothing to fix |
| 2 | Good: correct; one small style/format miss |
| 3 | Okay: mostly correct but vague, padded, or one criterion missed |
| 4 | Weak: a relevant fact is missing or wrong, or several criteria missed |
| 5 | Bad: wrong or invented facts, ignores the question, or breaks a hard rule of the prompt |

Hard rules (score 4–5): invented facts; event dates/times or prices stated as confirmed (module 3.6); live status claimed (availability, traffic, weather); a `must_not_include` keyword present.

## Criteria (Rozaliia's rules)

- `check_length` — answer length is limited (guide: ≤ 120 words for a normal question; longer only if the question asks for a list or itinerary). `ok` / `fail`.
- `check_link_at_end` — the answer ends with a general link on the topic. `ok` / `fail`; `n/a` when the question is a greeting, small talk, or a refusal case where no link exists.
- `check_general_vs_specific` — a general question gets a general answer, a specific question a specific one. `ok` / `fail`.

## Reference data

Per question the judge receives `expected_behavior`, `must_include`, `must_not_include`, `source_url`, and — when filled — `expected_answer` and `key_facts` (`;`-separated facts the answer may state). Without `expected_answer`/`key_facts` the judge scores against `expected_behavior` only and says so in `judge_notes`.

## What the judge must not do

- It cannot verify **prices, dates, counts, opening hours**. It sets `needs_manual = true` with the reason, and does not score such a claim as correct just because it sounds plausible. These rows are checked against Supabase or by hand.
- It does not reward length or friendliness.
- `fix_type` (only for score ≥ 3, else empty): `prompt` = wording/format/rule of the prompt; `Vova` = Gastbot behaviour, retrieval, platform setting; `data` = missing or wrong source data; `links` = link entries.

## Caveat

A score difference between Gastbot and Dify partly comes from retrieval (one website + PDFs vs the Dify knowledge base), not only from the prompt. Compare tracks with that in mind.

## Output fields

`score`, `ideal_answer`, `fix_type`, `check_length`, `check_link_at_end`, `check_general_vs_specific`, `needs_manual`, `manual_reason`, `judge_notes` (one or two sentences).

## Changelog

- rubric-v0.1 (30.09.2026): first version; to be calibrated against ~10 manual scores per run.
