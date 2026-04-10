import os
from rich import print as rprint
from google.genai import types
from config import client, logger
from models import MODELS
from runner import run_models
from judge import build_judge_prompt

if os.path.exists("manual.txt"):
  with open("manual.txt", "r") as file:
    question = file.read()
  logger.info("Using question from manual.txt")
else:
  # No manual.txt present — generate the question automatically
  request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. Answer only with the question, no explanation."
  response = client.models.generate_content(
    model="gemma-4-31b-it",
    contents=request,
    config=types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
  )
  question = response.text
  logger.info("Question generated automatically")

rprint(question)

answers, competitors = run_models(MODELS, question)

judge_prompt = build_judge_prompt(question, answers, competitors)

with open("judge.txt", "w") as file:
  file.write(judge_prompt)

rprint(competitors)
