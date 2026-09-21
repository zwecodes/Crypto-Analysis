from fastapi.testclient import TestClient

from main import app
from services.cache import TtlCache, market_data_cache
from services.rate_limit import RateLimitMiddleware

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
