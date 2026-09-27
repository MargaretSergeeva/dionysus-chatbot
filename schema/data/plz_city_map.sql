-- DC2-132: canonical city, derived from the page's own address block (PLZ + town)
-- inside `rheingau_pages.content`, not from the messy free-text `cities` column
-- (which mixes real towns with the broader "Rheingau" region tag in one
-- pipe-delimited string, e.g. "Oestrich-Winkel | Oestrich | Winkel | Hallgarten").
--
-- PLZ is the join key rather than the parsed town text, because Eltville's
-- Ortsteile (Erbach/Hattenheim/Martinsthal/Rauenthal) each carry their own PLZ
-- but the source text inconsistently labels them as "Eltville am Rhein" /
-- "Eltville-Hattenheim" / "Hattenheim" / "Eltville" for the very same address —
-- PLZ disambiguates correctly where text alone would collapse distinct
-- districts together.
--
-- Coverage after backfill: poi 93.5%, event 95.4%, accommodation 99.1%,
-- experience 93.8%; pages 15.8%, tour 9.3% (expected — those aren't
-- single-location pages, so most legitimately have no page-level address).
-- See DC2-A-127 for the full writeup.

CREATE TABLE IF NOT EXISTS public._plz_city_map (
  plz text PRIMARY KEY,
  city text NOT NULL
);
COMMENT ON TABLE public._plz_city_map IS
  'PLZ -> canonical Rheingau town/district. Lookup/normalization table, same convention
   as _grape_map / _weinart_map: no FK, used by the city backfill, not joined at query time.';

INSERT INTO public._plz_city_map (plz, city) VALUES
  ('65385', 'Rüdesheim am Rhein'),
  ('65375', 'Oestrich-Winkel'),
  ('65366', 'Geisenheim'),
  ('65239', 'Hochheim am Main'),
  ('65343', 'Eltville am Rhein'),
  ('65344', 'Eltville-Martinsthal'),
  ('65345', 'Eltville-Rauenthal'),
  ('65346', 'Eltville-Erbach'),
  ('65347', 'Eltville-Hattenheim'),
  ('65391', 'Lorch'),
  ('65396', 'Walluf'),
  ('65399', 'Kiedrich'),
  ('65439', 'Flörsheim am Main'),
  ('65183', 'Wiesbaden'),
  ('65185', 'Wiesbaden'),
  ('65187', 'Wiesbaden'),
  ('65189', 'Wiesbaden'),
  ('65195', 'Wiesbaden'),
  ('65199', 'Wiesbaden'),
  ('65201', 'Wiesbaden'),
  ('65203', 'Wiesbaden'),
  ('65205', 'Wiesbaden')
ON CONFLICT (plz) DO NOTHING;

-- rheingau_pages.city / city_source columns + the backfill itself:

ALTER TABLE rheingau_pages ADD COLUMN IF NOT EXISTS city text;
ALTER TABLE rheingau_pages ADD COLUMN IF NOT EXISTS city_source text;

COMMENT ON COLUMN rheingau_pages.city IS
  'Canonical town/district (DC2-132, DC2-A-127), backfilled from the PLZ+town found in the page''s
   own address block in `content`, mapped through _plz_city_map. NULL when no address
   block was found (mostly category=pages/tour, which are not single-location pages) or
   the PLZ fell outside the known Rheingau range (a handful of data-entry outliers, e.g.
   a PLZ from a different region entirely) — left NULL rather than guessed. Distinct from
   the free-text, multi-value `cities` column, which mixes actual towns with the broader
   "Rheingau" region tag and cannot be filtered on reliably.';
COMMENT ON COLUMN rheingau_pages.city_source IS
  'How `city` was set. Currently only ''address_plz'' (DC2-132). Lets later tiers
   (manual/self-reported) be added without touching this backfill.';

WITH extracted AS (
  SELECT page_id,
    (regexp_match(content,
      '(\d{5})\s+(Rüdesheim(?: am Rhein)?|Eltville(?:-\w+)?(?: am Rhein)?|Geisenheim|Oestrich-Winkel(?: Hallgarten)?|Lorch|Kiedrich|Walluf|Hochheim(?: am Main)?|Flörsheim(?: am Main)?|Wiesbaden|Johannisberg|Hattenheim|Erbach|Rauenthal|Winkel|Assmannshausen|Martinsthal|Mittelheim)'
    ))[1] AS plz
  FROM rheingau_pages
  WHERE is_active
)
UPDATE rheingau_pages rp
SET city = m.city,
    city_source = 'address_plz'
FROM extracted e
JOIN public._plz_city_map m ON m.plz = e.plz
WHERE rp.page_id = e.page_id;
