"""
AI-generated strategy explanations using Groq's free-tier LLM API.
Run once to generate pros/cons — not called live per-request.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from strategies import STRATEGIES
from backtest import run_backtest

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


def build_prompt(strategy, backtest_result):
    return f"""You are explaining a Bitcoin trading strategy to a non-technical user.

Strategy name: {strategy['name']}
Rule: {strategy['description']}

Historical backtest results (past 6 months):
- Total return: {backtest_result['total_return_pct']}%
- Number of trades: {backtest_result['num_trades']}
- Win rate: {backtest_result['win_rate_pct']}%
- Sharpe ratio: {backtest_result['sharpe_ratio']}
- Max drawdown: {backtest_result['max_drawdown_pct']}%

Write 2-3 short pros and 2-3 short cons of this strategy, based on these actual results.
Keep each point under 15 words. Be honest about tradeoffs (e.g. high return but high risk).
"""


def explain_strategy(strategy_id: str):
    strategy = next(s for s in STRATEGIES if s["id"] == strategy_id)
    backtest_result = run_backtest(strategy_id)

    prompt = build_prompt(strategy, backtest_result)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = explain_strategy("rsi_oversold")
    print(result)