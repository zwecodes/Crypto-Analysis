"""
AI-generated strategy explanations using an LLM API (Groq, free tier).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


def test_llm_call():
    response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "In one sentence, explain what RSI measures in trading."}
    ],
)
    return response.choices[0].message.content


if __name__ == "__main__":
    result = test_llm_call()
    print(result)