-- 01.10.2026 (Margarita): Lage values from the competition data end in " -" when a wine has only a
-- village and no vineyard site ("Heppenheim -", "Hattenheim -", "Steinberg -"). Strip the trailing dash, keep the village.
-- 74 rows. Wine names keep their " - " (official names from the source).
-- Backup of the old values: archive.wines_lage_20261001 (wein_id, lage_weinberg).
-- Re-runnable: rows without a trailing dash are untouched.
create schema if not exists archive;
create table if not exists archive.wines_lage_20261001 as
  select wein_id, lage_weinberg from public.wines where lage_weinberg ~ '\s*-\s*$';

update public.wines
set lage_weinberg = nullif(regexp_replace(lage_weinberg, '\s*-\s*$', ''), '')
where lage_weinberg ~ '\s*-\s*$';
