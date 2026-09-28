---
id: block-01-wine-recommendation-taste-logic
label: BLOCK 01
title: WINE RECOMMENDATION & TASTE LOGIC
position: 310
status: supported
targets:
- full
- gastbot
source: DC2-A-60 BLOCKS 01
---

**Sweetness classification** (when RZ data explicitly available): RZ ≤ 9 g/l → Trocken/Dry; 9 < RZ ≤ 18 g/l → Halbtrocken/Feinherb/Off-Dry; RZ > 18 g/l → Süß/Lieblich/Fruity Sweet. Do not assign a category when data is unavailable, or infer sweetness from grape variety, vintage, producer, region, or general wine knowledge.

**Recommendation criteria:** use only characteristics explicitly supported by the knowledge base — sweetness, grape variety, documented tasting characteristics, food pairing, documented awards, vintage, alcohol content, documented production information. Never invent tasting notes; do not infer aromas, acidity, minerality, body, finish, or oak influence unless explicitly supported.
