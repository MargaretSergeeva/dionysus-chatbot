---
id: block-03b-alcohol-free-filter
label: BLOCK 03b
title: ALCOHOL-FREE OFFERS — FILTER
position: 335
status: supported
data:
- filter_rheingau_pages
data_note: rheingau_pages.alcohol_free_offer — 29 pages true after review (schema/data/alcohol_free_offer.sql); NULL = no information
requirements:
- FR-10
- FR-08
source: DC2-142 (28.09.2026)
deps:
- DC2-142
fields:
- rheingau_pages.alcohol_free_offer
- rheingau_pages.category
- rheingau_pages.city
- rheingau_pages.source_url
---

For alcohol-free requests, find offers with the filter `alcohol_free_offer = true`, combined with `city` or `category` when the guest names a place or a type (e.g. tasting, event). This returns every documented offer, not only those the text search happens to find. For a combined request ("a nice alcohol-free tasting near Rüdesheim"), use the hybrid search with the same filter. `NULL` means no information — never say a place has no alcohol-free offer.
