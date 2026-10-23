import pytest

from criteria import check_signal, evaluate_criteria

RSI = {
    "id": "rsi_oversold",
    "buy_criteria": {"indicator": "rsi", "operator": "<", "value": 30},
    "sell_criteria": {"indicator": "rsi", "operator": ">", "value": 70},
}
CROSS = {
    "id": "ma_crossover",
    "buy_criteria": {"indicator": "ema_20", "operator": ">", "compare_to": "sma_50"},
    "sell_criteria": {"indicator": "ema_20", "operator": "<", "compare_to": "sma_50"},
}
ML = {"id": "ml_signal", "buy_criteria": None, "sell_criteria": None}


def test_fixed_value():
    assert evaluate_criteria(RSI["buy_criteria"], {"rsi": 25}) is True
    assert evaluate_criteria(RSI["buy_criteria"], {"rsi": 35}) is False


def test_compare_to_column():
    assert evaluate_criteria(CROSS["buy_criteria"], {"ema_20": 101, "sma_50": 100}) is True
    assert evaluate_criteria(CROSS["buy_criteria"], {"ema_20": 99, "sma_50": 100}) is False


def test_buy_only_on_change():
    assert check_signal(RSI, {"rsi": 40}, {"rsi": 28}) == "BUY"
    assert check_signal(RSI, {"rsi": 25}, {"rsi": 28}) is None


def test_sell_on_change():
    assert check_signal(RSI, {"rsi": 60}, {"rsi": 72}) == "SELL"
    assert check_signal(RSI, {"rsi": 75}, {"rsi": 72}) is None


def test_crossover_buy_and_sell():
    below = {"ema_20": 99, "sma_50": 100}
    above = {"ema_20": 101, "sma_50": 100}
    assert check_signal(CROSS, below, above) == "BUY"
    assert check_signal(CROSS, above, below) == "SELL"
    assert check_signal(CROSS, above, above) is None


def test_nan_is_false():
    assert evaluate_criteria(RSI["buy_criteria"], {"rsi": float("nan")}) is False


def test_ml_signal_has_no_rule():
    assert check_signal(ML, {}, {}) is None


def test_unknown_operator_raises():
    with pytest.raises(ValueError):
        evaluate_criteria({"indicator": "rsi", "operator": "==", "value": 30}, {"rsi": 30})