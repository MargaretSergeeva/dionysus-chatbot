#!/usr/bin/env python3
"""Maintain the fixed question set (evaluation/gastbot_v1_questions.csv).

  columns   add the reference columns `expected_answer`, `key_facts`, `reviewer` (idempotent)
  assign    fill EMPTY `reviewer` cells 50/50 (Margarita/Oksana), balanced per category; existing
            assignments never change, so IDs stay stable across runs
  compare   compare the IDs / question texts of another file (Margarita's Excel, Rozaliia's 120) with the repo set

Question IDs are fixed: never renumber or delete a row; retire a row by setting `origin` to `retired`.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict

from common import QUESTIONS, REVIEWERS, ID_ALIASES, load_questions, pick, read_table, write_csv

NEW_COLS = ["expected_answer", "key_facts", "reviewer"]


def fields_of(rows):
    base = list(rows[0].keys())
    return base + [c for c in NEW_COLS if c not in base]


def cmd_columns(_):
    rows = load_questions()
    fields = fields_of(rows)
    for r in rows:
        for c in NEW_COLS:
            r.setdefault(c, "")
    write_csv(QUESTIONS, rows, fields)
    print(f"{len(rows)} rows, columns: {', '.join(NEW_COLS)}")


def cmd_assign(_):
    rows = load_questions()
    fields = fields_of(rows)
    for r in rows:
        r.setdefault("reviewer", "")
    load = Counter(r["reviewer"] for r in rows if r["reviewer"])
    cat_load = defaultdict(Counter)
    for r in rows:
        if r["reviewer"]:
            cat_load[r["category"]][r["reviewer"]] += 1
    for r in sorted((r for r in rows if not r["reviewer"]), key=lambda r: (r["category"], r["id"])):
        c = cat_load[r["category"]]
        # least-loaded within the category first, then overall; ties -> first name
        who = min(REVIEWERS, key=lambda n: (c[n], load[n], REVIEWERS.index(n)))
        r["reviewer"] = who
        c[who] += 1
        load[who] += 1
    write_csv(QUESTIONS, rows, fields)
    print(dict(load))


def cmd_compare(args):
    repo = {r["id"]: r for r in load_questions()}
    other = read_table(args.file)
    idc = pick(other[0], ID_ALIASES)
    qc = pick(other[0], ["question", "Question", "Frage"])
    if not idc:
        sys.exit(f"no ID column in {args.file} (looked for {ID_ALIASES}); columns: {list(other[0])}")
    theirs = {r[idc].strip(): r for r in other if r[idc].strip()}
    only_repo = sorted(set(repo) - set(theirs))
    only_theirs = sorted(set(theirs) - set(repo))
    print(f"repo: {len(repo)}  {args.file.name}: {len(theirs)}")
    print(f"only in repo ({len(only_repo)}):")
    for i in only_repo:
        print(f"  {i}  [{repo[i]['category']}] {repo[i]['question'][:90]}")
    print(f"only in {args.file.name} ({len(only_theirs)}): {only_theirs}")
    if qc:
        diff = [i for i in set(repo) & set(theirs) if repo[i]["question"].strip() != theirs[i][qc].strip()]
        print(f"same ID, different question text ({len(diff)}): {sorted(diff)}")
    print("\nDecide per row: keep (repo is the source of truth) or retire (origin=retired).")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("columns").set_defaults(fn=cmd_columns)
    s.add_parser("assign").set_defaults(fn=cmd_assign)
    c = s.add_parser("compare")
    c.add_argument("file", type=__import__("pathlib").Path)
    c.set_defaults(fn=cmd_compare)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
