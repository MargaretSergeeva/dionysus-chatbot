#!/usr/bin/env python3
"""Calibrate the judge against manual scores.

  sample:  python scripts/eval/calibrate.py sample --judge <x.judge.csv> [--n 10] [--seed 1]
           -> IDs to score manually first (stratified over the judge's score range, deterministic)
  compare: python scripts/eval/calibrate.py compare --judge <x.judge.csv> --manual <reviewed.xlsx|csv>
           -> exact / within-1 agreement, mean abs. error, bias (judge - manual), fix_type and check agreement, big misses

Scores are inverted (1 = super, 5 = bad). Adjust evaluation/rubric.md when bias or misses show a pattern; bump rubric_version.
"""
from __future__ import annotations

import argparse
import random
from collections import defaultdict
from pathlib import Path

from common import read_table


def num(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["sample", "compare"])
    p.add_argument("--judge", type=Path, required=True)
    p.add_argument("--manual", type=Path)
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    judge = {r["question_id"]: r for r in read_table(a.judge)}

    if a.cmd == "sample":
        by = defaultdict(list)
        for i, r in judge.items():
            by[r["score"]].append(i)
        rnd, pick, pools = random.Random(a.seed), [], [sorted(v) for _, v in sorted(by.items())]
        for v in pools:
            rnd.shuffle(v)
        while len(pick) < min(a.n, len(judge)):     # round-robin over score buckets
            for v in pools:
                if v and len(pick) < a.n:
                    pick.append(v.pop())
        print(" ".join(sorted(pick)))
        return

    manual = {r["question_id"]: r for r in read_table(a.manual) if num(r.get("score")) is not None}
    pairs = [(i, num(judge[i]["score"]), num(manual[i]["score"])) for i in manual if i in judge and num(judge[i]["score"]) is not None]
    if not pairs:
        raise SystemExit("no rows with both a judge score and a manual score")
    n = len(pairs)
    print(f"rows compared: {n}")
    print(f"exact: {sum(j == m for _, j, m in pairs) / n:.0%}   within ±1: {sum(abs(j - m) <= 1 for _, j, m in pairs) / n:.0%}")
    print(f"MAE: {sum(abs(j - m) for _, j, m in pairs) / n:.2f}   bias (judge - manual): {sum(j - m for _, j, m in pairs) / n:+.2f}  (+ = judge harsher)")
    for col in ("fix_type", "check_length", "check_link_at_end", "check_general_vs_specific"):
        both = [(judge[i].get(col, ""), manual[i].get(col, "")) for i in manual if i in judge and manual[i].get(col, "")]
        if both:
            print(f"{col}: {sum(x == y for x, y in both)}/{len(both)} agree")
    print("big misses (|diff| >= 2):")
    for i, j, m in sorted(pairs):
        if abs(j - m) >= 2:
            print(f"  {i}: judge {j}, manual {m} — {judge[i]['judge_notes'][:120]}")


if __name__ == "__main__":
    main()
