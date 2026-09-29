#!/usr/bin/env python3
"""
Build a static, plain-HTML wine page from the Supabase view wines_enriched, so a crawler
(Gastbot's own RAG) can read the wines until the wine upload to the platform works.

  export SUPABASE_URL=https://uywsaicdejkrozllalez.supabase.co
  export SUPABASE_SERVICE_KEY=...          # secret key (sb_secret_...) or legacy service_role key
  python scripts/build_wine_page.py                    # writes site/wines/index.html + site/wines/table/index.html
  python scripts/build_wine_page.py --from-json rows.json   # test without Supabase

One block per wine (a heading + fact lines), because a crawler cuts pages into passages: each wine
should stay together. NULL fields are left out, never written as "unknown".
The fields are the ones the bot uses from the wine view (see prompts/modules/2-sources/2.4_wines.md).
"""
import argparse, html, json, os, sys
from datetime import date
from pathlib import Path
import requests

COLUMNS = ["weinname", "erzeuger", "erzeuger_ort", "rebsorte_normalized", "weinart_normalized", "dryness_de",
           "body_de", "qualitaetsstufe", "lage_weinberg", "jahrgang", "praemierung", "bewertung", "alkohol_pct",
           "quelle_url"]
# label shown on the page  ->  column
FACTS = [("Weingut", "erzeuger"), ("Ort", "erzeuger_ort"), ("Rebsorte", "rebsorte_normalized"),
         ("Weinart", "weinart_normalized"), ("Geschmacksrichtung", "dryness_de"), ("Körper", "body_de"),
         ("Qualitätsstufe", "qualitaetsstufe"), ("Lage", "lage_weinberg"), ("Jahrgang", "jahrgang"),
         ("Prämierung", "praemierung"), ("Bewertung", "bewertung"), ("Alkohol", "alkohol_pct")]


def fetch(base, key):
    headers = {"apikey": key}
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    rows, start = [], 0
    while True:
        r = requests.get(f"{base}/rest/v1/wines_enriched?select={','.join(COLUMNS)}&order=erzeuger,weinname",
                         headers={**headers, "Range": f"{start}-{start + 999}"}, timeout=60)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            return rows
        start += 1000


def fmt(col, v):
    if col == "alkohol_pct":
        return f"{float(v):g} % vol"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def render(rows):
    out = ["<!doctype html>", '<html lang="de"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           "<title>Rheingau Weinverzeichnis</title>",
           "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}"
           "h2{margin:1.6rem 0 .2rem;font-size:1.1rem}ul{margin:.2rem 0;padding-left:1.2rem}</style></head><body>",
           "<h1>Rheingau Weinverzeichnis</h1>",
           f"<p>{len(rows)} Weine aus dem Rheingau mit Weingut, Rebsorte, Geschmacksrichtung und Auszeichnungen. "
           f"Stand: {date.today().strftime('%d.%m.%Y')}.</p>"]
    for w in rows:
        name = (w.get("weinname") or "").strip()
        if not name:
            continue
        maker = (w.get("erzeuger") or "").strip()
        out.append(f"<section><h2>{html.escape(name)}" + (f" – {html.escape(maker)}" if maker else "") + "</h2><ul>")
        for label, col in FACTS:
            v = w.get(col)
            if v is None or str(v).strip() == "":
                continue
            out.append(f"<li>{label}: {html.escape(fmt(col, v))}</li>")
        if w.get("quelle_url"):
            u = html.escape(w["quelle_url"], quote=True)
            out.append(f'<li>Quelle: <a href="{u}">{u}</a></li>')
        out.append("</ul></section>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


TABLE_TEMPLATE = Path(__file__).with_name("wine_table_template.html")


def render_table(rows):
    """Page for people: searchable, filterable table (JS). noindex — the crawler page stays /wines/."""
    data = json.dumps([{c: w.get(c) for c in COLUMNS if c != "quelle_url"} for w in rows if (w.get("weinname") or "").strip()],
                      ensure_ascii=False).replace("</", "<\\/")
    return (TABLE_TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data)
            .replace("__COUNT__", str(len(rows))).replace("__DATE__", date.today().strftime("%d.%m.%Y")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json", help="read rows from a JSON file instead of Supabase (test)")
    ap.add_argument("--out", default="site/wines/index.html")
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
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(rows), encoding="utf-8")
    print(f"{len(rows)} wines -> {path}")
    tpath = path.parent / "table" / "index.html"
    tpath.parent.mkdir(parents=True, exist_ok=True)
    tpath.write_text(render_table(rows), encoding="utf-8")
    print(f"{len(rows)} wines -> {tpath}")


if __name__ == "__main__":
    main()
