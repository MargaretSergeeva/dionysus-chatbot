-- DC2-143 — dryness label per wine (table wine_dryness), derived from residual sugar and acidity.
-- Rule: EU Regulation (EU) 2019/33, Annex III (still wines):
--   Trocken      RZ <= 4 g/l, or RZ <= 9 g/l and acidity >= RZ - 2
--   Halbtrocken  RZ <= 12 g/l, or RZ <= 18 g/l and acidity >= RZ - 10
--   Lieblich     RZ <= 45 g/l
--   Süß          RZ > 45 g/l
-- Reconstructed 01.10.2026: the table was built outside migrations; this rule reproduces all 763 existing rows exactly.
-- Customer changes to the formula come in as a new mapping (decision 28.09.2026). Re-runnable.

create table if not exists public.wine_dryness (
  wein_id text primary key references public.wines(wein_id) on delete cascade,
  dryness_de text not null,
  dryness_en text not null,
  basis text not null,
  calculated_at timestamptz not null default now()
);

insert into public.wine_dryness (wein_id, dryness_de, dryness_en, basis)
select w.wein_id, d.de, d.en, 'EU Verordnung (EU) 2019/33, Anhang III (Restzucker/Säure)'
from public.wines w
cross join lateral (select case
    when w.restzucker_g_l <= 4 or (w.restzucker_g_l <= 9 and w.saeure_g_l >= w.restzucker_g_l - 2) then 'Trocken'
    when w.restzucker_g_l <= 12 or (w.restzucker_g_l <= 18 and w.saeure_g_l >= w.restzucker_g_l - 10) then 'Halbtrocken'
    when w.restzucker_g_l <= 45 then 'Lieblich'
    else 'Süß' end as de) k
cross join lateral (select k.de, case k.de when 'Trocken' then 'Dry' when 'Halbtrocken' then 'Off-dry'
                                        when 'Lieblich' then 'Medium' else 'Sweet' end as en) d
where w.restzucker_g_l is not null and w.saeure_g_l is not null
on conflict (wein_id) do update set dryness_de = excluded.dryness_de, dryness_en = excluded.dryness_en,
  basis = excluded.basis, calculated_at = now();
