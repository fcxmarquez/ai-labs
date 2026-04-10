def build_judge_prompt(question, answers, competitors) -> str:
  together = ""
  for index, answer in enumerate(answers):
    together += f"# Response from competitor {index + 1}\n\n"
    together += answer + "\n\n"

  return f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.

Here are the responses from each competitor:

{together}
"""
