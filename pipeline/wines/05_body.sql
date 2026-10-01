-- DC2-144 — body per wine (table wine_body). Only full-bodied wines get a row; no row = no information.
-- Rule (internal, customer confirmation pending): alcohol >= 13 % AND acidity > 7 g/l -> "Vollmundig".
-- Reconstructed 01.10.2026: the table was built outside migrations; this rule reproduces the existing 16 rows exactly.
-- The 747 other rows were removed on 29.09.2026 (backup archive.wine_body_not_full_bodied_20260929). Re-runnable.

create table if not exists public.wine_body (
  wein_id text primary key references public.wines(wein_id) on delete cascade,
  full_bodied boolean not null,
  body_de text,
  body_en text,
  basis text not null,
  status text not null,
  calculated_at timestamptz not null default now()
);

delete from public.wine_body b using public.wines w
where b.wein_id = w.wein_id and not (w.alkohol_pct >= 13 and w.saeure_g_l > 7);

insert into public.wine_body (wein_id, full_bodied, body_de, body_en, basis, status)
select wein_id, true, 'Vollmundig', 'Full-bodied',
       'Alkohol >= 13% UND Säure > 7 g/l (interne Regel, Kundenbestätigung ausstehend)', 'pending_customer_confirmation'
from public.wines where alkohol_pct >= 13 and saeure_g_l > 7
on conflict (wein_id) do update set full_bodied = true, body_de = excluded.body_de, body_en = excluded.body_en,
  basis = excluded.basis, status = excluded.status, calculated_at = now();
