-- DC2-142 (28.09.2026): last date listed on a page. rheingau_pages.dates is text like
-- "04.12.2026 | 05.12.2026 | 06.12.2026"; returns the latest valid DD.MM.YYYY, NULL if none.
-- Used by the search functions to skip events/experiences whose last date is before today
-- (CORE 10: no past events). Nothing is deactivated; a page with updated dates comes back by itself.
CREATE OR REPLACE FUNCTION public.page_last_date(p_dates text)
RETURNS date LANGUAGE sql IMMUTABLE AS $$
  SELECT max(to_date(trim(x), 'DD.MM.YYYY'))
  FROM unnest(string_to_array(p_dates, '|')) AS x
  WHERE trim(x) ~ '^\d{2}\.\d{2}\.\d{4}$';
$$;

-- Condition added to filter_rheingau_pages, match_rheingau_chunks, match_rheingau_chunks_filtered:
--   AND (rp.category NOT IN ('event','experience')
--        OR public.page_last_date(rp.dates) IS NULL
--        OR public.page_last_date(rp.dates) >= current_date)
