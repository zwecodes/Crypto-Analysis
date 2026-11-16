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


def _load_features(days_back: int = 180):
    df = get_btc_data_extended(days_back=days_back)
    df = build_feature_dataframe(df)
    return df.dropna().reset_index(drop=True)


def _simulate(df, strategy):
    """Run one strategy over df. Returns the closed trades in time order.

    Each trade also carries private fields (_exit_time, _pct) that are used to
    cut the trade list at any end date; they are removed before storing.
    """
    position = None
    trades = []

    for _, row in df.iterrows():
        if position is None and strategy["buy_rule"](row):
            position = {"entry_date": row["open_time"], "entry_price": row["close"]}
        elif position is not None and strategy["sell_rule"](row):
            exit_price = row["close"]
            pct_change = (exit_price - position["entry_price"]) / position["entry_price"]

            trades.append({
                "entry_date": str(position["entry_date"]),
                "exit_date": str(row["open_time"]),
                "entry_price": round(position["entry_price"], 2),
                "exit_price": round(exit_price, 2),
                "return_pct": round(pct_change * 100, 2),
                "_exit_time": row["open_time"],
                "_pct": pct_change,
            })
            position = None

    return trades


def _summarize(strategy_id, trades, start_date, end_date, starting_balance):
    balance = starting_balance
    balance_history = [starting_balance]
    for t in trades:
        balance *= (1 + t["_pct"])
        balance_history.append(balance)

    clean = [{k: v for k, v in t.items() if not k.startswith("_")} for t in trades]
    num_trades = len(clean)
    winning_trades = [t for t in clean if t["return_pct"] > 0]
    win_rate = round(len(winning_trades) / num_trades * 100, 2) if num_trades > 0 else 0.0

    return {
        "strategy_id": strategy_id,
        "start_date": start_date,
        "end_date": end_date,
        "starting_balance": starting_balance,
        "ending_balance": round(balance, 2),
        "total_return_pct": round((balance - starting_balance) / starting_balance * 100, 2),
        "num_trades": num_trades,
        "win_rate_pct": win_rate,
        "sharpe_ratio": compute_sharpe_ratio(clean),
        "max_drawdown_pct": compute_max_drawdown(balance_history),
        "trades": clean,
    }


def run_backtest(strategy_id: str, starting_balance: float = 10000.0):
    strategy = get_strategy(strategy_id)

    if strategy["buy_rule"] is None:
        raise NotImplementedError(
            f"Strategy '{strategy_id}' has no rule-based logic (likely the ML signal strategy) — "
            "backtest it separately using predict.py's model output instead."
        )

    df = _load_features(days_back=180)
    start_date = str(df["open_time"].iloc[0].date())
    end_date = str(df["open_time"].iloc[-1].date())

    trades = _simulate(df, strategy)
    return _summarize(strategy_id, trades, start_date, end_date, starting_balance)


def run_backtests_for_end_dates(
    start_date: str = "2026-03-31",
    min_end_date: str = "2026-04-30",
    days_back: int = 240,
    starting_balance: float = 10000.0,
):
    """Backtest every rule-based strategy from start_date to each end date.

    Each strategy is simulated once over the whole period; the result for an end
    date uses only the trades closed on or before that date (the simulation only
    looks forward in time, so this equals a separate run ending on that date).
    Returns one result dict per (strategy, end date).
    """
    from datetime import date as _date, timedelta

    start = _date.fromisoformat(start_date)
    min_end = _date.fromisoformat(min_end_date)

    df = _load_features(days_back=days_back)
    df = df[df["open_time"].dt.date >= start].reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"No data on or after {start_date}")

    # Use only fully closed days, so results never change when the script is re-run:
    # drop the still-forming candle, and leave out the newest day if it is incomplete.
    df = df.iloc[:-1].reset_index(drop=True)
    last_ts = df["open_time"].iloc[-1]
    last_full_day = last_ts.date() if last_ts.hour == 23 else last_ts.date() - timedelta(days=1)
    df = df[df["open_time"].dt.date <= last_full_day].reset_index(drop=True)

    first_date = str(df["open_time"].iloc[0].date())
    if first_date != start_date:
        print(f"Warning: data starts on {first_date}, not {start_date}")

    end_dates = sorted({d for d in df["open_time"].dt.date if d >= min_end})
    results = []
    for strategy in STRATEGIES:
        if strategy["buy_rule"] is None:
            continue  # skip ml_signal — handled separately, not rule-based
        trades = _simulate(df, strategy)
        for end in end_dates:
            subset = [t for t in trades if t["_exit_time"].date() <= end]
            results.append(
                _summarize(strategy["id"], subset, first_date, str(end), starting_balance)
            )
    return results


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


if __name__ == "__main__":
    results = run_all_backtests()

    print(f"{'Strategy':<20} {'Return %':>10} {'Trades':>8} {'Win %':>8} {'Sharpe':>8} {'Max DD %':>10}")
    print("-" * 68)
    for r in results:
        print(f"{r['strategy_id']:<20} {r['total_return_pct']:>10} {r['num_trades']:>8} "
              f"{r['win_rate_pct']:>8} {r['sharpe_ratio']:>8} {r['max_drawdown_pct']:>10}")

    save_backtest_results(results)
    print("\nSaved to backtest_results.json")
