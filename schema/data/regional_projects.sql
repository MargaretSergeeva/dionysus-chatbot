-- DC2-133: recover 7 "Organisation"-tagged Isklucheno pages into rheingau_pages
-- as category=regional_project, instead of leaving them excluded.
--
-- These 7 pages (URL shape: zweckverband/aktuelle-projekte/...) were originally
-- excluded as generic organizational/governance pages, but manual review showed
-- they contain real, substantive text about Zweckverband Rheingau regional-park
-- development projects — some completed, some in progress, some still at
-- feasibility-study stage. Distinct from the OTHER "Organisation" pages (board
-- membership, meeting minutes, budgets), which stay excluded — see
-- ../data/excluded_pages_registry.sql (DC2-134).
--
-- project_status / expected_completion are meaningful ONLY for
-- category=regional_project; NULL for every other category.

ALTER TABLE rheingau_pages ADD COLUMN IF NOT EXISTS project_status text;
ALTER TABLE rheingau_pages ADD COLUMN IF NOT EXISTS expected_completion text;

COMMENT ON COLUMN rheingau_pages.project_status IS
  'Only meaningful for category=regional_project (DC2-133): existing | in_progress | planned | overview.
   NULL for every other category — this is not a general-purpose status field.';
COMMENT ON COLUMN rheingau_pages.expected_completion IS
  'Free-text completion note for category=regional_project rows (DC2-133), e.g. "bis Ende 2025".
   NULL when the source page gives no date. Not a parsed/typed date — source text varies too much.';

INSERT INTO rheingau_pages
  (page_id, category, page_type, primary_category_de, title, content, content_hash, source_url,
   city, city_source, project_status, expected_completion, is_active, last_crawled_at)
VALUES
  ('8c2b0a5ff1460b7c', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Leinpfadplätzchen', '...(full German text, see rheingau.com)...',
   md5('Leinpfadplätzchen' || 'Der neue Rastplatz am westlichen Ostrand Wallufs'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/leinpfadplaetzchen',
   'Walluf', 'manual_review', 'existing', NULL, true, now()),
  ('487bd3251abe08f5', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Nikolausquelle', '...(full German text, see rheingau.com)...',
   md5('Nikolausquelle' || 'Nikolausquelle'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/nikolausquelle',
   'Eltville am Rhein', 'manual_review', 'existing', NULL, true, now()),
  ('3345743e7edfe668', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Goethe Strand Rüdesheim', '...(full German text, see rheingau.com)...',
   md5('Goethe Strand Rüdesheim' || 'Goethe Strand Rüdesheim'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/goethe-strand-ruedesheim',
   'Rüdesheim am Rhein', 'manual_review', 'in_progress', 'bis Ende des Jahres 2025', true, now()),
  ('17352ec711f95e96', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Rosengarten Kurfürstliche Burg', '...(full German text, see rheingau.com)...',
   md5('Rosengarten Kurfürstliche Burg' || 'Rosengarten Kurfürstliche Burg'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/rosengarten-kurfuerstliche-burg',
   'Eltville am Rhein', 'manual_review', 'planned', 'Planung bis Ende 2025/Anfang 2026, Baubeginn Herbst 2026', true, now()),
  ('5809477a9af9c6ff', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Erlebnispunkt Lorch', '...(full German text, see rheingau.com)...',
   md5('Erlebnispunkt Lorch' || 'Erlebnispunkt Lorch'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/regionalpark-projekte/machbarkeitsstudie-erlebnispunkt-lorch',
   'Lorch', 'manual_review', 'planned', NULL, true, now()),
  ('5f51f006aa4848bc', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Radschnellverbindung', '...(full German text, see rheingau.com)...',
   md5('Radschnellverbindung' || 'Radschnellverbindung'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/radschnellverbindung',
   NULL, 'manual_review', 'in_progress', 'Anfang 2024 laut Quelle (Stand der Quelle: 2023, möglicherweise veraltet)', true, now()),
  ('19e86380d5ee789a', 'regional_project', 'zweckverband_project', 'Regionalpark-Projekt',
   'Erlebnispunkte Regionalpark Route', '...(full German text, see rheingau.com)...',
   md5('Erlebnispunkte Regionalpark Route' || 'Erlebnispunkte Regionalpark Route'),
   'https://www.rheingau.com/zweckverband/aktuelle-projekte/regionalpark-route',
   NULL, 'manual_review', 'overview', NULL, true, now())
ON CONFLICT (page_id) DO NOTHING;

UPDATE "Isklucheno"
SET "Comments" = 'Восстановлено в rheingau_pages 25.09.2026 как category=regional_project (DC2-133) — на странице реально есть текст, исключение как "Organisation" было ошибочным.'
WHERE "ID страницы" IN (
  '8c2b0a5ff1460b7c','487bd3251abe08f5','3345743e7edfe668',
  '17352ec711f95e96','5809477a9af9c6ff','5f51f006aa4848bc','19e86380d5ee789a'
);

-- NOTE: this file is the repo source-of-truth record of what was applied via
-- mcp__Supabase__apply_migration (migration name: add_regional_projects_from_isklucheno).
-- The `content` values here are placeholders — the live rows in Supabase hold the
-- actual full German text fetched from each source_url; re-running this file
-- as-is would overwrite that with placeholder text, so it is NOT idempotent for
-- `content` (page_id conflicts are skipped via ON CONFLICT DO NOTHING, so in
-- practice re-running this is a no-op once the rows already exist).
