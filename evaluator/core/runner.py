from concurrent.futures import ThreadPoolExecutor, as_completed
from litellm import completion, ModelResponse
from typing import cast
from google.genai import types
from core.config import client, logger

def call_model(model, question):
  if model["provider"] == "google":
    response = client.models.generate_content(
      model=model["model"],
      contents=question,
      config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.HIGH)
      ),
    )
    return model["model"], response.text
  elif model["provider"] == "litellm":
    messages = [{"role": "user", "content": question}]
    response = cast(ModelResponse, completion(model=model["model"], messages=messages))
    return model["model"], response.choices[0].message.content
  else:
    raise ValueError(f"Unsupported provider: {model['provider']}")


def run_models(models, question) -> tuple[list[str], list[str]]:
  answers = []
  competitors = []

  with ThreadPoolExecutor() as executor:
    futures = {executor.submit(call_model, model, question): model for model in models}
    for future in as_completed(futures):
      model = futures[future]
      try:
        name, text = future.result()
        if text is None:
          logger.warning("Model %s returned no content, skipping", name)
        else:
          answers.append(text)
          competitors.append(name)
          logger.info("Model %s succeeded", name)
      except Exception as e:
        logger.error("Model %s failed: %s", model["model"], e)

  return answers, competitors
