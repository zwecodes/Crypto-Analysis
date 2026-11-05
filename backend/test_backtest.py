"""Tests for GET /api/backtest/{strategy_id}: exact date-range matching only.

Supabase is replaced by a tiny in-memory fake, so these run without network
access or credentials (same as GitHub Actions CI).
"""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import routes.backtest as backtest_module
from main import app

client = TestClient(app)

STRATEGY = "rsi_oversold"

CACHED_ROW = {
    "strategy_id": STRATEGY,
    "start_date": "2026-03-31",
    "end_date": "2026-10-23",
    "total_return_pct": 12.4,
    "win_rate_pct": 58.0,
    "num_trades": 1,
    "trades": [
        {
            "entry_date": "2026-04-02",
            "exit_date": "2026-04-09",
            "entry_price": 62000.0,
            "exit_price": 64500.0,
            "return_pct": 4.03,
        }
    ],
    "computed_at": "2026-10-23T10:00:00+00:00",
}


class FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column, value):
        self._rows = [r for r in self._rows if str(r.get(column)) == str(value)]
        return self

    def order(self, column, desc=False):
        self._rows.sort(key=lambda r: str(r.get(column, "")), reverse=desc)
        return self

    def limit(self, count):
        self._rows = self._rows[:count]
        return self

    def execute(self):
        return SimpleNamespace(data=self._rows)


class FakeClient:
    def __init__(self, tables):
        self._tables = tables

    def table(self, name):
        return FakeQuery(self._tables.get(name, []))


def use_tables(monkeypatch, backtest_rows):
    tables = {
        "strategies": [{"id": STRATEGY}],
        "backtest_results": backtest_rows,
    }
    monkeypatch.setattr(backtest_module, "_get_client", lambda: FakeClient(tables))


def url(start, end, strategy=STRATEGY):
    return f"/api/backtest/{strategy}?start_date={start}&end_date={end}"


def test_exact_match_returns_existing_result_format(monkeypatch):
    use_tables(monkeypatch, [CACHED_ROW])

    response = client.get(url("2026-03-31", "2026-10-23"))

    assert response.status_code == 200
    assert response.json() == {
        "strategy_id": STRATEGY,
        "start_date": "2026-03-31",
        "end_date": "2026-10-23",
        "total_return_pct": 12.4,
        "win_rate_pct": 58.0,
        "num_trades": 1,
        "trades": [
            {
                "entry_date": "2026-04-02",
                "exit_date": "2026-04-09",
                "entry_price": 62000.0,
                "exit_price": 64500.0,
                "return_pct": 4.03,
            }
        ],
    }


def test_different_range_is_not_returned_silently(monkeypatch):
    use_tables(monkeypatch, [CACHED_ROW])

    # The exact case reported by the frontend: a cached result exists, but for
    # a different window than the one selected.
    response = client.get(url("2026-06-25", "2026-09-25"))

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NO_MATCHING_BACKTEST"
    assert "2026-06-25 to 2026-09-25" in error["message"]
    assert "Available ranges: 2026-03-31 to 2026-10-23" in error["message"]
    assert "total_return_pct" not in response.json()


def test_partial_overlap_is_not_a_match(monkeypatch):
    use_tables(monkeypatch, [CACHED_ROW])

    # Same start date, different end date: still not an exact match.
    response = client.get(url("2026-03-31", "2026-10-22"))

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NO_MATCHING_BACKTEST"


def test_no_results_for_strategy_returns_clear_404(monkeypatch):
    use_tables(monkeypatch, [])

    response = client.get(url("2026-03-31", "2026-10-23"))

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NO_MATCHING_BACKTEST"
    assert "No backtest results have been computed" in error["message"]


def test_available_ranges_are_listed_once_newest_first(monkeypatch):
    older = dict(CACHED_ROW, start_date="2026-01-01", end_date="2026-06-30",
                 computed_at="2026-07-01T00:00:00+00:00")
    duplicate = dict(CACHED_ROW)
    use_tables(monkeypatch, [older, CACHED_ROW, duplicate])

    response = client.get(url("2026-08-01", "2026-08-31"))

    message = response.json()["error"]["message"]
    assert response.status_code == 404
    assert message.count("2026-03-31 to 2026-10-23") == 1
    assert message.index("2026-03-31 to 2026-10-23") < message.index("2026-01-01 to 2026-06-30")


def test_unknown_strategy_is_still_not_found(monkeypatch):
    use_tables(monkeypatch, [CACHED_ROW])

    response = client.get(url("2026-03-31", "2026-10-23", strategy="not_a_strategy"))

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def _fail_if_database_is_used():
    raise AssertionError("validation must run before any database call")


@pytest.mark.parametrize(
    "query, message_part",
    [
        ("start_date=2026-08-01&end_date=2026-01-01", "on or before"),
        ("start_date=2026-13-45&end_date=2026-10-23", "start_date must be an ISO date"),
        ("start_date=2026-03-31&end_date=not-a-date", "end_date must be an ISO date"),
    ],
)
def test_invalid_dates_are_rejected_before_the_database(monkeypatch, query, message_part):
    monkeypatch.setattr(backtest_module, "_get_client", _fail_if_database_is_used)

    response = client.get(f"/api/backtest/{STRATEGY}?{query}")

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "BAD_REQUEST"
    assert message_part in error["message"]