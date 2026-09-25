#!/usr/bin/env python3
"""
Dify smoke test for Dionysus's merged prompt.

Does NOT edit the Dify app's saved config (Dify's public API has no
supported endpoint for that). Instead it sends the freshly merged prompt
as an input variable on a normal chat call, so every push to main
exercises the latest prompt against a live Dify app and you can see the
reply in the GitHub Action log.

Requires your Dify app to expose an input variable that its system
prompt is templated from (default name: system_prompt -- rename via
DIFY_PROMPT_VARIABLE if your app uses a different one).

Env vars (set as GitHub Actions secrets/vars):
  DIFY_API_KEY        required -- app's Service API key (App > API Access)
  DIFY_BASE_URL        optional -- default https://api.dify.ai/v1
                        (use your own host if self-hosting Dify)
  DIFY_PROMPT_VARIABLE optional -- default "system_prompt"
  DIFY_TEST_MESSAGE    optional -- default "Welche trockenen Rieslinge empfiehlst du?"
  MERGED_PROMPT_PATH   optional -- default prompts/merged/system_prompt.md
"""

import os
import sys
import json
import urllib.request
import urllib.error

MERGED_PROMPT_PATH = os.environ.get(
    "MERGED_PROMPT_PATH", "prompts/merged/system_prompt.md"
)
DIFY_BASE_URL = os.environ.get("DIFY_BASE_URL", "https://api.dify.ai/v1").rstrip("/")
DIFY_PROMPT_VARIABLE = os.environ.get("DIFY_PROMPT_VARIABLE", "system_prompt")
DIFY_TEST_MESSAGE = os.environ.get(
    "DIFY_TEST_MESSAGE", "Welche trockenen Rieslinge empfiehlst du?"
)


def fail(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    api_key = os.environ.get("DIFY_API_KEY")
    if not api_key:
        fail("DIFY_API_KEY is not set. Add it as a GitHub Actions secret.")

    if not os.path.exists(MERGED_PROMPT_PATH):
        fail(
            f"{MERGED_PROMPT_PATH} not found. This script expects merge.py "
            "to have already produced the merged prompt (run it as an earlier "
            "step in the workflow, or check the path)."
        )

    with open(MERGED_PROMPT_PATH, "r", encoding="utf-8") as f:
        merged_prompt = f.read()

    print(f"Loaded merged prompt: {len(merged_prompt)} chars from {MERGED_PROMPT_PATH}")

    payload = {
        "inputs": {DIFY_PROMPT_VARIABLE: merged_prompt},
        "query": DIFY_TEST_MESSAGE,
        "response_mode": "blocking",
        "user": "ci-smoke-test",
    }

    req = urllib.request.Request(
        f"{DIFY_BASE_URL}/chat-messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        fail(f"Dify API returned {e.code}: {detail}")
        return
    except urllib.error.URLError as e:
        fail(f"Could not reach Dify at {DIFY_BASE_URL}: {e}")
        return

    answer = body.get("answer", "").strip()
    if not answer:
        fail(f"Dify responded with no 'answer' field. Full response: {body}")

    print("--- Dify replied ---")
    print(answer)
    print("--------------------")
    print("Smoke test passed: prompt round-tripped through Dify successfully.")


if __name__ == "__main__":
    main()
