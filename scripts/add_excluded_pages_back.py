#!/usr/bin/env python3
"""
DC2-152: add the pages we had taken out (privacy, imprint, partner, press, newsletter, jobs)
back to the search data. They are listed in rheingau_excluded_registry; this scrapes them and writes
rheingau_pages -> rheingau_rag_chunks_v2 (with Cohere embeddings).

Run on a machine that can reach rheingau.com (the cloud workspace cannot).

  export SUPABASE_URL=https://uywsaicdejkrozllalez.supabase.co
  export SUPABASE_SERVICE_KEY=...        # secret key (sb_secret_...) or legacy service_role key
  export COHERE_API_KEY=...
  pip install requests beautifulsoup4

  python scripts/add_excluded_pages_back.py                 # dry run: fetch, show pages + chunks
  python scripts/add_excluded_pages_back.py --apply         # write pages, chunks, embeddings
  python scripts/add_excluded_pages_back.py --text-dir txt  # use txt/<page_id>.txt instead of fetching
                                                          # (paste the page text if a page can't be scraped)

Format matches the existing rows:
  page_id      = sha1(source_url)[:16]
  content_hash = md5(content)
  chunk_id     = <page_id>-<chunk_index:03d>, section 'Beschreibung' (type 'main'),
                 title prefixed to the first chunk, chunks of about 700-1000 characters.
The registry rows are NOT deleted here; do that after checking (see the printed SQL).
"""
import argparse, hashlib, os, re, sys, json
from datetime import datetime, timezone
import requests

EMBED_MODEL = "embed-multilingual-v3.0"
MAX_CHUNK = 1000
# registry rows to load: everything public except the internal newsletter pages
# and the frag-lisbeth Datenschutzhinweis (deliberately kept out)
REGISTRY_FILTER = (
    "or=(registry_category.in.(partner_area,press_area,newsletter,jobs),"
    "registry_category.eq.legal)&source_url=not.like.*/frag-lisbeth/*"
)


def env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing env var {name}")
    return v


def sb_headers(key, extra=None):
    h = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):  # legacy service_role JWT; new sb_secret_ keys go in apikey only
        h["Authorization"] = f"Bearer {key}"
    h.update(extra or {})
    return h


def page_id_for(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def fetch_text(url):
    from bs4 import BeautifulSoup
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (Dionysus ingest)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "nav", "header", "footer", "form", "noscript", "svg"]):
        t.decompose()
    root = soup.find("main") or soup.find(id=re.compile("content", re.I)) or soup.body or soup
    text = root.get_text("\n")
    return clean(text)


def clean(text):
    lines = [re.sub(r"[ \t ]+", " ", l).strip() for l in text.splitlines()]
    out = []
    for l in lines:
        if l or (out and out[-1]):
            out.append(l)
    return "\n".join(out).strip()


def split_chunks(title, text):
    """Paragraph-aware split into <= MAX_CHUNK characters; title prefixes chunk 0."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        while len(p) > MAX_CHUNK:  # very long paragraph: cut at a sentence/space
            cut = max(p.rfind(". ", 0, MAX_CHUNK), p.rfind(" ", 0, MAX_CHUNK))
            cut = cut + 1 if cut > 200 else MAX_CHUNK
            if cur:
                chunks.append(cur); cur = ""
            chunks.append(p[:cut].strip()); p = p[cut:].strip()
        if cur and len(cur) + 1 + len(p) > MAX_CHUNK:
            chunks.append(cur); cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        chunks.append(cur)
    if chunks and not chunks[0].startswith(title):
        chunks[0] = f"{title} {chunks[0]}"
    return chunks


def embed(texts, key):
    vecs = []
    for i in range(0, len(texts), 96):
        r = requests.post(
            "https://api.cohere.com/v1/embed",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": EMBED_MODEL, "input_type": "search_document", "texts": texts[i:i + 96],
                  "embedding_types": ["float"]},
            timeout=60)
        r.raise_for_status()
        vecs += r.json()["embeddings"]["float"]
    return vecs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write to Supabase (default: dry run)")
    ap.add_argument("--text-dir", help="read <dir>/<page_id>.txt instead of fetching the site")
    args = ap.parse_args()

    base, skey = env("SUPABASE_URL").rstrip("/"), env("SUPABASE_SERVICE_KEY")
    rows = requests.get(f"{base}/rest/v1/rheingau_excluded_registry?select=*&{REGISTRY_FILTER}",
                        headers=sb_headers(skey), timeout=30)
    rows.raise_for_status()
    rows = rows.json()
    print(f"{len(rows)} registry pages to load")
    now = datetime.now(timezone.utc).isoformat()

    pages, chunks = [], []
    for r in rows:
        url, title, pid = r["source_url"], r["title"], r["page_id"]
        if pid != page_id_for(url):
            print(f"  ! page_id differs from sha1(url) for {url}; keeping registry id {pid}")
        try:
            if args.text_dir:
                text = clean(open(os.path.join(args.text_dir, f"{pid}.txt"), encoding="utf-8").read())
            else:
                text = fetch_text(url)
        except Exception as e:
            print(f"  ! {url}: {e}"); continue
        if len(text) < 80:
            print(f"  ! {url}: almost no text ({len(text)} chars), skipped"); continue
        pages.append({
            "page_id": pid, "group_name": "Informationsseite", "page_type": "pages", "category": "pages",
            "primary_category_de": "Allgemeine Information", "tags": "Allgemeine Information",
            "title": title, "content": text, "source_url": url,
            "content_hash": hashlib.md5(text.encode()).hexdigest(), "last_crawled_at": now,
        })
        for i, c in enumerate(split_chunks(title, text)):
            chunks.append({"chunk_id": f"{pid}-{i:03d}", "page_id": pid, "chunk_index": i,
                           "section_index": 0, "section_chunk_index": i, "section_type": "main",
                           "section_title": "Beschreibung", "chunk_text": c})
        print(f"  {title}: {len(text)} chars, {sum(1 for c in chunks if c['page_id']==pid)} chunks")

    print(f"\n{len(pages)} pages, {len(chunks)} chunks")
    if not args.apply:
        for c in chunks[:3]:
            print("\n---", c["chunk_id"], "\n", c["chunk_text"][:300])
        print("\nDry run. Re-run with --apply to write.")
        return

    vecs = embed([c["chunk_text"] for c in chunks], env("COHERE_API_KEY"))
    for c, v in zip(chunks, vecs):
        c["embedding"] = "[" + ",".join(f"{x:.8f}" for x in v) + "]"

    up = {"Prefer": "resolution=merge-duplicates,return=minimal"}
    r = requests.post(f"{base}/rest/v1/rheingau_pages?on_conflict=page_id", headers=sb_headers(skey, up),
                      data=json.dumps(pages), timeout=60); r.raise_for_status()
    ids = ",".join(p["page_id"] for p in pages)
    requests.delete(f"{base}/rest/v1/rheingau_rag_chunks_v2?page_id=in.({ids})",
                    headers=sb_headers(skey), timeout=60).raise_for_status()
    for i in range(0, len(chunks), 50):
        r = requests.post(f"{base}/rest/v1/rheingau_rag_chunks_v2", headers=sb_headers(skey, up),
                          data=json.dumps(chunks[i:i + 50]), timeout=120); r.raise_for_status()
    print("written. Next: check in Supabase, then remove these pages from the registry:")
    print(f"  delete from rheingau_excluded_registry where page_id in ({', '.join(repr(p['page_id']) for p in pages)});")


if __name__ == "__main__":
    main()
