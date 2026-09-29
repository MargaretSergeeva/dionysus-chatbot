#!/usr/bin/env python3
"""
Build a static, plain-HTML wine page from the Supabase view wines_enriched, so a crawler
(Gastbot's own RAG) can read the wines until the wine upload to the platform works.

  export SUPABASE_URL=https://uywsaicdejkrozllalez.supabase.co
  export SUPABASE_SERVICE_KEY=...          # secret key (sb_secret_...) or legacy service_role key
  python scripts/build_wine_page.py                    # writes site/wines/<winery>/, site/wines/index.html, site/wines/sitemap.xml, site/wines/table/
  python scripts/build_wine_page.py --from-json rows.json   # test without Supabase

One page per winery, one block per wine (a heading + fact lines), because a crawler cuts pages into
passages: each wine should stay together. Gastbot rejects pages over 10240 bytes of text, so large wineries
are split into parts (MAX_TEXT_BYTES). Gastbot imports the pages through wines/sitemap.xml. NULL fields are left out, never written as "unknown".
The fields are the ones the bot uses from the wine view (see prompts/modules/2-sources/2.4_wines.md).
"""
import argparse, html, json, os, re, sys
from datetime import date
from pathlib import Path
import requests

COLUMNS = ["weinname", "weingut", "ort", "rebsorte", "weinart", "geschmacksrichtung",
           "körper", "qualitätsstufe", "lage", "jahrgang", "prämierung", "bewertung", "alkohol",
           "quelle"]
# label shown on the page  ->  column
FACTS = [("Weingut", "weingut"), ("Ort", "ort"), ("Rebsorte", "rebsorte"),
         ("Weinart", "weinart"), ("Geschmacksrichtung", "geschmacksrichtung"), ("Körper", "körper"),
         ("Qualitätsstufe", "qualitätsstufe"), ("Lage", "lage"), ("Jahrgang", "jahrgang"),
         ("Prämierung", "prämierung"), ("Bewertung", "bewertung"), ("Alkohol", "alkohol")]


def fetch(base, key):
    headers = {"apikey": key}
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    rows, start = [], 0
    while True:
        r = requests.get(f"{base}/rest/v1/wines_enriched?select={','.join(COLUMNS)}&order=weingut,weinname",
                         headers={**headers, "Range": f"{start}-{start + 999}"}, timeout=60)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            return rows
        start += 1000


def fmt(col, v):
    if col == "alkohol":
        return f"{float(v):g} % vol"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


BASE_URL = "https://margaretsergeeva.github.io/dionysus-chatbot"
MAX_TEXT_BYTES = 8000   # Gastbot rejects pages whose extracted text exceeds 10240 UTF-8 bytes
SOURCE = "https://www.die-besten-weine-hessens.de/veranstaltung/weinfinder"
STYLE = ("<style>body{font:16px/1.5 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}"
         "h2{margin:1.6rem 0 .2rem;font-size:1.1rem}ul{margin:.2rem 0;padding-left:1.2rem}</style>")


def slug(s):
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "weingut"


def wine_block(w):
    name = (w.get("weinname") or "").strip()
    maker = (w.get("weingut") or "").strip()
    out = [f"<section><h2>{html.escape(name)}" + (f" – {html.escape(maker)}" if maker else "") + "</h2><ul>"]
    for label, col in FACTS:
        v = w.get(col)
        if v is None or str(v).strip() == "":
            continue
        out.append(f"<li>{label}: {html.escape(fmt(col, v))}</li>")
    out.append("</ul></section>")
    return "\n".join(out)


def text_bytes(fragment):
    return len(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).encode("utf-8"))


def page(title, body):
    return "\n".join(["<!doctype html>", '<html lang="de"><head><meta charset="utf-8">',
                      '<meta name="viewport" content="width=device-width, initial-scale=1">',
                      f"<title>{html.escape(title)}</title>", STYLE, "</head><body>", body, "</body></html>"]) + "\n"


def render_pages(rows):
    """One page per winery (split into parts if the text is too long for Gastbot) + an index page.
    Returns {relative path: html}. A crawler cuts pages into passages: each wine stays in one block."""
    today = date.today().strftime("%d.%m.%Y")
    by_maker = {}
    for w in rows:
        if (w.get("weinname") or "").strip():
            by_maker.setdefault((w.get("weingut") or "Unbekanntes Weingut").strip(), []).append(w)
    pages, index, used = {}, [], set()
    for maker in sorted(by_maker, key=str.lower):
        wines = by_maker[maker]
        ort = next((w.get("ort") for w in wines if w.get("ort")), "")
        parts, cur, size = [], [], 0
        for w in wines:
            b = wine_block(w)
            if cur and size + text_bytes(b) > MAX_TEXT_BYTES:
                parts.append(cur); cur, size = [], 0
            cur.append(b); size += text_bytes(b)
        parts.append(cur)
        base = slug(maker)
        while base in used:
            base += "-2"
        used.add(base)
        for i, blocks in enumerate(parts, 1):
            path = f"wines/{base}/" if i == 1 else f"wines/{base}-{i}/"
            suffix = f" (Teil {i} von {len(parts)})" if len(parts) > 1 else ""
            title = f"Weine – {maker}{suffix}"
            intro = (f"<h1>{html.escape(title)}</h1><p>Prämierte Weine von {html.escape(maker)}"
                     + (f" in {html.escape(ort)}" if ort else "") + f": Weingut, Rebsorte, Geschmacksrichtung und "
                     f"Auszeichnungen. Stand: {today}. Quelle: {SOURCE}</p>")
            pages[path + "index.html"] = page(title, intro + "\n" + "\n".join(blocks))
            index.append((path, title, len(blocks)))
    links = "\n".join(f'<li><a href="{BASE_URL}/{p}">{html.escape(t)}</a> ({n} Weine)</li>' for p, t, n in index)
    pages["wines/index.html"] = page("Weinverzeichnis – Weingüter",
                                     f"<h1>Weinverzeichnis – Weingüter</h1><p>{len(rows)} prämierte Weine von "
                                     f"{len(by_maker)} Weingütern. Stand: {today}.</p><ul>{links}</ul>")
    return pages, [p for p, _, _ in index]


def sitemap(paths):
    urls = "".join(f"<url><loc>{BASE_URL}/{p}</loc></url>" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')


TABLE_TEMPLATE = Path(__file__).with_name("wine_table_template.html")


def render_table(rows):
    """Page for people: searchable, filterable table (JS). noindex — the crawler page stays /wines/."""
    data = json.dumps([{c: w.get(c) for c in COLUMNS if c != "quelle"} for w in rows if (w.get("weinname") or "").strip()],
                      ensure_ascii=False).replace("</", "<\\/")
    return (TABLE_TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data)
            .replace("__COUNT__", str(len(rows))).replace("__DATE__", date.today().strftime("%d.%m.%Y")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json", help="read rows from a JSON file instead of Supabase (test)")
    ap.add_argument("--out", default="site", help="site folder published by GitHub Pages")
    args = ap.parse_args()
    if args.from_json:
        rows = json.load(open(args.from_json, encoding="utf-8"))
    else:
        for n in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
            if not os.environ.get(n):
                sys.exit(f"missing env var {n}")
        rows = fetch(os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_KEY"])
    if not rows:
        sys.exit("no wines returned — not writing an empty page")
    site = Path(args.out)
    pages, paths = render_pages(rows)
    for rel, text in pages.items():
        f = site / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    (site / "wines" / "sitemap.xml").write_text(sitemap(paths), encoding="utf-8")
    print(f"{len(rows)} wines -> {len(paths)} winery pages + index + wines/sitemap.xml in {site}")
    tpath = site / "wines" / "table" / "index.html"
    tpath.parent.mkdir(parents=True, exist_ok=True)
    tpath.write_text(render_table(rows), encoding="utf-8")
    print(f"{len(rows)} wines -> {tpath}")


if __name__ == "__main__":
    main()
