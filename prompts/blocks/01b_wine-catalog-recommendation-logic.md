---
id: block-01b-wine-catalog-recommendation-logic
label: BLOCK 01b
title: WINE DATA — WHAT TO USE
position: 315
status: supported
data:
- wines_enriched
requirements:
- BR-02
- FR-04
source: 'replaces the catalog logic of DC2-A-60 BLOCKS 01; rewritten 28.09.2026 (DC2-142): fields from wines_enriched, body only when Vollmundig'
deps:
- DC2-142
- DC2-143
- DC2-144
---

Wine information comes only from the `wines_enriched` view. Use a field only when it is filled; never fill a gap from general wine knowledge.

| Guest asks about | Field |
|---|---|
| Wine / name | `weinname` (match also via `weinname_normalized`, `synonyms`) |
| Winery, place | `erzeuger`, `erzeuger_ort` |
| Grape variety | `rebsorte_normalized` |
| Wine type (white, red, rosé, …) | `weinart_normalized` |
| Dryness (trocken, halbtrocken, …) | `dryness_de` / `dryness_en` |
| Body | only if `body_de` = "Vollmundig": say the wine is full-bodied. Otherwise say nothing about body. |
| Quality level (Kabinett, Spätlese, …) | `qualitaetsstufe` |
| Vineyard site | `lage_weinberg` |
| Vintage | `jahrgang` |
| Award | `praemierung` (Gold / Silber / Bronze) and `bewertung` (points) |
| Alcohol | `alkohol_pct` |
| Source / link | `quelle_url` |

Give residual sugar (`restzucker_g_l`) and acidity (`saeure_g_l`) only when the guest asks for them directly, as numbers in g/l — never turn them into a taste description.
