---
id: block-06b-historical-anchors
label: BLOCK 06b
title: CURATED HISTORICAL ANCHORS
position: 365
status: supported
data:
- historical_anchors
requirements:
- FR-06
- FR-11
source: DC2-A-60 BLOCKS 06 (anchor part), split per DC2-142 (28.09.2026)
deps:
- DC2-142
fields:
- historical_anchors.name
- historical_anchors.city
- historical_anchors.historical_fact
- historical_anchors.key_year
- historical_anchors.related_wine
- historical_anchors.usage_note
- historical_anchors.source_page_id
---

Curated historical and cultural anchors live in the `historical_anchors` table (name, city, category, historical fact, key year, related wine, usage note, `source_page_id` of the rheingau.com page it was verified against). Prefer an anchor when one fits the place or topic; otherwise use only historical facts from page content under BLOCK 06. Never add a fact from general knowledge, however plausible.
