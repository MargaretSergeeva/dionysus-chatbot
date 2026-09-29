-- DC2-142: single source the bot reads for wines (applied 28.09.2026 as migration dc2_142_wines_enriched_view).
-- Catalog + normalized names / grapes / types + dryness (wine_dryness) + body (wine_body), joined by wein_id.
-- security_invoker: the view uses the caller's rights, so RLS on the base tables applies.
create or replace view public.wines_enriched
with (security_invoker = on) as
select
  w.wein_id,
  w.erzeuger, w.erzeuger_id, w.erzeuger_plz, w.erzeuger_ort,
  w.weinname, w.weinname_normalized, w.synonyms,
  w.jahrgang,
  w.lage_weinberg,
  w.rebsorte, w.rebsorte_normalized, w.rebsorte_array,
  w.weinart, w.weinart_normalized,
  w.qualitaetsstufe,
  w.praemierung, w.bewertung,
  w.restzucker_g_l, w.saeure_g_l, w.alkohol_pct,
  d.dryness_de, d.dryness_en, d.basis as dryness_basis,
  b.body_de, b.body_en, b.full_bodied, b.basis as body_basis, b.status as body_status,
  w.quelle_url
from public.wines w
left join public.wine_dryness d on d.wein_id = w.wein_id
left join public.wine_body b on b.wein_id = w.wein_id;

comment on view public.wines_enriched is
  'DC2-142: single source the bot reads for wines — catalog + normalized names/grapes/types + dryness (wine_dryness) + body (wine_body), joined by wein_id.';
