import os
from rich import print as rprint
from google.genai import types
from core.config import client, logger
from core.models import MODELS
from core.runner import run_models
from core.judge import build_judge_prompt
from core.evaluate import evaluate_models

PROMPT_PATH = "prompts/kvstore.txt"

if os.path.exists(PROMPT_PATH):
  with open(PROMPT_PATH, "r") as file:
    question = file.read()
  logger.info("Using question from %s", PROMPT_PATH)
else:
  # No prompt file present — generate the question automatically
  request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. Answer only with the question, no explanation."
  response = client.models.generate_content(
    model="gemma-4-31b-it",
    contents=request,
    config=types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.HIGH)
    ),
  )
  question = response.text
  logger.info("Question generated automatically")

rprint(question)

answers, competitors = run_models(MODELS, question)

judge_prompt = build_judge_prompt(question, answers, competitors)

with open("outputs/judge.txt", "w") as file:
  file.write(judge_prompt)

rprint(competitors)

evaluate_models(competitors, judge_prompt)
