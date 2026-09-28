---
id: block-01b-wine-catalog-recommendation-logic
label: BLOCK 01b
title: WINE CATALOG — RECOMMENDATION LOGIC
position: 315
status: supported
data:
- wines
- wine_dryness
data_note: dryness labels come from our normalization/enrichment formula; customer changes are added as a new mapping (decision 28.09.2026)
source: DC2-A-60 BLOCKS 01 (catalog part), split per DC2-142 (28.09.2026); dryness thresholds replaced by wine_dryness labels (normalized and enriched wine data, DC2-143)
deps:
- DC2-142
- DC2-143
---

**Dryness:** use only the dryness label from `wine_dryness` (`dryness_de` / `dryness_en`). If a wine has no label, do not assign a dryness category.

**Recommendation criteria:** use only catalog fields that are filled — dryness label, grape variety, food pairing, documented awards, vintage, alcohol content.
