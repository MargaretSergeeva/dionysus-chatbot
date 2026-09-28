-- DC2-142: transport_type for 71 reviewed transport pages (Margarita, 28.09.2026).
-- Excluded as activities/other: Störzel wine walks (2), Loreley Schifffahrt, Querfeldwein tour with cable car,
-- Restaurant Biergarten Seilbahn, Weinprobierstand an der Fähre, per Bus, per Schiff, Anleger 511, Bike like a local.
update public.rheingau_pages set transport_type = 'info' where page_id in
  ('35b34a818b6b93ee','facc5d1bb8759b33','71b220600dcaf9a8','14d91b3604d927c2'); -- Anreise, Bahnsanierung, Schifffahrt, E-Bike Ladestationen
update public.rheingau_pages set transport_type = 'station' where page_id in
  ('a7f55712b4264e73','702dcb039e17e381','9fe941ee954727b0'); -- Bahnhof Rüdesheim, Lorch, Lorchhausen
update public.rheingau_pages set transport_type = 'ferry' where page_id in
  ('c62261e57ec5302b','78947ea509e4a277','36832d6eaf4aa899','b41597e11a5f6ed7','e148bc1692d3afe5');
update public.rheingau_pages set transport_type = 'boat_landing' where page_id in
  ('f652c9de1cd180b9','3f3795a9d0d77076','2e01e291975275d9','6bb7fdbd22d19e9e','b270064a6d75f3df','bc68fa8a6f7a6434');
update public.rheingau_pages set transport_type = 'cable_car' where page_id in
  ('812d9f8055c6f3f6','f9d97019912e5cec','8304500d7816a571','77f09030b75ed5a4'); -- Seilbahn page + poi, Niederwald-Sessellift, Ringticket
update public.rheingau_pages set transport_type = 'parking' where page_id in
  ('c9cab82f083770c2','c86fe9be5679ebf8','122d71a7d8eb736a','d0b1cdd15f65bc6e','afb7ed8036ab21b6','852fa29bda63ace0',
   '689ccae08ce83759','2e4c39f90bf9cea7','27d73dd63c9eaf6e','fb46ba5471dd0d54','1d314b7259a2999e','a8e64d06e46b1a20',
   'b08139178d29d13e','352c944c04e9f604','55699a4cd3c15fa1','100340ad2c04a156','d46e3a68fb86796b','98f885c7c9b3ff18', -- Rüdesheim (18)
   '650baa6e4565731e','d943a0f9f670893a','87fb74aa545c40b5','2c93b68bf72db4d7','38b40f5262731fad','76fe086687552d3a',
   'eeb6ac04cca11e03','049b10cb1e12c520','7c7fc86b0c7608ea','e5466ff049ec5844','79ad40b87c991423','3d2a08daa7de1b48'); -- Hochheim (12)
update public.rheingau_pages set transport_type = 'camper_stop' where page_id in
  ('664cf542a01067b9','04442ac804f220a9','46f7d3b1e6e28537','e71582666f981ce5','c04bbdce29b7130c',
   '8a3f8b295a655f9e','5df645a6fb2b9253','7b5a5ba0609c6d39','1b79abfc97e06a67','02cbd7b07fa31082');
update public.rheingau_pages set transport_type = 'ebike_charging' where page_id in
  ('121de28e26497bdd','53d76491c0761cba','1b5711687bb5a02d','abd30e392ac13640','1a7b86d27e3e41b0',
   '9a4f9757a37f4f36','4ed5d485611f3b2f','8512a27c33c01842');
update public.rheingau_pages set transport_type = 'taxi' where page_id in ('dacd784b7334ca2f');

-- City for 7 transport pages whose contact address is the operator's office outside the Rheingau
-- (so the DC2-132 postcode backfill left city NULL). Taken from the page's `cities` column. Broader fix: DC2-150.
update public.rheingau_pages set city = 'Lorch', city_source = 'manual_review' where page_id in ('702dcb039e17e381','b41597e11a5f6ed7');
update public.rheingau_pages set city = 'Rüdesheim am Rhein', city_source = 'manual_review' where page_id in ('78947ea509e4a277','36832d6eaf4aa899');
update public.rheingau_pages set city = 'Flörsheim am Main', city_source = 'manual_review' where page_id = '6bb7fdbd22d19e9e';
update public.rheingau_pages set city = 'Oestrich-Winkel', city_source = 'manual_review' where page_id = 'b270064a6d75f3df';
update public.rheingau_pages set city = 'Eltville am Rhein', city_source = 'manual_review' where page_id = 'bc68fa8a6f7a6434';
