-- DC2-142: 6 pages found active in rheingau_pages on 28.09.2026 that the bot must never cite.
-- Added to rheingau_excluded_registry and deleted from the search tables.
-- 22b3e6426ffe1f89 Datenschutzhinweis (legal) · 5e2f6cd458292c42 Test Integration · d0c824f1fe813856 Test (poi)
-- a2834a316a627cd2 Dankeseite · ce933766de8ae5bb Danke Projektbewertung · 84a76ef59fc2a7e2 Danke für die Meldung
insert into public.rheingau_excluded_registry (page_id, title, registry_category, exclusion_reason_original, source_url, notes, added_at)
select page_id, title,
  case when title = 'Datenschutzhinweis' then 'legal' else 'technical' end,
  case when title = 'Datenschutzhinweis' then 'Datenschutz' when title ilike 'test%' then 'Testseite' else 'Formularbestätigung' end,
  source_url, 'DC2-142: found active in rheingau_pages on 28.09.2026; deactivated so the bot never cites it', now()
from public.rheingau_pages
where page_id in ('22b3e6426ffe1f89','5e2f6cd458292c42','a2834a316a627cd2','ce933766de8ae5bb','d0c824f1fe813856','84a76ef59fc2a7e2')
on conflict do nothing;
-- Pages and their chunks are then deleted; the flag rheingau_pages.is_active was dropped (29.09.2026).
delete from public.rheingau_rag_chunks_v2 where page_id in ('22b3e6426ffe1f89','5e2f6cd458292c42','a2834a316a627cd2','ce933766de8ae5bb','d0c824f1fe813856','84a76ef59fc2a7e2');
delete from public.rheingau_pages where page_id in ('22b3e6426ffe1f89','5e2f6cd458292c42','a2834a316a627cd2','ce933766de8ae5bb','d0c824f1fe813856','84a76ef59fc2a7e2');
