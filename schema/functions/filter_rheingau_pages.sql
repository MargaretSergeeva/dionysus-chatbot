-- YouTrack: DC2-A-96 (Chatbot architecture: data sources and query routing), issues DC2-131, DC2-132
--
-- Structured-filter retrieval, companion to match_rheingau_chunks (DC2-119).
--
-- Nullable-boolean discipline: every boolean param defaults to NULL, meaning
-- "don't filter on this flag." A true/false param only ever matches confirmed
-- rows in rheingau_pages — never a row where the flag itself is NULL (unknown).
-- This mirrors the amenity-flags convention from DC2-A-125: NULL = unverified,
-- never coerced to false. p_city follows the same rule and expects the
-- canonical value in rheingau_pages.city (DC2-132, ../data/plz_city_map.sql),
-- not the free-text, multi-value `cities` column.
--
-- Use for list/filter-style questions ("which hotels in Rüdesheim are
-- pet-friendly?") where semantic search over rheingau_rag_chunks_v2 cannot
-- guarantee a complete, exact-match result set.

CREATE OR REPLACE FUNCTION public.filter_rheingau_pages(
  p_category text DEFAULT NULL,
  p_page_type text DEFAULT NULL,
  p_city text DEFAULT NULL,
  p_pet_friendly boolean DEFAULT NULL,
  p_bike_friendly boolean DEFAULT NULL,
  p_wifi_available boolean DEFAULT NULL,
  p_parking_available boolean DEFAULT NULL,
  p_wheelchair_accessible boolean DEFAULT NULL,
  p_family_friendly boolean DEFAULT NULL,
  p_breakfast_included boolean DEFAULT NULL,
  p_nonsmoking boolean DEFAULT NULL,
  p_group_friendly boolean DEFAULT NULL,
  p_elevator_available boolean DEFAULT NULL,
  p_ev_charging_available boolean DEFAULT NULL,
  p_bike_rental_available boolean DEFAULT NULL,
  p_vegetarian_available boolean DEFAULT NULL,
  p_gluten_free_available boolean DEFAULT NULL,
  p_luggage_transport_available boolean DEFAULT NULL,
  p_drying_room_available boolean DEFAULT NULL,
  p_hiking_certified boolean DEFAULT NULL,
  p_accessibility_certified boolean DEFAULT NULL,
  p_limit integer DEFAULT 20
)
RETURNS TABLE (
  page_id text,
  title text,
  category text,
  page_type text,
  city text,
  source_url text,
  phones text[],
  emails text[],
  partner_links jsonb,
  pet_friendly boolean,
  bike_friendly boolean,
  wifi_available boolean,
  parking_available boolean,
  wheelchair_accessible boolean,
  family_friendly boolean,
  breakfast_included boolean,
  nonsmoking boolean,
  group_friendly boolean,
  elevator_available boolean,
  ev_charging_available boolean,
  bike_rental_available boolean,
  vegetarian_available boolean,
  gluten_free_available boolean,
  luggage_transport_available boolean,
  drying_room_available boolean,
  hiking_certified boolean,
  accessibility_certified boolean
)
LANGUAGE sql STABLE AS $$
  SELECT
    rp.page_id, rp.title, rp.category, rp.page_type, rp.city, rp.source_url,
    rp.phones, rp.emails, rp.partner_links,
    rp.pet_friendly, rp.bike_friendly, rp.wifi_available, rp.parking_available,
    rp.wheelchair_accessible, rp.family_friendly, rp.breakfast_included,
    rp.nonsmoking, rp.group_friendly, rp.elevator_available, rp.ev_charging_available,
    rp.bike_rental_available, rp.vegetarian_available, rp.gluten_free_available,
    rp.luggage_transport_available, rp.drying_room_available, rp.hiking_certified,
    rp.accessibility_certified
  FROM rheingau_pages rp
  WHERE rp.is_active
    AND (p_category IS NULL OR rp.category = p_category)
    AND (p_page_type IS NULL OR rp.page_type = p_page_type)
    AND (p_city IS NULL OR rp.city = p_city)
    AND (p_pet_friendly IS NULL OR rp.pet_friendly = p_pet_friendly)
    AND (p_bike_friendly IS NULL OR rp.bike_friendly = p_bike_friendly)
    AND (p_wifi_available IS NULL OR rp.wifi_available = p_wifi_available)
    AND (p_parking_available IS NULL OR rp.parking_available = p_parking_available)
    AND (p_wheelchair_accessible IS NULL OR rp.wheelchair_accessible = p_wheelchair_accessible)
    AND (p_family_friendly IS NULL OR rp.family_friendly = p_family_friendly)
    AND (p_breakfast_included IS NULL OR rp.breakfast_included = p_breakfast_included)
    AND (p_nonsmoking IS NULL OR rp.nonsmoking = p_nonsmoking)
    AND (p_group_friendly IS NULL OR rp.group_friendly = p_group_friendly)
    AND (p_elevator_available IS NULL OR rp.elevator_available = p_elevator_available)
    AND (p_ev_charging_available IS NULL OR rp.ev_charging_available = p_ev_charging_available)
    AND (p_bike_rental_available IS NULL OR rp.bike_rental_available = p_bike_rental_available)
    AND (p_vegetarian_available IS NULL OR rp.vegetarian_available = p_vegetarian_available)
    AND (p_gluten_free_available IS NULL OR rp.gluten_free_available = p_gluten_free_available)
    AND (p_luggage_transport_available IS NULL OR rp.luggage_transport_available = p_luggage_transport_available)
    AND (p_drying_room_available IS NULL OR rp.drying_room_available = p_drying_room_available)
    AND (p_hiking_certified IS NULL OR rp.hiking_certified = p_hiking_certified)
    AND (p_accessibility_certified IS NULL OR rp.accessibility_certified = p_accessibility_certified)
  ORDER BY rp.title
  LIMIT GREATEST(p_limit, 1);
$$;

COMMENT ON FUNCTION public.filter_rheingau_pages(
  text, text, text, boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean,
  boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean, integer
) IS
  'Structured-filter retrieval (DC2-131, city param DC2-132), companion to match_rheingau_chunks
   (DC2-119). Every boolean/city param left NULL is not filtered on; a true/false param only
   matches confirmed rows, never rows where the flag itself is NULL (unknown). p_city expects
   the canonical value in rheingau_pages.city (e.g. "Eltville-Erbach"), not free text.';
