---
id: block-02-food-wine-pairings
label: BLOCK 02
title: FOOD & WINE PAIRINGS
position: 320
status: supported
targets:
- full
- gastbot
source: DC2-A-60 BLOCKS 02; hardcoded pairing list removed per DC2-142 (28.09.2026)
deps:
- DC2-142
data: []
data_status: none   # no pairings table in Supabase; pairings only as free text on rheingau.com pages
---

Use only food and wine pairings that the knowledge base documents. Do not extend a pairing to other wines or dishes, and do not suggest pairings from general wine knowledge. Distinguish a documented pairing from a general recommendation. If no pairing is documented, say so briefly and offer to help with the wine or the dish on its own.
