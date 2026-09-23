"""
Core backtesting engine — simulates a strategy's buy/sell rules
against historical data, logs individual trades, and computes summary stats.
"""

from features import build_feature_dataframe
from data import get_btc_data_extended
from strategies import get_strategy
from strategies import STRATEGIES
import numpy as np 
import json


import numpy as np


def run_backtest(strategy_id: str, starting_balance: float = 10000.0):
    strategy = get_strategy(strategy_id)

    if strategy["buy_rule"] is None:
        raise NotImplementedError(
            f"Strategy '{strategy_id}' has no rule-based logic (likely the ML signal strategy) — "
            "backtest it separately using predict.py's model output instead."
        )

    df = get_btc_data_extended(days_back=180)
    df = build_feature_dataframe(df)
    df = df.dropna().reset_index(drop=True)

    start_date = str(df["open_time"].iloc[0].date())
    end_date = str(df["open_time"].iloc[-1].date())

    balance = starting_balance
    balance_history = [starting_balance]
    position = None
    trades = []

    for _, row in df.iterrows():
        if position is None and strategy["buy_rule"](row):
            position = {"entry_date": row["open_time"], "entry_price": row["close"]}
        elif position is not None and strategy["sell_rule"](row):
            exit_price = row["close"]
            pct_change = (exit_price - position["entry_price"]) / position["entry_price"]
            balance *= (1 + pct_change)
            balance_history.append(balance)

            trades.append({
                "entry_date": str(position["entry_date"]),
                "exit_date": str(row["open_time"]),
                "entry_price": round(position["entry_price"], 2),
                "exit_price": round(exit_price, 2),
                "return_pct": round(pct_change * 100, 2),
            })
            position = None

    num_trades = len(trades)
    winning_trades = [t for t in trades if t["return_pct"] > 0]
    win_rate = round(len(winning_trades) / num_trades * 100, 2) if num_trades > 0 else 0.0

    sharpe_ratio = compute_sharpe_ratio(trades)
    max_drawdown = compute_max_drawdown(balance_history)

    return {
        "strategy_id": strategy_id,
        "start_date": start_date,
        "end_date": end_date,
        "starting_balance": starting_balance,
        "ending_balance": round(balance, 2),
        "total_return_pct": round((balance - starting_balance) / starting_balance * 100, 2),
        "num_trades": num_trades,
        "win_rate_pct": win_rate,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown_pct": max_drawdown,
        "trades": trades,
    }


def compute_sharpe_ratio(trades, risk_free_rate: float = 0.0):
    if len(trades) < 2:
        return 0.0
    returns = np.array([t["return_pct"] for t in trades])
    excess_returns = returns - risk_free_rate
    if excess_returns.std() == 0:
        return 0.0
    return round(float(excess_returns.mean() / excess_returns.std()), 3)


def compute_max_drawdown(balance_history):
    balances = np.array(balance_history)
    running_max = np.maximum.accumulate(balances)
    drawdowns = (balances - running_max) / running_max
    return round(float(drawdowns.min() * 100), 2)

def run_all_backtests(starting_balance: float = 10000.0):
    results = []
    for strategy in STRATEGIES:
        if strategy["buy_rule"] is None:
            continue  # skip ml_signal — handled separately, not rule-based

        result = run_backtest(strategy["id"], starting_balance)
        results.append(result)

    return results

def save_backtest_results(results, path="backtest_results.json"):
    """Temporary local output until DB write is wired up with Backend."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2)

# if __name__ == "__main__":
#     results = run_all_backtests()

#     print(f"{'Strategy':<20} {'Return %':>10} {'Trades':>8} {'Win %':>8} {'Sharpe':>8} {'Max DD %':>10}")
#     print("-" * 68)
#     for r in results:
#         print(f"{r['strategy_id']:<20} {r['total_return_pct']:>10} {r['num_trades']:>8} "
#               f"{r['win_rate_pct']:>8} {r['sharpe_ratio']:>8} {r['max_drawdown_pct']:>10}")

if __name__ == "__main__":
    results = run_all_backtests()

    print(f"{'Strategy':<20} {'Return %':>10} {'Trades':>8} {'Win %':>8} {'Sharpe':>8} {'Max DD %':>10}")
    print("-" * 68)
    for r in results:
        print(f"{r['strategy_id']:<20} {r['total_return_pct']:>10} {r['num_trades']:>8} "
              f"{r['win_rate_pct']:>8} {r['sharpe_ratio']:>8} {r['max_drawdown_pct']:>10}")

    save_backtest_results(results)
    print("\nSaved to backtest_results.json")