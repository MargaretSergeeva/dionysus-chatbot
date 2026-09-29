#!/usr/bin/env python3
"""Check that every prompt module in a build has at least one test (DC2-A-132, DC2-140).

Test sets live in evaluation/<target>_*_questions.csv. The `modules` column lists module codes
separated by ';':  the module label ('1.4', '3.3', '6'), or
PLATFORM:<builtin> = a Gastbot built-in from prompts/platform/gastbot_baseline.yaml.

Fails when a module of the build has no test, or when a test names an unknown code.

Usage: python scripts/check_test_coverage.py --target gastbot --tests evaluation/gastbot_v1_questions.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from assemble_prompt import PROMPTS, TARGETS, load_yaml, run_check, select

PLATFORM_CODES = {"reply_translation", "do_not_translate", "links_manager", "current_time"}


def module_code(module) -> str:
    return module.label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    args = parser.parse_args()

    gate = load_yaml(path=PROMPTS / "gate.yaml")
    baseline = load_yaml(path=PROMPTS / "platform" / "gastbot_baseline.yaml")
    modules = [m for m in select(modules=run_check(gate=gate, baseline=baseline), target=args.target, gate=gate) if m.label]
    build_codes = {module_code(module=m): m for m in modules}
    all_codes = {module_code(module=m) for m in run_check(gate=gate, baseline=baseline) if m.label}
    platform_codes = PLATFORM_CODES | set(baseline["builtins"]) | set(baseline["conflicts"])

    with args.tests.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts = {code: 0 for code in build_codes}
    errors = []
    for row in rows:
        for code in filter(None, row["modules"].split(";")):
            if code.startswith("PLATFORM:"):
                if code.removeprefix("PLATFORM:") not in platform_codes:
                    errors.append(f"{row['id']}: unknown platform code '{code}'")
                continue
            if code not in build_codes:
                if code not in all_codes:
                    errors.append(f"{row['id']}: unknown module code '{code}'")
                continue   # module exists but is not in this build (e.g. no data yet) — test counts for the other build
            counts[code] += 1

    errors += [f"module {code} ({build_codes[code].title}) has no test" for code, n in counts.items() if n == 0]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{args.target}: {len(rows)} tests cover all {len(build_codes)} modules")
    for code, n in sorted(counts.items(), key=lambda kv: [int(x) if x.isdigit() else 0 for x in kv[0].split('.')]):
        print(f"  {code:5} {n:3}  {build_codes[code].title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
