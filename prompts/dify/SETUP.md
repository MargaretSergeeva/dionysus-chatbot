# Dify setup for the test runs (Margarita's track)

The runner (`scripts/eval/dify_runner.py`) sends the prompt as an **input variable**, so a run always tests the committed prompt file, not whatever is saved in the Dify editor. This is the same mechanism as the CI smoke test (`scripts/dify_smoke_test.py`).

## One-time, in the Dify console (cannot be done from the repo)

1. **Create the app**: Studio → Create from blank → **Chatbot** (Chatflow also works; the API call is the same `chat-messages`).
2. **Add an input variable**: name `system_prompt`, type **Paragraph**, *not* required for the editor but always sent by the runner. Raise the max length above the prompt size (`prompts/dist/full/system_prompt.md` is ~18,000 characters; the default limit can be lower — check).
3. **Instruction (system prompt) field**: the single line `{{system_prompt}}`.
4. **Model**: pick the model and settings you want to test and **write them down** in the run notes — model and temperature change answers as much as the prompt.
5. **Knowledge**: attach the Dify knowledge base. Note what is in it; Gastbot answers from rheingau.com + PDFs, so differences in results are partly retrieval, not the prompt.
6. **Publish**, then App → **API Access**: copy the **API Server** URL (cloud: `https://api.dify.ai/v1`) and create a **Service API key** (`app-…`).

## On the machine that runs the tests

```bash
export DIFY_API_KEY=app-xxxxxxxx                    # never commit this
export DIFY_BASE_URL=https://api.dify.ai/v1         # or your own host
python scripts/eval/dify_runner.py --version v1.0 \
    --prompt-file prompts/dify/prompt-v.1.0_Dify.md --prompt-tag prompt-v.1.0_Dify --limit 3   # try 3 first
python scripts/eval/dify_runner.py --version v1.0 --prompt-file … --prompt-tag …               # all 125
```

Output: `evaluation/runs/margarita/dify/v1.0__<date>.csv` + `.meta.json`, same format as Vova's intake. Then `review_xlsx.py fill` and `judge.py` work on it unchanged. A failed row stays empty; rerun the same command to retry only those.

Multi-turn rows: the earlier `User:` turns are replayed in one Dify conversation; the recorded assistant turns in the CSV are placeholders and are not used.

For a CI/GitHub run later: `DIFY_API_KEY` as a repository secret (the smoke test already uses that name).
