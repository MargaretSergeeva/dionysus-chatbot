-- YouTrack: DC2-119 (semantic search), DC2-142 (active pages only, 28.09.2026)
-- Pure semantic search over rheingau_rag_chunks_v2. Only chunks of active pages (rheingau_pages.is_active),
-- so deactivated pages (e.g. test pages, form confirmations) are never returned.
CREATE OR REPLACE FUNCTION public.match_rheingau_chunks(query_embedding vector, match_count integer DEFAULT 10, match_threshold double precision DEFAULT 0.0)
RETURNS TABLE(chunk_id text, page_id text, section_type text, section_title text, chunk_text text, similarity double precision)
LANGUAGE sql STABLE AS $$
  SELECT c.chunk_id, c.page_id, c.section_type, c.section_title, c.chunk_text,
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM rheingau_rag_chunks_v2 c
  JOIN rheingau_pages rp ON rp.page_id = c.page_id
  WHERE c.embedding IS NOT NULL
    AND rp.is_active
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
$$;
