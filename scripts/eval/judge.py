#!/usr/bin/env python3
"""Private LLM-as-judge (Claude API). Same rubric and output fields as the reviewer Excel.

  ANTHROPIC_API_KEY=... python scripts/eval/judge.py --run evaluation/runs/oksana/gastbot/v1.1__2026-10-02.csv [--limit N] [--model ...]

Input: canonical run CSV (+ its .meta.json) from intake.py or the Dify runner; questions + reference data from the
question set; rubric from evaluation/rubric.md. Output: evaluation/judge/<same path>.judge.csv and .judge.meta.json
(judge model, rubric version + sha256, question set sha256, token usage). Deterministic checks (must_include /
must_not_include, word count, link at end, numeric claims) run in code and are passed to the judge as facts.
Prices/dates/counts are never verified by the model: rows are flagged needs_manual.
Resumable: rows already in the output file are skipped.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

from common import CHECKS, EVAL, FIX_TYPES, JUDGE, QUESTIONS, ROOT, RUBRIC, load_meta, load_questions, read_table, rubric_version, sha256, write_csv

DEFAULT_MODEL = "claude-opus-5-5"
OUT_FIELDS = ["question_id", "score", "ideal_answer", "fix_type", "check_length", "check_link_at_end",
              "check_general_vs_specific", "needs_manual", "manual_reason", "judge_notes",
              "auto_must_include_missing", "auto_must_not_include_hit", "auto_words", "auto_link_at_end"]

URL_RE = re.compile(r"https?://\S+")
NUM_RE = re.compile(r"(\d+[.,]?\d*\s?(€|EUR|Euro|Uhr|%|km|m\b|Minuten|Stunden|Euro)|\b\d{1,2}\.\s?\d{1,2}\.(\s?\d{2,4})?|\b(19|20)\d{2}\b|\b\d{1,3}\s+(Weingüter|Weine|Betriebe|Veranstaltungen|Orte)\b)", re.I)

SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
        "ideal_answer": {"type": "string"},
        "fix_type": {"type": "string", "enum": [""] + FIX_TYPES},
        "check_length": {"type": "string", "enum": CHECKS},
        "check_link_at_end": {"type": "string", "enum": CHECKS},
        "check_general_vs_specific": {"type": "string", "enum": CHECKS},
        "needs_manual": {"type": "boolean"},
        "manual_reason": {"type": "string"},
        "judge_notes": {"type": "string"},
    },
    "required": ["score", "ideal_answer", "fix_type", "check_length", "check_link_at_end",
                 "check_general_vs_specific", "needs_manual", "manual_reason", "judge_notes"],
    "additionalProperties": False,
}


def auto_checks(q: dict, answer: str) -> dict:
    low = answer.lower()
    inc = [k.strip() for k in q.get("must_include", "").split(";") if k.strip()]
    exc = [k.strip() for k in q.get("must_not_include", "").split(";") if k.strip()]
    tail = answer.strip()[-250:]
    return {
        "must_include_missing": [k for k in inc if k.lower() not in low],
        "must_not_include_hit": [k for k in exc if k.lower() in low],
        "words": len(answer.split()),
        "link_at_end": bool(URL_RE.search(tail)),
        "numeric_claims": sorted({m.group(0) for m in NUM_RE.finditer(answer)})[:8],
    }


def user_prompt(q: dict, answer: str, auto: dict) -> str:
    ref = {k: q.get(k, "") for k in ("expected_behavior", "must_include", "must_not_include", "source_url", "expected_answer", "key_facts", "modules")}
    return (
        f"<question id=\"{q['id']}\" language=\"{q['language']}\">\n{q['question']}\n</question>\n"
        + (f"<earlier_turns>\n{q['context']}\n</earlier_turns>\n" if q.get("context") else "")
        + f"<reference>\n{json.dumps(ref, ensure_ascii=False, indent=1)}\n</reference>\n"
        f"<automatic_checks>\n{json.dumps(auto, ensure_ascii=False)}\n</automatic_checks>\n"
        f"<bot_answer>\n{answer}\n</bot_answer>\n\n"
        "Judge the bot answer with the rubric. Fill every field. Score is inverted (1 = super, 5 = bad). "
        "If the answer states a price, date, count or opening hour you cannot verify from the reference, set needs_manual = true and name it in manual_reason."
    )


def judge_row(client, model, system, q, answer, auto):
    resp = client.messages.create(
        model=model, max_tokens=4000, system=system,
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": user_prompt(q, answer, auto)}],
    )
    if resp.stop_reason == "refusal":
        return None, resp.usage
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text), resp.usage


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--limit", type=int)
    a = p.parse_args()

    import anthropic
    client = anthropic.Anthropic()
    system = RUBRIC.read_text(encoding="utf-8")
    qs = {q["id"]: q for q in load_questions()}
    run = read_table(a.run)
    if a.limit:
        run = run[: a.limit]

    rel = a.run.resolve().relative_to(EVAL / "runs")
    out = JUDGE / rel.parent / (rel.name.removesuffix(".csv") + ".judge.csv")
    meta_path = out.with_name(out.name.removesuffix(".csv") + ".meta.json")
    done = {r["question_id"]: r for r in read_table(out)} if out.exists() else {}
    tokens = {"input": 0, "output": 0, "cache_read": 0}
    run_meta_path = a.run.with_name(a.run.name.removesuffix(".csv") + ".meta.json")

    for n, r in enumerate(run, 1):
        i = r["question_id"]
        if i in done:
            continue
        q, answer = qs[i], r["answer"]
        auto = auto_checks(q, answer)
        try:
            res, usage = judge_row(client, a.model, system, q, answer, auto)
        except anthropic.APIStatusError as e:
            print(f"{i}: API error {e.status_code}, stopping (rerun to resume)", file=sys.stderr)
            break
        tokens["input"] += usage.input_tokens
        tokens["output"] += usage.output_tokens
        tokens["cache_read"] += getattr(usage, "cache_read_input_tokens", 0) or 0
        if res is None:
            res = {"score": "", "ideal_answer": "", "fix_type": "", "check_length": "", "check_link_at_end": "",
                   "check_general_vs_specific": "", "needs_manual": True, "manual_reason": "judge refused", "judge_notes": ""}
        if auto["numeric_claims"] and not res["needs_manual"]:
            res["needs_manual"], res["manual_reason"] = True, "numeric claims to verify: " + ", ".join(auto["numeric_claims"])
        res.update({"question_id": i, "auto_must_include_missing": ";".join(auto["must_include_missing"]),
                    "auto_must_not_include_hit": ";".join(auto["must_not_include_hit"]),
                    "auto_words": auto["words"], "auto_link_at_end": auto["link_at_end"]})
        done[i] = res
        write_csv(out, [done[k] for k in sorted(done)], OUT_FIELDS)     # write after every row: resumable
        print(f"[{n}/{len(run)}] {i} score={res['score']} manual={res['needs_manual']}")

    meta = {"judge_model": a.model, "rubric_version": rubric_version(), "rubric_sha256": sha256(RUBRIC),
            "question_set_sha256": sha256(QUESTIONS), "run_file": str(a.run.resolve().relative_to(ROOT)),
            "run_meta": load_meta(run_meta_path) if run_meta_path.exists() else None,
            "rows_judged": len(done), "tokens_this_invocation": tokens,
            "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
