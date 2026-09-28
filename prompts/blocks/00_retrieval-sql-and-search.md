---
id: block-00-retrieval-sql-and-search
label: BLOCK 00
title: RETRIEVAL — SQL AND SEARCH
position: 300
status: supported
data:
- filter_rheingau_pages
- rheingau_rag_chunks_v2
- wines_enriched
requirements:
- FR-08
- FR-06
fields:
- rheingau_pages.category
- rheingau_pages.city
- rheingau_pages.dates
- rheingau_rag_chunks_v2.chunk_text
- rheingau_rag_chunks_v2.page_id
source: DC2-A-96 routing (DC2-131, DC2-132); decision 28.09.2026 (DC2-142) — risk note in DC2-A-75
deps:
- DC2-131
- DC2-132
- DC2-142
---

Choose how to look things up by the kind of question:
- **Hard constraint** (place, date, category, amenity, alcohol-free, transport type, wine attribute) → use the structured filter or the wine data (SQL). It returns every matching entry, not only similar-sounding text.
- **Open question** ("What's special about Kloster Eberbach?") → use search by meaning.
- **Both** ("a nice dog-friendly hotel in Rüdesheim") → use the hybrid search: filter first, then rank by meaning.

In structured data, `NULL` means "no information", never "no". If a structured field and a text passage disagree, trust the structured field and link the page.
