#!/usr/bin/env python3
"""Check that every prompt module in a build has at least one test (DC2-A-132, DC2-140).

Test sets live in evaluation/<target>_*_questions.csv. The `modules` column lists module codes
separated by ';':  C04 = core '04', B03 = 'BLOCK 03', A02a = adapter '02a',
PLATFORM:<builtin> = a Gastbot built-in from prompts/platform/gastbot_baseline.yaml.
Compact modules (gastbot_compact) are counted by the codes in their `covers` list.

Fails when a module of the build has no test, or when a test names an unknown code.

Usage: python scripts/check_test_coverage.py --target gastbot --tests evaluation/gastbot_v1_questions.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from assemble_prompt import PROMPTS, TARGETS, load_modules, load_yaml, select

PLATFORM_CODES = {"reply_translation", "do_not_translate", "links_manager", "current_time"}


def module_code(label: str) -> str:
    if label.startswith("BLOCK "):
        return "B" + label.removeprefix("BLOCK ")
    if label[:2].isdigit() and len(label) > 2:
        return "A" + label
    return "C" + label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    args = parser.parse_args()

    gate = load_yaml(path=PROMPTS / "gate.yaml")
    modules = [m for m in select(modules=load_modules(), target=args.target, gate=gate) if m.label or m.covers]
    build_codes = {}
    for m in modules:
        for code in (m.covers or [module_code(label=m.label)]):
            if code in build_codes:
                raise SystemExit(f"code {code} is covered by two modules: {build_codes[code].id}, {m.id}")
            build_codes[code] = m

    with args.tests.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts = {code: 0 for code in build_codes}
    errors = []
    for row in rows:
        for code in filter(None, row["modules"].split(";")):
            if code.startswith("PLATFORM:"):
                if code.removeprefix("PLATFORM:") not in PLATFORM_CODES:
                    errors.append(f"{row['id']}: unknown platform code '{code}'")
                continue
            if code not in build_codes:
                errors.append(f"{row['id']}: module '{code}' is not in the {args.target} build")
                continue
            counts[code] += 1

    errors += [f"module {code} ({build_codes[code].title}) has no test" for code, n in counts.items() if n == 0]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{args.target}: {len(rows)} tests cover all {len(build_codes)} modules")
    for code, n in sorted(counts.items()):
        print(f"  {code:5} {n:3}  {build_codes[code].title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
