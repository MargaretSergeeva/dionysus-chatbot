-- YouTrack: DC2-A-96 (Chatbot architecture: data sources and query routing), issue DC2-131
--
-- Hybrid retrieval: same semantic ranking as match_rheingau_chunks (DC2-119),
-- scoped to chunks whose page passes the same structured amenity/category
-- filters as filter_rheingau_pages.sql.
--
-- Use for combined queries that need both meaning and a hard constraint
-- ("recommend a nice pet-friendly hotel near Rüdesheim") — filter_rheingau_pages
-- alone can't rank by "nice", and match_rheingau_chunks alone can't guarantee
-- the pet-friendly constraint actually holds.

CREATE OR REPLACE FUNCTION public.match_rheingau_chunks_filtered(
  query_embedding vector,
  match_count integer DEFAULT 10,
  match_threshold double precision DEFAULT 0.0,
  p_category text DEFAULT NULL,
  p_page_type text DEFAULT NULL,
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
  p_accessibility_certified boolean DEFAULT NULL
)
RETURNS TABLE (
  chunk_id text,
  page_id text,
  section_type text,
  section_title text,
  chunk_text text,
  similarity double precision
)
LANGUAGE sql STABLE AS $$
  SELECT
    c.chunk_id,
    c.page_id,
    c.section_type,
    c.section_title,
    c.chunk_text,
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM rheingau_rag_chunks_v2 c
  JOIN rheingau_pages rp ON rp.page_id = c.page_id
  WHERE c.embedding IS NOT NULL
    AND rp.is_active
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
    AND (p_category IS NULL OR rp.category = p_category)
    AND (p_page_type IS NULL OR rp.page_type = p_page_type)
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
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
$$;

COMMENT ON FUNCTION public.match_rheingau_chunks_filtered IS
  'Hybrid retrieval (DC2-131): semantic ranking like match_rheingau_chunks (DC2-119), scoped to pages
   passing the same structured amenity/category filters as filter_rheingau_pages. Use for combined
   queries ("recommend a nice pet-friendly hotel near Rüdesheim").';
