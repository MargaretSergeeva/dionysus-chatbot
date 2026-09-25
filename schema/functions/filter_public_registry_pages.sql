-- YouTrack: DC2-A-96, DC2-A-130 (staged prompt rule), issue DC2-136
--
-- Exposes only the queryable slice of rheingau_excluded_registry (DC2-134):
-- partner_area, press_area, newsletter, jobs -- decided 25.09.2026 to be real
-- content someone could legitimately ask the bot about (brochures,
-- certification, ad-code guidelines, newsletter signup, job openings).
--
-- legal / organisation / internal / technical / no_content are NEVER
-- returned by any function, on purpose -- checked case by case, genuinely
-- nothing to answer with (e.g. the "internal" Weinbauverband page is a pure
-- login gate with zero information about becoming a new member -- verified
-- via WebFetch). See DC2-A-130 Regel 3 for the full per-category rationale.
--
-- No category parameter: this function always scopes to exactly the 4
-- queryable categories, so a caller can never accidentally widen it to
-- legal/technical/etc. by passing the wrong value.

CREATE OR REPLACE FUNCTION public.filter_public_registry_pages()
RETURNS TABLE (
  page_id text,
  title text,
  registry_category text,
  source_url text,
  partner_links text
)
LANGUAGE sql STABLE AS $$
  SELECT page_id, title, registry_category, source_url, partner_links
  FROM rheingau_excluded_registry
  WHERE registry_category IN ('partner_area', 'press_area', 'newsletter', 'jobs')
  ORDER BY registry_category, title;
$$;

COMMENT ON FUNCTION public.filter_public_registry_pages() IS
  'DC2-136: the only queryable slice of rheingau_excluded_registry (DC2-134) -- partner_area,
   press_area, newsletter, jobs. legal/organisation/internal/technical/no_content are never
   returned by any function, on purpose (see DC2-A-130 Regel 3). No RAG chunks exist for any
   row here -- return title + source_url as the answer, never fabricated excerpt text.';
