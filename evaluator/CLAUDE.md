# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run main.py          # run the evaluator
uv run ruff check .     # lint
uv run ruff format .    # format
```

No test suite exists yet.

## Architecture

The evaluator poses a question to multiple LLMs in parallel and writes a judge prompt to `outputs/judge.txt` for ranking the responses.

**Flow** (`main.py`):
1. Load question from `prompts/kvstore.txt` if present; otherwise auto-generate via Gemma with high-thinking
2. `run_models()` — sends the question concurrently to all models in `evaluator/models.py`, returns `(answers, competitors)`
3. `build_judge_prompt()` — assembles numbered responses into a judge prompt string
4. Write prompt to `outputs/judge.txt`

**Package** (`core/`):
- `config.py` — env loading, Google `genai.Client`, shared `logger`
- `models.py` — list of `{provider, model}` dicts; edit here to add/remove competitors
- `runner.py` — `ThreadPoolExecutor` fan-out; supports `google` (via `google-genai`) and `litellm` providers
- `judge.py` — pure string builder for the judge prompt; no API calls
- `evaluate.py` — calls judge model and prints ranked results

**Prompts** (`prompts/`): input `.txt` files sent to competitor models. Add new challenges here.

**Outputs** (`outputs/`): `judge.txt` and `results.txt` are gitignored runtime artifacts.

**Planned direction** (`plan.md`): evolve into an interactive CLI with a manual mode (user pastes question) and automatic mode (model generates question).

## Style

- 2-space indentation (enforced by ruff)
- Python 3.12+, managed with `uv`

## Environment

Copy `.env.example` to `.env`. Key variables: `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`.
