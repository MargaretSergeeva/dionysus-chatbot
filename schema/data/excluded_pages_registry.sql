-- DC2-134: registry for the ~73 Isklucheno rows NOT recovered into rheingau_pages
-- (the 7 regional-project pages are handled separately — see regional_projects.sql, DC2-133).
--
-- Not merged into rheingau_pages: this is a different kind of content (legal
-- boilerplate, internal/technical pages, empty pages) that the tourist-facing
-- retrieval functions should never surface. But per client feedback, some of
-- it (Partnerbereich, Pressebereich) is real content a partner or press
-- contact could legitimately ask the bot about (brochures, quality-seal
-- certification, ad-code guidelines) — so it's tracked here in a queryable
-- registry, category by category, rather than silently dropped.

CREATE TABLE IF NOT EXISTS public.rheingau_excluded_registry (
  page_id text PRIMARY KEY,
  title text NOT NULL,
  registry_category text NOT NULL,
  exclusion_reason_original text,
  source_url text,
  partner_links text,
  content_verified_empty boolean,
  notes text,
  added_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.rheingau_excluded_registry IS
  'DC2-134: pages crawled but kept out of rheingau_pages entirely (distinct from
   category=regional_project, DC2-133, which WAS merged in). Not queried by the
   tourist-facing retrieval functions (filter_rheingau_pages / match_rheingau_chunks*);
   exists so partner/press/legal content is tracked and findable, not silently lost.';

COMMENT ON COLUMN public.rheingau_excluded_registry.registry_category IS
  'One of: legal, partner_area, press_area, organisation, jobs, newsletter, internal,
   technical, no_content. Normalized grouping over the raw Isklucheno exclusion reason
   -- lets "show me everything for partners" or "everything Datenschutz-related" be
   a simple filter instead of parsing free-text reasons.';

COMMENT ON COLUMN public.rheingau_excluded_registry.content_verified_empty IS
  'Only set for registry_category=no_content. true = client manually confirmed the page
   has no usable text (25.09.2026 review, 13 pages). NULL = not manually checked yet
   (most "Kein verwertbarer Text" rows) -- never guessed, per the NULL=unverified rule
   used across rheingau_pages amenity flags (DC2-A-125).';

INSERT INTO public.rheingau_excluded_registry
  (page_id, title, registry_category, exclusion_reason_original, source_url, partner_links, content_verified_empty)
VALUES
  -- legal
  ('506e5da79ab2b7fe','Datenschutz','legal','Datenschutz / политика конфиденциальности','https://www.rheingau.com/datenschutz',NULL,NULL),
  ('8484e7a6f99305e3','Datenschutzerklärung','legal','Datenschutzerklärung / политика конфиденциальности','https://www.rheingau.com/datenschutzerklaerung',NULL,NULL),
  ('b6b94b9801e2832a','Whistleblowing System','legal','Hinweisgebersystem / служебная система сообщений','https://www.rheingau.com/hinweisgebersystem',NULL,NULL),
  ('6e7d79a55c19dc42','Impressum','legal','Impressum / выходные данные','https://www.rheingau.com/impressum','www.shapefruit.de — https://www.shapefruit.de/webseiten-mit-wordpress/',NULL),

  -- jobs
  ('a0593e36dcef2ff5','Jobs','jobs','Jobs / вакансии','https://www.rheingau.com/jobs',NULL,NULL),

  -- newsletter
  ('f31daf661f55f4c2','Cleverreach','newsletter','Newsletter / подписка на рассылку','https://www.rheingau.com/newsletter',NULL,NULL),

  -- internal
  ('55464792aefd3e0c','Anmeldung Mitgliederbereich Weinbauverband','internal','Interner Bereich / внутренний раздел','https://www.rheingau.com/intern',NULL,NULL),
  ('c180d867c9833b25','Interner Bereich','internal','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/interner-bereich',NULL,NULL),
  ('ec19b4b61fca80ba','Interner Newsletter Deskline Infrastruktur','internal','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/termineerfassen/interner-newsletter-deskline-infrastruktur',NULL,NULL),
  ('36d08dbcb62c89c9','Passwort vergessen','internal','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/mitgliederbereich-weinbauverand/passwort-vergessen',NULL,NULL),
  ('8eb239bc6de733fe','Newsletterabfrage 2024','internal','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/interner-newsletter/newsletterabfrage-2025',NULL,NULL),

  -- technical
  ('f8cdb93c0bb6a88a','Danke','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/form/danke',NULL,NULL),
  ('a8330141064bdba8','Event-Kalender','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/webkomponenten/test-weingut-schreiber/event-kalender',NULL,NULL),
  ('7f24d78bb65fd1a9','Interaktive','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/webkomponenten/test-weingut-schreiber/interaktive',NULL,NULL),
  ('0343c0a0755ff98d','Regiondo React-Widget','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/regiondo-react-widget',NULL,NULL),
  ('93f697b3bc78ef96','Regiondo-Test','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/regiondo',NULL,NULL),
  ('a03af69a6da397cf','Schreiber_Test','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/webkomponenten/schreiber-test',NULL,NULL),
  ('c9b1553ef4ee5af2','Schreiber_Test (Kopie 1)','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/webkomponenten/schreiber-test-1',NULL,NULL),
  ('3b2234948cabfbdd','TEst2','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/test2',NULL,NULL),
  ('aea15bcfdaf66b4d','TOSC','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/tosc',NULL,NULL),
  ('a7d3607c15d84845','Tosc Unterkünfte','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/tosc-unterkuenfte',NULL,NULL),
  ('984ab77e7e7d57ff','Webkomponenten','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/webkomponenten',NULL,NULL),
  ('92966ac612337ead','Suche','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/suche',NULL,NULL),
  ('483344fac90bcc00','Umfrage Hinweis auf Download','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/download/download-corporate-design/nutzungsbedingungen/umfrage-hinweis-auf-download',NULL,NULL),
  ('d0bade678c1f131b','Teilnehmer_Genussmomente','technical','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/genuss-gewinnspiel-welt/teilnehmer-genussmomente',NULL,NULL),
  ('6bcf605879c7e807','Footer','technical','Technische Seite / техническая страница','https://www.rheingau.com/footer-1','https://www.facebook.com/rheingau.deineregion; https://www.instagram.com/rheingau.deineregion; https://www.youtube.com/channel/UCU099sCwCPVlZnkYk_zKdMw; https://www.pinterest.de/erlebe_rheingau/; https://www.linkedin.com/company/rheingau-taunus-kultur-und-tourismus/; https://www.linkedin.com/company/rheingauer-weinwerbung-gmbh/',NULL),

  -- organisation (governance/admin pages -- distinct from the 7 project pages recovered under DC2-133)
  ('c9bbed8838e48892','Aktuelle Projekte','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/aktuelle-projekte','Weitere Infos — https://www.regionalpark-rheinmain.de/portfolio-item/regionalpark-route-leinpfad/',NULL),
  ('6795e223da5a2947','Anmeldung Mitgliederversammlung','organisation','Organisation / организационная страница','https://www.rheingau.com/marketingverein/anmeldung-mitgliederversammlung',NULL,NULL),
  ('21e97b6d4459c0a3','Bekanntmachungen','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/bekanntmachungen',NULL,NULL),
  ('ca2870e367bf500a','Download Service-Point Schild','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/servicepoint-weinprobierstand/download-service-point-schild',NULL,NULL),
  ('d4a7491d33b3eeac','Haushaltsplan','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/verbandsversammlung/haushaltsplan',NULL,NULL),
  ('a34e2a12f44fa9ab','Lachaue','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/aktuelle-projekte/lachaue',NULL,NULL),
  ('ddeed4925c314682','Protokollarchiv','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/verbandsversammlung/protokollarchiv',NULL,NULL),
  ('08a9d3c3975d71ec','Rheingau-Taunus Marketing Verein','organisation','Organisation / организационная страница','https://www.rheingau.com/marketingverein','Jetzt entdecken — http://www.das-spritzenhaus.de; https://hotelschloss-reinhartshausen.de/; https://gaestebegleiter.de; https://taunuswunderland.de; http://www.schoenleber-1848.com; http://www.klickrhein.de',NULL),
  ('6404ec4684bfc4ec','Service-Point Weinprobierstand','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/servicepoint-weinprobierstand',NULL,NULL),
  ('0a067ba4b638998e','Unterführung Erbach','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/aktuelle-projekte/unterfuehrung-erbach',NULL,NULL),
  ('3c8c7a38d4d4ade3','Verbandsversammlung','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/verbandsversammlung',NULL,NULL),
  ('1e9cc2e9f88bbb6d','Verbandsvorstand','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband/vorstand-und-mitglieder','Stadt Eltville am Rhein http://www.eltville.de; Gemeinde Walluf http://www.walluf.de; Gemeinde Kiedrich http://www.kiedrich.de; Stadt Oestrich-Winkel http://www.oestrich-winkel.de; Hochschulstadt Geisenheim http://www.geisenheim.de; Verein für Regionalentwicklung http://www.zukunft-rheingau.de; Stadt Rüdesheim http://www.stadt-ruedesheim.de; Rheingau-Taunus-Kreis http://www.rheingau-taunus.de; Stadt Lorch http://www.lorch-rhein.de',NULL),
  ('967032d96a2516f8','Zweckverband Rheingau','organisation','Organisation / организационная страница','https://www.rheingau.com/zweckverband',NULL,NULL),

  -- partner_area
  ('d15f98faede46022','Broschürenabfrage','partner_area','Partnerbereich / раздел для партнёров','https://www.rheingau.com/fuer-leistungspartnerinnen-und-partner/broschuerenabfrage',NULL,NULL),
  ('4febcc21fb90858f','Für Leistungspartnerinnen und -partner','partner_area','Partnerbereich / раздел для партнёров','https://www.rheingau.com/fuer-leistungspartnerinnen-und-partner','Tourismuspolitischer Handlungsrahmen Hessen 2023 — https://www.hessen.tourismusnetzwerk.info/wp-content/uploads/2023/07/TPH_final__komprimierte_Version_fuer_Web_HESSEN_TPH_2023_WEB2.pdf; Strategischer Marketingplan für Hessen 2025+ — https://www.hessen.tourismusnetzwerk.info/inhalte/tourismusstrategie/strategischer-marketingplan/; Tourismus-Hub Hessen — https://www.hessen.tourismusnetzwerk.info/inhalte/digitales/tourismus-hub-hessen/; Gastgeber Kompass Hessen — https://www.hessen.tourismusnetz-werk.info/inhalte/qualitaet/infos-fuer-gastgeber/gastgeber-kompass/',NULL),
  ('56cceb14afcbd02b','Klassifizierung mit Qualitätssiegeln','partner_area','Partnerbereich / раздел для партнёров','https://www.rheingau.com/fuer-leistungspartnerinnen-und-partner/klassifizierung-mit-qualitaetssiegeln','www.reisen-fuer-alle.de; www.sterneferien.de/dtv-klassifizierung; www.bettundbike.de/unterkunft-werden; www.wanderbares-deutschland.de/gastgeber',NULL),
  ('89b6eda236f72db7','Regiondo','partner_area','Partnerbereich / раздел для партнёров','https://www.rheingau.com/fuer-leistungspartnerinnen-und-partner/regiondo','Erlebnisse buchen auf wiesbaden.de; hessen-tourismus.de; ruedesheim.de',NULL),

  -- press_area
  ('d41055dddcea03bf','Leitfaden Werbekodex','press_area','Pressebereich / раздел для прессы','https://www.rheingau.com/service/presse-download/leitfaden-werbekodex','Social-Media-Leitlinien des deutschen Werberates — https://werberat.de/wp-content/uploads/2024/07/Social-Media-Leitlinien-fuer-Hersteller-alkohlhaltiger-Getraenke_abAug24.pdf; https://werberat.de/leitfaden-zum-werbekodex-des-deutschen-werberats/alkoholhaltige-getraenke/',NULL),
  ('391f92562441460a','Presse, Download & Leitfaden Werbekodex','press_area','Pressebereich / раздел для прессы','https://www.rheingau.com/service/presse-download',NULL,NULL),

  -- no_content: the 13 pages the client manually verified as genuinely empty
  ('f3806dc855e93e97','Abtei St. Hildegard','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/abtei-st-hildegard',NULL,true),
  ('ea84de5559556054','Burgruine Scharfenstein','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/burgruine-scharfenstein',NULL,true),
  ('028dffdbda91b2c4','Freistaat Flaschenhals','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/freistaat-flaschenhals',NULL,true),
  ('bbe7701176dad089','Geisenheimer Linde','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/geisenheimer-linde',NULL,true),
  ('ac3c70812e2d197b','Geisenheimer Wochenmarkt','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/menue/genuss/geisenheimer-wochenmarkt',NULL,true),
  ('de480af9befba4f6','Graeger Villa','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/graeger-villa',NULL,true),
  ('d082171fd12dc38c','Königsklinger Aue','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/koenigsklinger-aue',NULL,true),
  ('936dd84ac99b1d2b','Weingut Bott','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/weingut-bott',NULL,true),
  ('015a123c54e7d5b7','Weingut Höhn','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/rheingau-grosses-gewaechs/weingut-hoehn',NULL,true),
  ('e3d8a97bde17c9eb','Weingut Schamari Mühle','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/rheingau-grosses-gewaechs/weingut-schamari-muehle',NULL,true),
  ('7ac32bdadaec97f6','Weingut Schönleber Blümlein','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/rheingau-grosses-gewaechs/weingut-schoenleber-bluemlein',NULL,true),
  ('ea209a103834226e','Weingut Schumann Nägler','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/rheingau-grosses-gewaechs/weingut-schumann-naegler',NULL,true),
  ('f35c9beef53636bd','Weinverladekran','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/weinverladekran',NULL,true),

  -- no_content: remaining "Kein verwertbarer Text" pages -- not yet manually checked one by one, left NULL
  ('1eb5ce5c157b7889','Die Millionen Meyers','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/kultur/die-millionen-meyers',NULL,NULL),
  ('aef4311fdfac94ec','Geführte Radtouren/Events','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/radfahren/gefuehrte-radtouren/events',NULL,NULL),
  ('4276874db11ab11a','Instagram','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefluester/instagram',NULL,NULL),
  ('ecbc27b8cf7e539c','Lisbeth empfiehlt','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/lisbeth-empfiehlt',NULL,NULL),
  ('44dfb8a34988f6dc','News','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/news-1',NULL,NULL),
  ('29bf546ff67115ba','Öffentliche Verkostung - Hessische Landeswein- und Sektprämierung 2025','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/hessische-landeswein-und-sektpraemierung',NULL,NULL),
  ('21628d6f44f6b2cb','per Bus, per Schiff, per Fahrrad','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gruppen-angebote/per-bus-per-schiff-per-fahrrad',NULL,NULL),
  ('2dcd5d3125e0d595','Prospekte bestellen zu WIESBADEN RHEINGAU','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/prospektbestellung',NULL,NULL),
  ('b202ea8fcb6025c0','Qualitätskriterien','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wein/rheingau-grosses-gewaechs/qualitaetskriterien',NULL,NULL),
  ('b547f0b6495dba1c','Service','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/service',NULL,NULL),
  ('2dcb00c84c0f29c5','Spezialangebote','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/spezialangebote',NULL,NULL),
  ('71039eb3f1e37709','Städteportraits','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/staedteportraits',NULL,NULL),
  ('d7b70afb47d66ecf','Weinwanderung mit Kultur- und Weinbotschaftern','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/gefuehrte-weinwanderung',NULL,NULL),
  ('921b7ac743c9885e','Wine4Sense','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/wine4sense',NULL,NULL),
  ('3fed3e12e5688ced','Workshops','no_content','Kein verwertbarer Text / нет пригодного текста','https://www.rheingau.com/rtkt/workshops',NULL,NULL)
ON CONFLICT (page_id) DO NOTHING;
