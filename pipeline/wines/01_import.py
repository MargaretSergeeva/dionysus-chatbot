#!/usr/bin/env python3
"""
Step 1 — import the wine catalog into public.wines.  PLACEHOLDER (DC2-162).

Source: die-besten-weine-hessens.de Weinfinder (JS-rendered; 763 wines, imported 21.09.2026 into public.wines,
migration create_wines_table). The original scraper is not in the repo yet — add it here when found.

Contract for this step:
- writes raw values only into public.wines (columns of migration create_wines_table), upsert on wein_id
- never touches derived columns or tables (steps 02–05 rebuild them)
"""
import sys

sys.exit("01_import.py: scraper not in the repo yet (DC2-162). Steps 02–05 run on the data already in Supabase.")
