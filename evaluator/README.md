# evaluator

A small tool for comparing LLM responses head-to-head. It poses a question to multiple models in parallel, then builds a judge prompt so another model can rank the answers.

## How it works

1. **Question** — reads from `manual.txt` if present; otherwise uses Gemma (with high-thinking) to auto-generate a challenging question.
2. **Run models** — sends the question concurrently to all models defined in `models.py` (Google models via `google-genai`, others via `litellm`/OpenRouter).
3. **Judge prompt** — assembles all responses into a structured prompt and writes it to `judge.txt`, ready to paste into any model for ranking.

## Setup

```bash
uv sync
cp .env.example .env   # add your API keys
```

Required keys in `.env`:

| Variable | Used for |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini / Gemma models |
| `OPENROUTER_API_KEY` | OpenRouter models (via litellm) |
| `OPENAI_API_KEY` | OpenAI models (via litellm, optional) |
| `GROQ_API_KEY` | Groq models (via litellm, optional) |

## Usage

```bash
# Auto-generate a question
uv run main.py

# Use your own question
echo "Your question here" > manual.txt
uv run main.py
```

Results are printed to the terminal and logged to `evaluator.log`. The judge prompt is written to `judge.txt`. This can be used to pass to a high intelligence model to rank the responses.

## Adding models

Edit `models.py`. Each entry needs a `provider` (`google` or `litellm`) and a `model` name:

```python
{"provider": "google", "model": "gemini-flash-latest"},
{"provider": "litellm", "model": "openrouter/openai/gpt-4o"},
```
