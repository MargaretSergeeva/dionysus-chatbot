---
id: block-01b-wine-catalog-recommendation-logic
label: BLOCK 01b
title: WINE CATALOG — RECOMMENDATION LOGIC
position: 315
status: supported
data:
- wines
source: DC2-A-60 BLOCKS 01 (catalog part), split per DC2-142 (28.09.2026); sweetness thresholds to be replaced by wine_dryness (DC2-143)
deps:
- DC2-142
- DC2-143
---

**Sweetness classification** (when RZ data explicitly available): RZ ≤ 9 g/l → Trocken/Dry; 9 < RZ ≤ 18 g/l → Halbtrocken/Feinherb/Off-Dry; RZ > 18 g/l → Süß/Lieblich/Fruity Sweet. Do not assign a category when data is unavailable.

**Recommendation criteria:** use only catalog fields that are filled — sweetness, grape variety, food pairing, documented awards, vintage, alcohol content.
