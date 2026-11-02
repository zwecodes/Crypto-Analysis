
import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../../services/apiClient";
import {
  deselectUserStrategy,
  getStrategies,
  getUserStrategy,
  selectUserStrategy,
} from "../../services/strategyService";
import type { Strategy, UserStrategy } from "../../types/api";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { Spinner } from "../../components/ui/Spinner";
import "./StrategyPickerPage.css";

type LoadState = "loading" | "ready" | "error";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session may have expired. Please log in again.";
    }
    return error.status >= 500
      ? "The server could not complete your request. Please try again."
      : error.message;
  }

  return "Unable to connect to the server. Please check your connection and try again.";
}

export function StrategyPickerPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [userStrategy, setUserStrategy] = useState<UserStrategy | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const [busyStrategyId, setBusyStrategyId] = useState<string | null>(null);
  const [isDeselecting, setIsDeselecting] = useState(false);

  const loadData = useCallback(async () => {
    setLoadState("loading");
    setErrorMessage("");

    try {
      const [strategyList, currentSelection] = await Promise.all([
        getStrategies(),
        getUserStrategy(),
      ]);

      setStrategies(strategyList);
      setUserStrategy(currentSelection);
      setLoadState("ready");
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function handleSelect(strategyId: string) {
    const strategy = strategies.find((item) => item.id === strategyId);
    if (!strategy || busyStrategyId || isDeselecting) return;

    const isSwitching =
      userStrategy?.active && userStrategy.strategy_id !== strategyId;

    const confirmationMessage = isSwitching
      ? `Switch to "${strategy.name}"? Your email alerts will follow the new strategy.`
      : `Select "${strategy.name}"? This also subscribes you to email alerts for this strategy.`;

    if (!window.confirm(confirmationMessage)) return;

    setBusyStrategyId(strategyId);
    setActionError("");

    try {
      const selection = await selectUserStrategy(strategyId);
      setUserStrategy(selection);
    } catch (error) {
      setActionError(getErrorMessage(error));
    } finally {
      setBusyStrategyId(null);
    }
  }

  async function handleDeselect() {
    if (busyStrategyId || isDeselecting || !userStrategy?.active) return;

    if (
      !window.confirm(
        "Turn off your selected strategy and its associated email alerts?"
      )
    ) {
      return;
    }

    setIsDeselecting(true);
    setActionError("");

    try {
      await deselectUserStrategy();
      setUserStrategy({
        strategy_id: null,
        active: false,
        selected_at: null,
      });
    } catch (error) {
      setActionError(getErrorMessage(error));
    } finally {
      setIsDeselecting(false);
    }
  }

  if (loadState === "loading") {
    return <Spinner label="Loading trading strategies..." />;
  }

  if (loadState === "error") {
    return (
      <div className="strategy-picker-page">
        <h1>Strategy Picker</h1>
        <ErrorMessage message={errorMessage} onRetry={() => void loadData()} />
      </div>
    );
  }

  return (
    <div className="strategy-picker-page">
      <header className="strategy-picker-header">
        <div>
          <h1>Strategy Picker</h1>
          <p>
            Compare predefined Bitcoin strategies and choose which one to follow.
          </p>
        </div>
      </header>

      <section className="strategy-alert-notice" aria-label="Email alert information">
        <strong>Important:</strong> Selecting a strategy also enables email
        alerts for it. Switching strategies changes your active selection;
        deselecting turns those alerts off.
      </section>

      {actionError && <ErrorMessage message={actionError} />}

      {userStrategy?.active && (
        <section className="current-strategy-panel" aria-live="polite">
          <div>
            <span className="strategy-status-label">Currently selected</span>
            <h2>
              {strategies.find(
                (strategy) => strategy.id === userStrategy.strategy_id
              )?.name ?? userStrategy.strategy_id}
            </h2>
            <p>
              Email alerts are enabled for your selected strategy.
              {userStrategy.selected_at &&
                ` Selected ${new Date(userStrategy.selected_at).toLocaleString()}.`}
            </p>
          </div>
          <button
            className="strategy-button strategy-button-secondary"
            type="button"
            onClick={() => void handleDeselect()}
            disabled={isDeselecting || busyStrategyId !== null}
          >
            {isDeselecting ? "Turning off..." : "Turn off alerts"}
          </button>
        </section>
      )}

      {strategies.length === 0 ? (
        <p className="strategy-empty-state">
          No strategies are available right now. Please try again later.
        </p>
      ) : (
        <section className="strategy-grid" aria-label="Available strategies">
          {strategies.map((strategy) => {
            const isSelected =
              userStrategy?.active &&
              userStrategy.strategy_id === strategy.id;
            const isBusy = busyStrategyId === strategy.id;

            return (
              <article className="strategy-card" key={strategy.id}>
                <div className="strategy-card-heading">
                  <h2>{strategy.name}</h2>
                  {isSelected && (
                    <span className="strategy-selected-badge">Selected</span>
                  )}
                </div>

                <p className="strategy-description">{strategy.description}</p>

                <div className="strategy-detail-list">
                  <div>
                    <h3>Pros</h3>
                    {strategy.pros.length > 0 ? (
                      <ul>
                        {strategy.pros.map((pro, index) => (
                          <li key={`${strategy.id}-pro-${index}`}>{pro}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="strategy-muted">No pros provided.</p>
                    )}
                  </div>

                  <div>
                    <h3>Cons</h3>
                    {strategy.cons.length > 0 ? (
                      <ul>
                        {strategy.cons.map((con, index) => (
                          <li key={`${strategy.id}-con-${index}`}>{con}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="strategy-muted">No cons provided.</p>
                    )}
                  </div>
                </div>

                <button
                  className={`strategy-button ${
                    isSelected
                      ? "strategy-button-selected"
                      : "strategy-button-primary"
                  }`}
                  type="button"
                  onClick={() => void handleSelect(strategy.id)}
                  disabled={isSelected || busyStrategyId !== null || isDeselecting}
                >
                  {isBusy
                    ? "Saving..."
                    : isSelected
                      ? "Currently selected"
                      : userStrategy?.active
                        ? "Switch to this strategy"
                        : "Select strategy"}
                </button>
              </article>
            );
          })}
        </section>
      )}
    </div>
  );
}
