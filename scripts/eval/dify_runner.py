#!/usr/bin/env python3
"""Run the fixed question set against the Dify app -> canonical run CSV (same format as intake.py).

  DIFY_API_KEY=... python scripts/eval/dify_runner.py --version v1.0 --prompt-file prompts/dify/prompt-v.1.0_Dify.md \\
        --prompt-tag prompt-v.1.0_Dify [--limit N] [--ids GB1-001,GB1-002] [--dry-run]

The prompt text is sent as an input variable of the Dify app (default `system_prompt`, same mechanism as
scripts/dify_smoke_test.py), so the run tests exactly the committed prompt file, not whatever is saved in Dify.
Each question starts a fresh conversation. Multi-turn rows: the `User:` turns of `context` are replayed first in the
same conversation (the recorded assistant turns are placeholders, Dify's own replies are used), then `question`.
Resumable: answers already in the output CSV are kept; failed rows are left empty and reported.
Env: DIFY_API_KEY (required), DIFY_BASE_URL (default https://api.dify.ai/v1), DIFY_PROMPT_VARIABLE (default system_prompt).
Output: evaluation/runs/margarita/dify/<ver>__<date>.csv + .meta.json (prompt sha256, base URL, failures, latency).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import ROOT, load_questions, read_table, run_stem, sha256, write_csv

BASE = os.environ.get("DIFY_BASE_URL", "https://api.dify.ai/v1").rstrip("/")
VAR = os.environ.get("DIFY_PROMPT_VARIABLE", "system_prompt")


def call(key: str, query: str, prompt: str, conversation_id: str, user: str) -> tuple[str, str]:
    body = {"inputs": {VAR: prompt}, "query": query, "response_mode": "blocking",
            "conversation_id": conversation_id, "user": user}
    req = urllib.request.Request(f"{BASE}/chat-messages", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode())
            return d.get("answer", "").strip(), d.get("conversation_id", "")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"cannot reach {BASE}: {e}")


def user_turns(context: str) -> list[str]:
    """`User: a | Assistant: b | User: c | Assistant: d` -> [a, c]."""
    return [m.strip() for m in re.findall(r"User:\s*(.*?)(?=\s*\|\s*Assistant:|$)", context, flags=re.S)]


def run_one(key: str, prompt: str, q: dict, tag: str) -> dict:
    t0, cid, user = time.time(), "", f"eval-{tag}-{q['id']}"
    for turn in user_turns(q.get("context", "")):
        _, cid = call(key, turn, prompt, cid, user)
    ans, _ = call(key, q["question"], prompt, cid, user)
    if not ans:
        raise RuntimeError("empty answer")
    return {"answer": ans, "seconds": round(time.time() - t0, 1)}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", required=True, help="e.g. v1.0 -> track margarita/dify/v1.0")
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--prompt-tag", required=True)
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--limit", type=int)
    p.add_argument("--ids", help="comma-separated question IDs")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--dry-run", action="store_true", help="show what would be sent, no API calls")
    a = p.parse_args()

    prompt = a.prompt_file.read_text(encoding="utf-8")
    qs = [q for q in load_questions() if q.get("origin") != "retired"]
    if a.ids:
        want = set(a.ids.split(","))
        qs = [q for q in qs if q["id"] in want]
    if a.limit:
        qs = qs[: a.limit]
    stem = run_stem("margarita/dify", a.version, a.date)
    out, meta_p = Path(f"{stem}.csv"), Path(f"{stem}.meta.json")
    done = {r["question_id"]: r for r in read_table(out)} if out.exists() else {}
    todo = [q for q in qs if not done.get(q["id"], {}).get("answer")]
    print(f"{len(qs)} questions, {len(todo)} to run, prompt {len(prompt)} chars, base {BASE}, variable {VAR}")
    if a.dry_run:
        for q in todo[:3]:
            print(q["id"], user_turns(q.get("context", "")), "->", q["question"][:80])
        return
    key = os.environ.get("DIFY_API_KEY") or sys.exit("DIFY_API_KEY is not set")

    failures, secs = {}, []

    def work(q):
        try:
            return q["id"], run_one(key, prompt, q, a.version), None
        except Exception as e:                        # noqa: BLE001 — record and continue
            return q["id"], None, str(e)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for n, (i, res, err) in enumerate(ex.map(work, todo), 1):
            q = next(x for x in qs if x["id"] == i)
            if err:
                failures[i] = err
                print(f"[{n}/{len(todo)}] {i} FAILED: {err[:120]}")
                continue
            done[i] = {"question_id": i, "question": q["question"], "answer": res["answer"]}
            secs.append(res["seconds"])
            write_csv(out, [done[k] for k in sorted(done)], ["question_id", "question", "answer"])
            print(f"[{n}/{len(todo)}] {i} ok ({res['seconds']}s)")

    missing = sorted(set(q["id"] for q in qs) - {i for i, r in done.items() if r.get("answer")})
    meta = {"track": "margarita/dify", "version": a.version, "date": a.date, "prompt_tag": a.prompt_tag,
            "prompt_file": str(a.prompt_file.resolve().relative_to(ROOT)) if a.prompt_file.resolve().is_relative_to(ROOT) else a.prompt_file.name,
            "prompt_sha256": sha256(a.prompt_file), "dify_base_url": BASE, "prompt_variable": VAR,
            "rows": len(done), "missing_ids": missing, "failures": failures,
            "avg_seconds": round(sum(secs) / len(secs), 1) if secs else None, "warnings": []}
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{out}: {len(done)} rows, {len(missing)} missing" + (" — rerun to retry failures" if missing else ""))


if __name__ == "__main__":
    main()
