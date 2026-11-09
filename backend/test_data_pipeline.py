"""Tests for services/data_pipeline.py that run without network or credentials."""
import pytest

from services import data_pipeline


def test_default_base_url(monkeypatch):
    monkeypatch.delenv("BINANCE_BASE_URL", raising=False)
    assert data_pipeline.get_klines_url() == "https://api.binance.com/api/v3/klines"


def test_base_url_can_be_overridden(monkeypatch):
    monkeypatch.setenv("BINANCE_BASE_URL", "https://data-api.binance.vision/")
    assert data_pipeline.get_klines_url() == "https://data-api.binance.vision/api/v3/klines"


def test_fetch_uses_configured_url(monkeypatch):
    monkeypatch.setenv("BINANCE_BASE_URL", "https://example.test")
    seen = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    def fake_get(url, **kwargs):
        seen["url"] = url
        return FakeResponse()

    monkeypatch.setattr(data_pipeline.httpx, "get", fake_get)

    assert data_pipeline.fetch_binance_klines() == []
    assert seen["url"] == "https://example.test/api/v3/klines"


def test_parse_candles_converts_ms_to_seconds():
    raw = [[1700000000000, "1", "2", "0.5", "1.5", "10", 0]]
    candle = data_pipeline.parse_candles(raw)[0]
    assert candle["timestamp"] == 1700000000
    assert candle["symbol"] == "BTC"
    assert candle["close"] == 1.5


def test_parse_candles_rejects_bad_rows():
    with pytest.raises(RuntimeError):
        data_pipeline.parse_candles([["bad"]])