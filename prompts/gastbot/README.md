# Gastbot prompts — Oksana's versions

Every prompt Oksana sends (Telegram) is saved here **as she sent it** and tagged.

- File: `prompts/gastbot/prompt-v.<X.Y>_Gastbot.md` (plain text of the Gastbot system prompt field)
- Commit message: `Gastbot prompt v.<X.Y> from Oksana (<date>)`
- Git tag on that commit: `prompt-v.<X.Y>_Gastbot` — the tag is what a run refers to (`intake.py --prompt-tag`)
- Track name of runs on this prompt: `oksana/gastbot/v<X.Y>`

Do not edit a tagged file; a change is a new version. These files are separate from the module-built prompt in `prompts/dist/` (`prompt-vX.Y` tags, Margarita's build system).
