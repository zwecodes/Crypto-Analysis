
import { useEffect, useState } from "react";
import { ApiError } from "../../services/apiClient";
import { getBacktestResult } from "../../services/backtestService";
import { getStrategies } from "../../services/strategyService";
import type { BacktestResult, Strategy } from "../../types/api";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { Spinner } from "../../components/ui/Spinner";
import "./BacktestResultsPage.css";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session may have expired. Please sign in again.";
    }

    if (error.status === 404) {
      return "This strategy was not found.";
    }

    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Unable to load backtest results. Please try again.";
}

function formatPercent(value: number | null): string {
  return value === null ? "—" : `${value.toFixed(2)}%`;
}

function formatPrice(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

function getSixMonthsAgo(): string {
  const date = new Date();
  date.setUTCMonth(date.getUTCMonth() - 6);
  return date.toISOString().slice(0, 10);
}

export function BacktestResultsPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState("");
  const [startDate, setStartDate] = useState(getSixMonthsAgo);
  const [endDate, setEndDate] = useState(getToday);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loadingStrategies, setLoadingStrategies] = useState(true);
  const [loadingResult, setLoadingResult] = useState(false);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadStrategies() {
      setLoadingStrategies(true);
      setError("");

      try {
        const data = await getStrategies();

        if (cancelled) return;

        setStrategies(data);

        if (data.length > 0) {
          setStrategyId((current) => current || data[0].id);
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoadingStrategies(false);
        }
      }
    }

    void loadStrategies();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!strategyId || !startDate || !endDate) {
      setResult(null);
      return;
    }

    if (startDate > endDate) {
      setResult(null);
      setError("Start date must be on or before end date.");
      return;
    }

    let cancelled = false;

    async function loadBacktest() {
      setLoadingResult(true);
      setError("");
      setResult(null);

      try {
        const data = await getBacktestResult(strategyId, {
          start_date: startDate,
          end_date: endDate,
        });

        if (!cancelled) {
          setResult(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoadingResult(false);
        }
      }
    }

    void loadBacktest();

    return () => {
      cancelled = true;
    };
  }, [strategyId, startDate, endDate, requestVersion]);

  if (loadingStrategies) {
    return (
      <section className="backtest-page">
        <Spinner />
        <p className="backtest-muted">Loading strategies...</p>
      </section>
    );
  }

  return (
    <section className="backtest-page">
      <header className="backtest-header">
        <div>
          <h1>Backtest Results</h1>
          <p className="backtest-muted">
            Review historical performance for a trading strategy.
          </p>
        </div>

        <button
          type="button"
          className="backtest-refresh"
          onClick={() => setRequestVersion((version) => version + 1)}
          disabled={loadingResult || !strategyId}
        >
          Refresh results
        </button>
      </header>

      <div className="backtest-filters">
        <label>
          Strategy
          <select
            value={strategyId}
            onChange={(event) => setStrategyId(event.target.value)}
            disabled={strategies.length === 0}
          >
            {strategies.map((strategy) => (
              <option key={strategy.id} value={strategy.id}>
                {strategy.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Start date
          <input
            type="date"
            value={startDate}
            max={endDate}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </label>

        <label>
          End date
          <input
            type="date"
            value={endDate}
            min={startDate}
            max={getToday()}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>
      </div>

      {error && <ErrorMessage message={error} />}

      {strategies.length === 0 && !error && (
        <div className="backtest-empty">
          No strategies are available to backtest.
        </div>
      )}

      {loadingResult && (
        <div className="backtest-loading">
          <Spinner />
          <p className="backtest-muted">Loading backtest results...</p>
        </div>
      )}

      {result && !loadingResult && !error && (
        <>
          <div className="backtest-result-meta">
            <span>
              Strategy:{" "}
              <strong>
                {strategies.find((item) => item.id === result.strategy_id)
                  ?.name ?? result.strategy_id}
              </strong>
            </span>
            <span>
              Data range: {result.start_date} to {result.end_date}
            </span>
          </div>

          <div className="backtest-metrics">
            <article className="backtest-metric">
              <span>Total return</span>
              <strong
                className={
                  result.total_return_pct === null
                    ? ""
                    : result.total_return_pct >= 0
                      ? "backtest-positive"
                      : "backtest-negative"
                }
              >
                {formatPercent(result.total_return_pct)}
              </strong>
            </article>

            <article className="backtest-metric">
              <span>Win rate</span>
              <strong>{formatPercent(result.win_rate_pct)}</strong>
            </article>

            <article className="backtest-metric">
              <span>Total trades</span>
              <strong>{result.num_trades}</strong>
            </article>
          </div>

          <section className="backtest-trades-section">
            <h2>Trade history</h2>

            {result.trades.length === 0 ? (
              <p className="backtest-empty">
                No trades are available for this result. This may mean that no
                cached backtest data exists for the selected strategy and date
                range.
              </p>
            ) : (
              <div className="backtest-table-wrapper">
                <table className="backtest-table">
                  <thead>
                    <tr>
                      <th>Entry date</th>
                      <th>Exit date</th>
                      <th>Entry price</th>
                      <th>Exit price</th>
                      <th>Return</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.trades.map((trade, index) => (
                      <tr
                        key={`${trade.entry_date}-${trade.exit_date}-${index}`}
                      >
                        <td>{trade.entry_date}</td>
                        <td>{trade.exit_date}</td>
                        <td>{formatPrice(trade.entry_price)}</td>
                        <td>{formatPrice(trade.exit_price)}</td>
                        <td
                          className={
                            trade.return_pct >= 0
                              ? "backtest-positive"
                              : "backtest-negative"
                          }
                        >
                          {formatPercent(trade.return_pct)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}
