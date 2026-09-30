"""Shared helpers for the evaluation tooling (test set, runs, review files, judge)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "evaluation"
QUESTIONS = EVAL / "gastbot_v1_questions.csv"
RUNS = EVAL / "runs"
JUDGE = EVAL / "judge"
REVIEW = EVAL / "review"
TEMPLATE = EVAL / "templates" / "review_template.xlsx"
RUBRIC = EVAL / "rubric.md"

REVIEWERS = ["Margarita", "Oksana"]
FIX_TYPES = ["prompt", "Vova", "data", "links"]
CHECKS = ["ok", "fail", "n/a"]
TRACK_RE = re.compile(r"^(oksana/gastbot|margarita/dify)/[\w.\-]+$")

ID_ALIASES = ["question_id", "id", "ID", "Question ID", "Frage-ID"]
ANSWER_ALIASES = ["answer", "actual_answer", "Answer", "Antwort", "response"]


def read_table(path: Path) -> list[dict]:
    """Read a CSV or XLSX (first sheet, first row = header) into a list of dicts of strings."""
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        head = [str(h).strip() if h is not None else "" for h in rows[0]]
        return [{h: ("" if v is None else str(v)) for h, v in zip(head, r) if h} for r in rows[1:] if any(v not in (None, "") for v in r)]
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def pick(row: dict, aliases: list[str]) -> str | None:
    for a in aliases:
        if a in row:
            return a
    return None


def load_questions(path: Path = QUESTIONS) -> list[dict]:
    return read_table(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rubric_version(path: Path = RUBRIC) -> str:
    m = re.search(r"^rubric_version:\s*(\S+)", path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "unknown"


def run_stem(track: str, version: str, date: str) -> Path:
    """evaluation/runs/<owner>/<platform>/<ver>__<date> (no suffix)."""
    owner, platform = track.split("/")
    return RUNS / owner / platform / f"{version}__{date}"


def load_meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
