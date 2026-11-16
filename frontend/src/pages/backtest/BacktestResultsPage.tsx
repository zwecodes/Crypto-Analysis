
import { useEffect, useState } from "react";
import { ApiError } from "../../services/apiClient";
import { getBacktestResult } from "../../services/backtestService";
import { getBtcPrices } from "../../services/priceService";
import { getStrategies } from "../../services/strategyService";
import type { BacktestResult, Strategy } from "../../types/api";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { Spinner } from "../../components/ui/Spinner";
import "./BacktestResultsPage.css";

const FIXED_START_DATE = "2026-03-31";
const MIN_END_DATE = "2026-04-30";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session may have expired. Please sign in again.";
    }

    if (error.code === "NOT_FOUND") {
      return "This strategy was not found.";
    }

    if (error.code === "NO_MATCHING_BACKTEST") {
      return error.message;
    }

    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Unable to load backtest results. Please try again.";
}

function formatCandleDate(timestamp: number): string {
  return new Date(timestamp * 1000).toISOString().slice(0, 10);
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
  const [endDate, setEndDate] = useState("");
  const [latestDate, setLatestDate] = useState("");
  const [result, setResult] = useState<BacktestResult | null>(null);

  const [loadingStrategies, setLoadingStrategies] = useState(true);
  const [loadingLatestDate, setLoadingLatestDate] = useState(true);
  const [loadingResult, setLoadingResult] = useState(false);

  const [error, setError] = useState("");
  const [dateError, setDateError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);

  const startDate = FIXED_START_DATE;

  // Load the newest available BTC candle date.
  useEffect(() => {
    let cancelled = false;

    async function loadLatestDate() {
      setLoadingLatestDate(true);
      setDateError("");

      try {
        const candles = await getBtcPrices({ limit: 1 });

        if (cancelled) return;

        if (candles.length === 0) {
          throw new Error("No BTC price data is available.");
        }

        const newestDate = formatCandleDate(
          candles[candles.length - 1].timestamp
        );

        if (newestDate < MIN_END_DATE) {
          throw new Error("No backtest end dates are currently available.");
        }

        setLatestDate(newestDate);
        setEndDate(newestDate);
      } catch (err) {
        if (!cancelled) {
          setDateError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoadingLatestDate(false);
        }
      }
    }

    void loadLatestDate();

    return () => {
      cancelled = true;
    };
  }, []);

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

  // Load backtest results whenever the strategy or end date changes.
  useEffect(() => {
    if (!strategyId || !endDate || !latestDate) {
      setResult(null);
      return;
    }

    if (endDate < MIN_END_DATE || endDate > latestDate) {
      setResult(null);
      setError("Please select a valid backtest end date.");
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
  }, [strategyId, startDate, endDate, latestDate, requestVersion]);

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
          disabled={loadingResult || !strategyId || !endDate}
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
          <input type="date" value={startDate} disabled />
        </label>

        <label>
          End date
          <input
            type="date"
            value={endDate}
            min={MIN_END_DATE}
            max={latestDate}
            disabled={loadingLatestDate || !latestDate}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>
      </div>

      {loadingLatestDate && (
        <p className="backtest-muted">
          Finding the newest available BTC data...
        </p>
      )}

      {dateError && <ErrorMessage message={dateError} />}

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
