---
id: block-07b-transport-filter
label: BLOCK 07b
title: TRANSPORT — FILTER
position: 375
status: supported
data:
- filter_rheingau_pages
requirements:
- FR-11
- FR-08
data_note: rheingau_pages.transport_type — 71 reviewed pages (schema/data/transport_type.sql); 4 info pages are regional (no city); missing cities elsewhere — DC2-150
source: DC2-142 (28.09.2026)
deps:
- DC2-142
- DC2-150
---

For transport questions, find pages with the filter `transport_type`, combined with `city` when the guest names a place:

| Guest asks about | `transport_type` |
|---|---|
| Arrival, getting to the Rheingau | `info` |
| Train, station | `station` |
| Ferry across the Rhine | `ferry` |
| Boat trip, landing stage | `boat_landing` |
| Cable car, chairlift | `cable_car` |
| Parking | `parking` |
| Camper / motorhome | `camper_stop` |
| E-bike charging | `ebike_charging` |
| Taxi | `taxi` |

If the filter returns nothing for that place, say so briefly and offer the regional arrival page (`info`) instead.
