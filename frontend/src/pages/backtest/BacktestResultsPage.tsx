
import { useEffect, useState } from "react";
import { ApiError } from "../../services/apiClient";
import {
  getBacktestRanges,
  getBacktestResult,
} from "../../services/backtestService";
import type { BacktestRanges } from "../../services/backtestService";
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

    if (error.code === "NOT_FOUND") {
      return "This strategy was not found.";
    }

    if (error.code === "NO_MATCHING_BACKTEST") {
      return "No backtest results are available for this strategy and date range.";
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

export function BacktestResultsPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState("");

  const [ranges, setRanges] = useState<BacktestRanges | null>(null);
  const [endDate, setEndDate] = useState("");
  const [result, setResult] = useState<BacktestResult | null>(null);

  const [loadingStrategies, setLoadingStrategies] = useState(true);
  const [loadingRanges, setLoadingRanges] = useState(false);
  const [loadingResult, setLoadingResult] = useState(false);

  const [error, setError] = useState("");
  const [rangeMessage, setRangeMessage] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);

  // Load available strategies.
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

  // Load date ranges for the selected strategy.
  useEffect(() => {
    if (!strategyId) {
      setRanges(null);
      setEndDate("");
      setResult(null);
      return;
    }

    let cancelled = false;

    async function loadRanges() {
      setLoadingRanges(true);
      setRanges(null);
      setEndDate("");
      setResult(null);
      setError("");
      setRangeMessage("");

      try {
        const data = await getBacktestRanges(strategyId);

        if (cancelled) return;

        setRanges(data);
        setEndDate(data.max_end_date);
      } catch (err) {
        if (cancelled) return;

        setRanges(null);
        setEndDate("");

        if (
          err instanceof ApiError &&
          err.code === "NO_MATCHING_BACKTEST"
        ) {
          setRangeMessage(
            "No backtest results have been computed for this strategy yet."
          );
        } else {
          setError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoadingRanges(false);
        }
      }
    }

    void loadRanges();

    return () => {
      cancelled = true;
    };
  }, [strategyId]);

  // Load results for the selected strategy and date range.
  useEffect(() => {
    if (!strategyId || !ranges || !endDate) {
      setResult(null);
      return;
    }

    if (
      endDate < ranges.min_end_date ||
      endDate > ranges.max_end_date
    ) {
      setResult(null);
      setError("Please select an end date within the available date range.");
      return;
    }

       const selectedRanges = ranges;
    const selectedEndDate = endDate;

    let cancelled = false;

    async function loadBacktest() {
      setLoadingResult(true);
      setError("");
      setRangeMessage("");
      setResult(null);

      try {
                const data = await getBacktestResult(strategyId, {
          start_date: selectedRanges.start_date,
          end_date: selectedEndDate,
        });

        if (!cancelled) {
          setResult(data);
        }
      } catch (err) {
        if (cancelled) return;

        if (
          err instanceof ApiError &&
          err.code === "NO_MATCHING_BACKTEST"
        ) {
          setRangeMessage(
            "No backtest results are available for this selected date range."
          );
        } else {
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
  }, [strategyId, ranges, endDate, requestVersion]);

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
          disabled={
            loadingRanges ||
            loadingResult ||
            !strategyId ||
            !ranges ||
            !endDate
          }
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
            value={ranges?.start_date ?? ""}
            disabled
          />
        </label>

        <label>
          End date
          <input
            type="date"
            value={endDate}
            min={ranges?.min_end_date}
            max={ranges?.max_end_date}
            disabled={loadingRanges || !ranges}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>
      </div>

      {loadingRanges && (
        <div className="backtest-loading">
          <Spinner />
          <p className="backtest-muted">
            Loading available dates for this strategy...
          </p>
        </div>
      )}

      {error && <ErrorMessage message={error} />}

      {rangeMessage && (
        <div className="backtest-empty">{rangeMessage}</div>
      )}

      {strategies.length === 0 && !error && (
        <div className="backtest-empty">
          No strategies are available to backtest.
        </div>
      )}

      {loadingResult && (
        <div className="backtest-loading">
          <Spinner />
          <p className="backtest-muted">
            Loading backtest results...
          </p>
        </div>
      )}

      {result && !loadingResult && !error && !rangeMessage && (
        <>
          <div className="backtest-result-meta">
            <span>
              Strategy:{" "}
              <strong>
                {strategies.find(
                  (item) => item.id === result.strategy_id
                )?.name ?? result.strategy_id}
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
                No trades are available for this result.
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
