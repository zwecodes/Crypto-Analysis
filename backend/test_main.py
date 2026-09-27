from fastapi.testclient import TestClient

from main import app
from routes.backtest import _iso_date
from routes.strategies import serialize_strategy
from services.cache import TtlCache, market_data_cache
from services.rate_limit import RateLimitMiddleware
from services.seed_strategies import STRATEGIES

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_prices_rejects_invalid_interval():
    response = client.get("/api/prices/btc?interval=2h")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "BAD_REQUEST"


def test_indicators_rejects_limit_too_large():
    response = client.get("/api/indicators/btc?limit=5000")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "BAD_REQUEST"


def test_backtest_rejects_bad_date_order():
    response = client.get(
        "/api/backtest/rsi_oversold?start_date=2026-08-01&end_date=2026-01-01"
    )
    # May be 400 (validation) or 500 if Supabase unreachable for strategy check —
    # bad date order is validated before the DB call.
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_strategy_list_keeps_only_predefined_ids():
    from routes.strategies import visible_strategies

    rows = [
        {"id": "test_strategy", "name": "Test", "description": "x", "pros": [], "cons": []},
        {
            "id": "ml_signal",
            "name": "ML Model Signal",
            "description": "model",
            "pros": [],
            "cons": [],
        },
        {
            "id": "rsi_oversold",
            "name": "RSI Oversold/Overbought",
            "description": "rsi",
            "pros": [],
            "cons": [],
        },
    ]
    kept = visible_strategies(rows)
    assert [row["id"] for row in kept] == ["rsi_oversold", "ml_signal"]


def test_strategy_ids_match_ml_contract():
    assert [item["id"] for item in STRATEGIES] == [
        "rsi_oversold",
        "ma_crossover",
        "macd_momentum",
        "bollinger_bounce",
        "ml_signal",
    ]


def test_serialize_strategy_defaults_empty_pros_cons():
    payload = serialize_strategy(
        {
            "id": "rsi_oversold",
            "name": "RSI Oversold/Overbought",
            "description": "Buys when RSI < 30, sells when RSI > 70",
            "pros": None,
            "cons": ["Can give false signals in strong trends"],
        }
    )
    assert payload["pros"] == []
    assert payload["cons"] == ["Can give false signals in strong trends"]


def test_backtest_trade_dates_are_iso_dates():
    assert _iso_date("2026-03-15 12:00:00") == "2026-03-15"
    assert _iso_date("2026-03-22") == "2026-03-22"


def test_ttl_cache_expires():
    cache = TtlCache(ttl_seconds=0.01)
    cache.set("k", {"ok": True})
    assert cache.get("k") == {"ok": True}
    import time

    time.sleep(0.02)
    assert cache.get("k") is None


def test_rate_limit_middleware_blocks_excess():
    from fastapi import FastAPI

    tiny = FastAPI()
    tiny.add_middleware(RateLimitMiddleware, limit=2, window_seconds=60.0)

    @tiny.get("/ping")
    def ping():
        return {"ok": True}

    c = TestClient(tiny)
    assert c.get("/ping").status_code == 200
    assert c.get("/ping").status_code == 200
    blocked = c.get("/ping")
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def teardown_module(_module):
    market_data_cache.clear()
