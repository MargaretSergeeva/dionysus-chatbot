-- DC2-152: public pages that are not in the search data (rheingau_pages / chunks)
-- but that the bot may point to by title and link: partner area, press, newsletter,
-- jobs and the legal pages (Impressum, Datenschutz). The frag-lisbeth Datenschutzhinweis
-- is excluded on purpose.
CREATE OR REPLACE FUNCTION public.filter_public_registry_pages()
 RETURNS TABLE(page_id text, title text, registry_category text, source_url text, partner_links text)
 LANGUAGE sql
 STABLE
AS $function$
  SELECT page_id, title, registry_category, source_url, partner_links
  FROM rheingau_excluded_registry
  WHERE registry_category IN ('partner_area', 'press_area', 'newsletter', 'jobs')
     OR (registry_category = 'legal' AND source_url NOT LIKE '%/frag-lisbeth/%')
  ORDER BY registry_category, title;
$function$;
