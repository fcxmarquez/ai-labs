from pydantic import BaseModel
from google.genai import types
from rich import print as rprint
import json

from core.config import client


class ResultItem(BaseModel):
  competitor: int
  justification: str


def evaluate_models(competitors, judge_prompt):
  response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=judge_prompt,
    config=types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.HIGH),
      response_mime_type="application/json",
      response_json_schema=list[ResultItem],
    ),
  )

  for rank_idx, result in enumerate(json.loads(response.text or "[]")):
    competitor = competitors[(result["competitor"]) - 1]
    rprint(f"{rank_idx + 1}. {competitor}: {result["justification"]} \n")
    rprint(result["competitor"])

  with open("outputs/results.txt", "w") as file:
    file.write(f"{response.text}")
