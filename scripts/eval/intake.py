#!/usr/bin/env python3
"""Intake: a run file that arrived via Telegram (Vova's table, or a Dify run) -> canonical CSV.

  python scripts/eval/intake.py <file.csv|xlsx> --track oksana/gastbot/v1.1 --prompt-tag prompt-v.1.1_Gastbot [--date 2026-10-02]

Validates: ID column present, all IDs in the fixed question set, no duplicates, no missing IDs, answers not empty,
question text (if present) equals the set. Errors stop the intake; warnings are written to the meta file.
Writes evaluation/runs/<owner>/<platform>/<ver>__<date>.csv (question_id,question,answer) + .meta.json
(track, prompt_tag, source file + sha256, counts, warnings). Every run is tied to a prompt tag.
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from common import ANSWER_ALIASES, ID_ALIASES, ROOT, TRACK_RE, load_questions, pick, read_table, run_stem, sha256, write_csv


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", type=Path)
    p.add_argument("--track", required=True, help="oksana/gastbot/<ver> or margarita/dify/<ver>")
    p.add_argument("--prompt-tag", required=True, help="git tag of the prompt used, e.g. prompt-v.1.1_Gastbot")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--allow-partial", action="store_true", help="accept a run that answers only some IDs")
    a = p.parse_args()

    if not TRACK_RE.match(a.track):
        sys.exit(f"track must look like oksana/gastbot/<ver> or margarita/dify/<ver>, got {a.track!r}")
    track, version = a.track.rsplit("/", 1)
    rows = read_table(a.file)
    if not rows:
        sys.exit("file is empty")
    idc, ac = pick(rows[0], ID_ALIASES), pick(rows[0], ANSWER_ALIASES)
    qc = pick(rows[0], ["question", "Question", "Frage"])
    if not idc or not ac:
        sys.exit(f"need an ID column {ID_ALIASES} and an answer column {ANSWER_ALIASES}; found {list(rows[0])}")

    qs = {q["id"]: q for q in load_questions()}
    errors, warnings, out, seen = [], [], [], set()
    for n, r in enumerate(rows, 2):
        i = r[idc].strip()
        if i not in qs:
            errors.append(f"row {n}: unknown question ID {i!r}")
            continue
        if i in seen:
            errors.append(f"row {n}: duplicate ID {i}")
            continue
        seen.add(i)
        ans = r[ac].strip()
        if not ans:
            warnings.append(f"{i}: empty answer")
        if qc and r[qc].strip() != qs[i]["question"].strip():
            warnings.append(f"{i}: question text differs from the set")
        out.append({"question_id": i, "question": qs[i]["question"], "answer": ans})
    missing = sorted(set(qs) - seen)
    if missing and not a.allow_partial:
        errors.append(f"{len(missing)} IDs missing (e.g. {missing[:5]}); use --allow-partial to accept")
    if errors:
        sys.exit("INTAKE FAILED\n" + "\n".join(errors[:30]))

    tag_ok = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "-q", "--verify", f"refs/tags/{a.prompt_tag}"],
                            capture_output=True).returncode == 0
    if not tag_ok:
        warnings.append(f"git tag {a.prompt_tag} does not exist yet — commit the prompt and tag it")

    stem = run_stem(track, version, a.date)
    out.sort(key=lambda r: r["question_id"])
    write_csv(Path(f"{stem}.csv"), out, ["question_id", "question", "answer"])
    meta = {"track": track, "version": version, "date": a.date, "prompt_tag": a.prompt_tag,
            "source_file": a.file.name, "source_sha256": sha256(a.file), "rows": len(out),
            "missing_ids": missing, "warnings": warnings}
    Path(f"{stem}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{Path(f'{stem}.csv').relative_to(ROOT)}: {len(out)} rows, {len(missing)} missing, {len(warnings)} warnings")
    for w in warnings[:15]:
        print("  warn:", w)


if __name__ == "__main__":
    main()
