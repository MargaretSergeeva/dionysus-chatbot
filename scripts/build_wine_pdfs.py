#!/usr/bin/env python3
"""
Build the wine catalog as a few PDFs for Gastbot's "Files" source (PDF only, max 5 MB per file, 20 files).
Same content and labels as the wine pages (build_wine_page.py): one block per wine, a heading + fact lines,
NULL fields left out. Wineries are never split across files.

  python scripts/build_wine_pdfs.py --from-json rows.json          # test without Supabase
  SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python scripts/build_wine_pdfs.py
Writes site/wines/pdf/weinverzeichnis-teil-N.pdf (published with GitHub Pages as well).
"""
import argparse, json, os, sys
from datetime import date
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
from build_wine_page import FACTS, SOURCE, fetch, fmt  # noqa: E402

FILES = 8  # leaves 12 of Gastbot's 20 file slots free
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def fonts():
    for name, f in (("Sans", "DejaVuSans.ttf"), ("Sans-Bold", "DejaVuSans-Bold.ttf")):
        try:
            pdfmetrics.registerFont(TTFont(name, FONT_DIR + f))
        except Exception:
            return "Helvetica", "Helvetica-Bold"
    return "Sans", "Sans-Bold"


def groups(rows, n):
    by_maker = {}
    for w in rows:
        if (w.get("weinname") or "").strip():
            by_maker.setdefault((w.get("weingut") or "Unbekanntes Weingut").strip(), []).append(w)
    makers = sorted(by_maker, key=str.lower)
    target = sum(len(v) for v in by_maker.values()) / n
    out, cur, size = [], [], 0
    for m in makers:
        if cur and size + len(by_maker[m]) / 2 > target and len(out) < n - 1:
            out.append(cur); cur, size = [], 0
        cur.append((m, by_maker[m])); size += len(by_maker[m])
    out.append(cur)
    return out


def build(rows, outdir):
    regular, bold = fonts()
    h1 = ParagraphStyle("h1", fontName=bold, fontSize=15, leading=19, spaceAfter=6)
    h2 = ParagraphStyle("h2", fontName=bold, fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4)
    h3 = ParagraphStyle("h3", fontName=bold, fontSize=10.5, leading=13, spaceBefore=6, spaceAfter=1)
    body = ParagraphStyle("b", fontName=regular, fontSize=9.5, leading=12.5)
    today = date.today().strftime("%d.%m.%Y")
    outdir.mkdir(parents=True, exist_ok=True)
    parts = groups(rows, FILES)
    paths = []
    for i, part in enumerate(parts, 1):
        first, last = part[0][0], part[-1][0]
        title = f"Weinverzeichnis Teil {i} von {len(parts)}: {first} bis {last}"
        story = [Paragraph(escape(title), h1),
                 Paragraph(escape(f"Prämierte Weine mit Weingut, Ort, Rebsorte, Weinart, Geschmacksrichtung, "
                                  f"Qualitätsstufe, Lage, Jahrgang, Prämierung, Bewertung und Alkohol. "
                                  f"Stand: {today}. Quelle: {SOURCE}"), body)]
        for maker, wines in part:
            story.append(Paragraph(escape(f"Weingut: {maker}"), h2))
            for w in wines:
                block = [Paragraph(escape(f"{w['weinname'].strip()} – {maker}"), h3)]
                for label, col in FACTS:
                    v = w.get(col)
                    if v is None or str(v).strip() == "":
                        continue
                    block.append(Paragraph(escape(f"{label}: {fmt(col, v)}"), body))
                story.append(KeepTogether(block))
        story.append(Spacer(1, 0.3 * cm))
        path = outdir / f"weinverzeichnis-teil-{i}.pdf"
        SimpleDocTemplate(str(path), pagesize=A4, title=title, author="Dionysus",
                          leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm
                          ).build(story)
        paths.append((path, sum(len(w) for _, w in part), title))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json")
    ap.add_argument("--out", default="site/wines/pdf")
    a = ap.parse_args()
    if a.from_json:
        rows = json.load(open(a.from_json, encoding="utf-8"))
    else:
        for n in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
            if not os.environ.get(n):
                sys.exit(f"missing env var {n}")
        rows = fetch(os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_KEY"])
    for p, n, t in build(rows, Path(a.out)):
        print(f"{n:4d} wines  {p.stat().st_size // 1024:5d} KB  {p.name}  ({t})")


if __name__ == "__main__":
    main()
