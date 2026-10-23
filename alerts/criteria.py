"""
Rule checker for strategy alerts.

Evaluates the structured buy_criteria / sell_criteria from ml/strategies.py
against one row of indicator values, and implements "alert on change only":
a signal fires when the condition is true on the latest closed candle and was
false on the candle before it.
"""
import operator

OPERATORS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}


def evaluate_criteria(criteria, row):
    """Return True or False for one criteria dict against one row (dict or pandas row)."""
    if criteria is None:
        return False
    compare = OPERATORS.get(criteria["operator"])
    if compare is None:
        raise ValueError(f"Unsupported operator: {criteria['operator']}")

    left = row[criteria["indicator"]]
    if "compare_to" in criteria:
        right = row[criteria["compare_to"]]
    else:
        right = criteria["value"]

    if left is None or right is None:
        return False
    return bool(compare(left, right))


def check_signal(strategy, previous_row, current_row):
    """Return "BUY", "SELL" or None. Fires only when the condition changes to true."""
    for side, key in (("BUY", "buy_criteria"), ("SELL", "sell_criteria")):
        criteria = strategy.get(key)
        if criteria is None:
            continue
        now = evaluate_criteria(criteria, current_row)
        before = evaluate_criteria(criteria, previous_row)
        if now and not before:
            return side
    return None