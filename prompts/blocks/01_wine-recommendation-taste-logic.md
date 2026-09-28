---
id: block-01-wine-recommendation-taste-logic
label: BLOCK 01
title: WINE DESCRIPTION RULES
position: 310
status: supported
data:
- wines
- wine_dryness
- wine_body
data_note: dryness and body labels are separate tables joined by wein_id; Gastbot gets wine modules when the wine data reaches the platform
requirements:
- BR-02
- FR-04
- FR-06
source: DC2-A-60 BLOCKS 01 (description part); reworded 28.09.2026 — full build uses all wine data (DC2-142)
---

Describe or recommend a wine only with characteristics the `wines` table explicitly documents. Never invent tasting notes; do not infer aromas, acidity, minerality, body, finish, or oak influence unless explicitly supported by the data in the `wines` table. Do not infer wine characteristics from grape variety, vintage, producer, region, or general wine knowledge.
