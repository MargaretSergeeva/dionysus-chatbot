-- DC2-10 / DC2-11 / DC2-12 — wine normalization (grape, wine type, name, synonyms). Re-runnable.
-- Raw columns stay untouched; derived columns: rebsorte_normalized, rebsorte_array, weinart_normalized,
-- weinname_normalized, synonyms. Lookup tables were filled outside migrations until 01.10.2026; their content is seeded here.
-- Origin: migrations add_normalization_columns_and_grape_map + apply_wine_normalization (22.09.2026).
--
-- !! NOT YET SAFE TO RUN ON THE LIVE DATA (checked 01.10.2026). The live columns were edited after 22.09 outside
-- !! migrations, so this file would change them:
-- !!   - 12 rows: blend labels in live data ("… blend", "Unspecified & Blauer Spätburgunder (Pinot Noir) blend")
-- !!   - 26 rows: weinname_normalized has a leading "- " in live data (e.g. "- Rotwein") — looks like a bug
-- !!   - all rows: synonyms in live data also contain Russian terms (e.g. "Белое вино") that are not in the lookup tables
-- !!   - 49 rows: rebsorte is NULL (no mapping)
-- !! Decide which version is right, update the lookup tables here, then add this step back to run_all.sh (DC2-162).

alter table public.wines
  add column if not exists rebsorte_normalized text,
  add column if not exists rebsorte_array text[],
  add column if not exists weinart_normalized text,
  add column if not exists weinname_normalized text,
  add column if not exists synonyms jsonb;

create table if not exists public._grape_map (raw text primary key, display text not null, components text[] not null);
create table if not exists public._grape_synonyms (canonical text primary key, synonyms jsonb not null);
create table if not exists public._weinart_map (raw text primary key, display text not null, synonyms jsonb not null);

-- Seed: raw grape string -> display name + components (42 rows, state 01.10.2026)
insert into public._grape_map (raw, display, components) values
('- & Bl. Spätburgunder', 'Blauer Spätburgunder (Pinot Noir)', '{"Blauer Spätburgunder"}'),
('Accent', 'Accent', '{Accent}'),
('Auxerrois', 'Auxerrois', '{Auxerrois}'),
('Bl. Spätburgunder', 'Blauer Spätburgunder (Pinot Noir)', '{"Blauer Spätburgunder"}'),
('Cab. Sauvignon', 'Cabernet Sauvignon', '{"Cabernet Sauvignon"}'),
('Cab. Sauvignon & Bl. Spätburgu', 'Cabernet Sauvignon & Blauer Spätburgunder (Pinot Noir)', '{"Cabernet Sauvignon","Blauer Spätburgunder"}'),
('Cabernet Blanc', 'Cabernet Blanc', '{"Cabernet Blanc"}'),
('Cabernet Cubin', 'Cabernet Cubin', '{"Cabernet Cubin"}'),
('Chardonnay', 'Chardonnay', '{Chardonnay}'),
('Dacpo & Portug. & Spätbgd.', 'Dakapo & Portugieser & Spätburgunder (Pinot Noir)', '{Dakapo,Portugieser,Spätburgunder}'),
('Dornfelder', 'Dornfelder', '{Dornfelder}'),
('Gelber Muskateller', 'Gelber Muskateller (Yellow Muscat)', '{"Gelber Muskateller"}'),
('Goldmuskateller', 'Goldmuskateller (Gold Muscat)', '{Goldmuskateller}'),
('Grauburgunder', 'Grauburgunder (Pinot Gris)', '{Grauburgunder}'),
('Grauer Burgunder', 'Grauburgunder (Pinot Gris)', '{Grauburgunder}'),
('Kerner', 'Kerner', '{Kerner}'),
('Lemberger', 'Lemberger (Blaufränkisch)', '{Lemberger}'),
('Merlot', 'Merlot', '{Merlot}'),
('Merlot & Bl. Spätburgunder', 'Merlot & Blauer Spätburgunder (Pinot Noir)', '{Merlot,"Blauer Spätburgunder"}'),
('Müller-Th.', 'Müller-Thurgau (Rivaner)', '{Müller-Thurgau}'),
('Pinot', 'Pinot (unspecified)', '{"Pinot (unspecified)"}'),
('Portugieser', 'Portugieser (Blauer Portugieser)', '{Portugieser}'),
('Riesling', 'Riesling', '{Riesling}'),
('Riesling & Dakapo', 'Riesling & Dakapo', '{Riesling,Dakapo}'),
('Rosenmuskateller', 'Rosenmuskateller (Rose Muscat)', '{Rosenmuskateller}'),
('Rotberger', 'Rotberger', '{Rotberger}'),
('Roter Riesling', 'Roter Riesling (Red-Berried Riesling)', '{"Roter Riesling"}'),
('Roter Traminer', 'Roter Traminer (Savagnin Rose)', '{"Roter Traminer"}'),
('Saint Laurent', 'Saint Laurent', '{"Saint Laurent"}'),
('Sauvignac', 'Sauvignac', '{Sauvignac}'),
('Sauvignon Blanc', 'Sauvignon Blanc', '{"Sauvignon Blanc"}'),
('Sauvignon blanc & Riesling', 'Sauvignon Blanc & Riesling', '{"Sauvignon Blanc",Riesling}'),
('Sauvignon gris', 'Sauvignon Gris', '{"Sauvignon Gris"}'),
('Scheurebe', 'Scheurebe', '{Scheurebe}'),
('Silvaner', 'Silvaner (Sylvaner)', '{Silvaner}'),
('Souvignier Gris', 'Souvignier Gris', '{"Souvignier Gris"}'),
('Spätburgunder & Divico', 'Spätburgunder (Pinot Noir) & Divico', '{Spätburgunder,Divico}'),
('St. Laurent', 'Saint Laurent', '{"Saint Laurent"}'),
('Weißbu, Chard, Graubu, Riesli', 'Weißburgunder, Chardonnay, Grauburgunder & Riesling', '{Weißburgunder,Chardonnay,Grauburgunder,Riesling}'),
('Weißburg&RotRies&SauBl&Ries', 'Weißburgunder, Roter Riesling, Sauvignon Blanc & Riesling', '{Weißburgunder,"Roter Riesling","Sauvignon Blanc",Riesling}'),
('Weißburgunder', 'Weißburgunder (Pinot Blanc)', '{Weißburgunder}'),
('Weisser Burgunder', 'Weißburgunder (Pinot Blanc)', '{Weißburgunder}')
on conflict (raw) do update set display = excluded.display, components = excluded.components;

-- Seed: canonical grape -> multilingual synonyms (31 rows)
insert into public._grape_synonyms (canonical, synonyms) values
('Accent', '["Accent"]'),
('Auxerrois', '["Auxerrois"]'),
('Blauer Spätburgunder', '["Spätburgunder", "Blauer Spätburgunder", "Pinot Noir", "Pinot Nero", "Pinot"]'),
('Cabernet Blanc', '["Cabernet Blanc"]'),
('Cabernet Cubin', '["Cabernet Cubin"]'),
('Cabernet Sauvignon', '["Cabernet Sauvignon", "Cab. Sauvignon"]'),
('Chardonnay', '["Chardonnay"]'),
('Dakapo', '["Dakapo", "Dacpo"]'),
('Divico', '["Divico"]'),
('Dornfelder', '["Dornfelder"]'),
('Gelber Muskateller', '["Gelber Muskateller", "Yellow Muscat", "Muscat Blanc", "Gele Muskaat", "Gul Muskat", "Moscato Giallo", "Muscat Doré"]'),
('Goldmuskateller', '["Goldmuskateller", "Gold Muscat", "Gouden Muskaat", "Guldmuskat", "Moscato Giallo", "Muscat Doré"]'),
('Grauburgunder', '["Grauburgunder", "Ruländer", "Pinot Gris", "Pinot Grigio"]'),
('Kerner', '["Kerner"]'),
('Lemberger', '["Lemberger", "Blaufränkisch", "Franconia"]'),
('Merlot', '["Merlot"]'),
('Müller-Thurgau', '["Müller-Thurgau", "Müller-Th.", "Rivaner"]'),
('Portugieser', '["Portugieser", "Blauer Portugieser"]'),
('Riesling', '["Riesling", "Rheinriesling"]'),
('Rosenmuskateller', '["Rosenmuskateller", "Rose Muscat", "Roze Muskaat", "Rosa Muskat", "Moscato Rosa", "Muscat Rose"]'),
('Rotberger', '["Rotberger"]'),
('Roter Riesling', '["Roter Riesling", "Red Riesling", "Rode Riesling", "Rød Riesling", "Riesling Rosso", "Riesling Rouge"]'),
('Roter Traminer', '["Roter Traminer", "Savagnin Rose", "Red Traminer", "Traminer Rosa"]'),
('Saint Laurent', '["Sankt Laurent", "St. Laurent", "Saint Laurent"]'),
('Sauvignac', '["Sauvignac"]'),
('Sauvignon Blanc', '["Sauvignon Blanc", "Sauvignon"]'),
('Sauvignon Gris', '["Sauvignon Gris"]'),
('Scheurebe', '["Scheurebe"]'),
('Silvaner', '["Silvaner", "Sylvaner"]'),
('Souvignier Gris', '["Souvignier Gris"]'),
('Weißburgunder', '["Weißburgunder", "Weissburgunder", "Pinot Blanc", "Pinot Bianco"]')
on conflict (canonical) do update set synonyms = excluded.synonyms;

-- Seed: raw wine type -> display + synonyms (6 rows)
insert into public._weinart_map (raw, display, synonyms) values
('Blanc de Noir', 'Blanc de Noir', '["Blanc de Noir", "White Wine from Red Grapes"]'),
('Roseewein', 'Roséwein', '["Roséwein", "Rosé Wine", "Rosé", "Rosévin", "Vino Rosato", "Vin Rosé"]'),
('Rotling', 'Rotling', '["Rotling", "Field Blend Rosé", "Rosé (cuvée)", "Cuvée-rosé", "Rosato da Uvaggio", "Rosé d''Assemblage"]'),
('Rotwein', 'Rotwein', '["Rotwein", "Red Wine", "Rode Wijn", "Rødvin", "Vino Rosso", "Vin Rouge"]'),
('Weissherbst', 'Weißherbst', '["Weißherbst", "Single-variety Rosé", "Eendruifsrosé", "Enkeltdruerosé", "Rosato Monovitigno", "Rosé Mono-cépage"]'),
('Weisswein', 'Weißwein', '["Weißwein", "White Wine", "Witte Wijn", "Hvidvin", "Vino Bianco", "Vin Blanc"]')
on conflict (raw) do update set display = excluded.display, synonyms = excluded.synonyms;

-- DC2-10: grape
update public.wines w set rebsorte_normalized = gm.display, rebsorte_array = gm.components
from public._grape_map gm where w.rebsorte = gm.raw;

-- DC2-11: wine type spelling (ss -> ß, ee -> é), also in the wine name
update public.wines w set weinart_normalized = wm.display from public._weinart_map wm where w.weinart = wm.raw;
update public.wines set weinname_normalized =
  replace(replace(replace(weinname, 'Weissherbst', 'Weißherbst'), 'Weisswein', 'Weißwein'), 'Roseewein', 'Roséwein');

-- DC2-12: synonyms = grape synonyms (all components) + wine type synonyms
update public.wines w set synonyms = coalesce(
    (select jsonb_agg(distinct syn) from unnest(w.rebsorte_array) as comp(name)
       join public._grape_synonyms gs on gs.canonical = comp.name
       cross join lateral jsonb_array_elements_text(gs.synonyms) as syn), '[]'::jsonb)
  || coalesce((select wm.synonyms from public._weinart_map wm where wm.raw = w.weinart), '[]'::jsonb);
