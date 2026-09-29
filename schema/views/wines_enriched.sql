-- DC2-142: single source the bot reads for wines (applied 28.09.2026 as migration dc2_142_wines_enriched_view).
-- 29.09.2026 (migration wines_enriched_german_columns): column names = German labels on the wine page, so the
-- prompt, the Gastbot wine page and the full build use one set of names. Base tables keep their names.
-- Umlaut names are lowercase and need no quotes in Postgres. English dryness/body columns dropped (the bot translates).
-- Catalog + normalized names / grapes / types + dryness (wine_dryness) + body (wine_body), joined by wein_id.
-- security_invoker: the view uses the caller's rights, so RLS on the base tables applies.
drop view if exists public.wines_enriched;
create view public.wines_enriched
with (security_invoker = on) as
select
  w.wein_id,
  w.erzeuger          as weingut,
  w.erzeuger_id       as weingut_id,
  w.erzeuger_plz      as plz,
  w.erzeuger_ort      as ort,
  w.weinname, w.weinname_normalized, w.synonyms,
  w.jahrgang,
  w.lage_weinberg     as lage,
  w.rebsorte_normalized as rebsorte,
  w.rebsorte          as rebsorte_original,
  w.rebsorte_array,
  w.weinart_normalized as weinart,
  w.weinart           as weinart_original,
  w.qualitaetsstufe   as qualitätsstufe,
  w.praemierung       as prämierung,
  w.bewertung,
  w.restzucker_g_l, w.saeure_g_l,
  w.alkohol_pct       as alkohol,
  d.dryness_de        as geschmacksrichtung,
  d.basis             as geschmacksrichtung_basis,
  b.body_de           as körper,
  b.full_bodied       as vollmundig,
  b.basis             as körper_basis,
  b.status            as körper_status,
  w.quelle_url        as quelle
from public.wines w
left join public.wine_dryness d on d.wein_id = w.wein_id
left join public.wine_body b on b.wein_id = w.wein_id;

comment on view public.wines_enriched is
  'DC2-142: single source the bot reads for wines — catalog + normalized names/grapes/types + dryness (wine_dryness) + body (wine_body), joined by wein_id. Column names = German labels on the wine page (29.09.2026).';
