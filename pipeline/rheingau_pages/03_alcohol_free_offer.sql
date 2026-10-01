-- DC2-142: alcohol_free_offer = true for pages that explicitly document alcohol-free wine, Sekt or
-- cocktails (incl. tours/tastings with alcohol-free options on request, and pages where alcohol-free
-- wine is a topic). Reviewed by Margarita on 28.09.2026 from the 51 active pages mentioning "alkoholfrei".
-- Pages with only soft drinks / juice or a bare mention stay NULL (= no information, never "no").
update public.rheingau_pages set alcohol_free_offer = true
where page_id in (
  -- Wine offers
  'fb6568e77028a056', -- Alkoholfreier Wein (Reset Riesling)
  'f53ede49d55beddd', -- Weinkellerei Carl Jung - Alkoholfrei
  '41dfe8007e806e63', -- Weingut BIBO RUNGE (poi)
  'c05adf88da350800', -- Weingut BIBO RUNGE (page)
  '0a46910904be48b5', -- Jahrgangspräsentation im Weingut Bibo Runge
  '3a0683d4e65560a1', -- Ausschank am REVOLUZZER Gartenhaus Weingut Bibo Runge
  'a15f2bb0c3bf667a', -- Querfeldwein Weindepot
  '2606107382f29ad9', -- Elster Mühle
  'bd530c31d59737f9', -- Rheingauer Wein (Reset Riesling section)
  '9f11de17b844ec86', -- Wir können auch anders: vegan, vegetarisch, alkoholfrei
  -- Tastings and events
  '7679fd986dad4a6a', -- QuerfeldweinTour geführte Weintour
  '147a44aeb03d14d1', -- SEKT-BRUNCH in der WEINVILLA Offenstein Erben
  '690b5f89e07f5c14', -- Die etwas andere Wein-Erlebnis-Tour
  'ddd10e46c0a7cbf8', -- TASTING - Käse trifft Sekt & Wein im Schloss Henkell
  '6aa3283761ad80e9', -- TASTING - Pearls of Europe
  '0baec5e1e9b7f953', -- TASTING - Cocktail-Mixing im Schloss Henkell
  'e1bd5ed371c2946d', -- Schaumwein Erlebnisseminar in der Villa Mumm (borderline, added)
  'cb61f7d57652d722', -- Weinseminar für Genießer im Weingut Nies (borderline, added)
  -- Wine-guide tours with alkoholfreie Optionen
  'd78f5692bebc7089', -- Eure Wunschtour
  '963e65723775d626', -- Hallgarter Sektspaziergang
  '8c418110a29c42cb', -- Niederwalddenkmal und Osteinscher Park
  '3230519023195836', -- per Bus
  'dd58816e0619710a', -- per Fahrrad
  'c61761efa892364a', -- Von Schloss zu Schloss
  '5ab5cb610fafc2d2', -- Wein- und Sektstadt Hochheim
  '857366b54c20f153', -- Weinwärts zwischen Eltville und Kiedrich
  '5f77040397329813', -- Hans Kessler (guide)
  'f42a8baf772cc4cd', -- Maria Nicolai (guide, borderline, added)
  '8b87c70939d5e61e'  -- Olaf Fuchs (guide, borderline, added)
);
