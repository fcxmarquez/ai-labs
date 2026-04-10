from litellm import completion
from google import genai
from google.genai import types
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from rich import print as rprint

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
  handlers=[
    logging.StreamHandler(),
    logging.FileHandler("evaluator.log"),
  ],
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)
# read the text from manual.txt
with open("manual.txt", "r") as file:
  manual = file.read()

request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]

# This will be for manual mode
# response = client.models.generate_content(
#   model="gemma-4-31b-it",
#   contents=request,
#   config=types.GenerateContentConfig(
#     thinking_config=types.ThinkingConfig(thinking_level="high")
#   ),
# )

# question = response.text
question = manual

rprint(question)

models = [
  {
    "provider": "google",
    "model": "gemini-flash-lite-latest",
  },
  {
    "provider": "google",
    "model": "gemini-flash-latest",
  },
  {
    "provider": "google",
    "model": "gemma-4-31b-it",
  },
  {
    "provider": "google",
    "model": "gemma-4-26b-a4b-it",
  },
  {
    "provider": "litellm",
    "model": "openrouter/minimax/minimax-m2.5:free",
  },
  {
    "provider": "litellm",
    "model": "openrouter/openai/gpt-oss-120b:free",
  },
]

messages = [{"role": "user", "content": question}]

def call_model(model):
  if model["provider"] == "google":
    response = client.models.generate_content(
      model=model["model"],
      contents=question,
      config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
      ),
    )
    return model["model"], response.text
  elif model["provider"] == "litellm":
    response = completion(model=model["model"], messages=messages)
    return model["model"], response.choices[0].message.content
  else:
    raise ValueError(f"Unsupported provider: {model['provider']}")

answers = []
competitors = []

with ThreadPoolExecutor() as executor:
  futures = {executor.submit(call_model, model): model for model in models}
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

together = ""
for index, answer in enumerate(answers):
  together += f"# Response from competitor {index + 1}\n\n"
  together += answer + "\n\n"

judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.

Here are the responses from each competitor:

{together}
"""

with open("judge.txt", "w") as file:
  file.write(judge)

rprint(competitors)
