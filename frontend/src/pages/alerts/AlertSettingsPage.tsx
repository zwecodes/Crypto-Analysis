
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../../services/apiClient";
import {
  deselectUserStrategy,
  getStrategies,
  getUserStrategy,
} from "../../services/strategyService";
import type { Strategy, UserStrategy } from "../../types/api";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { Spinner } from "../../components/ui/Spinner";
import "./AlertSettingsPage.css";

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

export function AlertSettingsPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [userStrategy, setUserStrategy] = useState<UserStrategy | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isDisabling, setIsDisabling] = useState(false);

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

  async function handleDisableAlerts() {
    if (isDisabling || !userStrategy?.active) return;

    if (
      !window.confirm(
        "Are you sure you want to turn off your email alerts?"
      )
    ) {
      return;
    }

    setIsDisabling(true);
    setActionError("");
    setSuccessMessage("");

    try {
      await deselectUserStrategy();

      setUserStrategy({
        strategy_id: null,
        active: false,
        selected_at: null,
      });

      setSuccessMessage("Your email alerts have been turned off.");
    } catch (error) {
      setActionError(getErrorMessage(error));
    } finally {
      setIsDisabling(false);
    }
  }

  if (loadState === "loading") {
    return <Spinner label="Loading alert settings..." />;
  }

  if (loadState === "error") {
    return (
      <div className="alerts-page">
        <h1>Alert Settings</h1>
        <ErrorMessage
          message={errorMessage}
          onRetry={() => void loadData()}
        />
      </div>
    );
  }

  const selectedStrategy = strategies.find(
    (strategy) => strategy.id === userStrategy?.strategy_id
  );

  return (
    <div className="alerts-page">
      <header className="alerts-header">
        <h1>Alert Settings</h1>
        <p>
          Manage your Bitcoin trading strategy email alert subscription.
        </p>
      </header>

      <section className="alerts-info">
        <strong>How it works</strong>
        <p>
          Your email alerts are linked to your selected trading strategy.
          Selecting a strategy enables alerts, while turning them off
          disables your active subscription.
        </p>
      </section>

      {actionError && <ErrorMessage message={actionError} />}

      {successMessage && (
        <div className="alerts-success" role="status">
          {successMessage}
        </div>
      )}

      <section className="alerts-status-card">
        <div className="alerts-status-heading">
          <h2>Email Alert Subscription</h2>

          <span
            className={`alerts-status-badge ${
              userStrategy?.active ? "alerts-status-active" : "alerts-status-inactive"
            }`}
          >
            {userStrategy?.active ? "Active" : "Inactive"}
          </span>
        </div>

        {userStrategy?.active ? (
          <>
            <div className="alerts-detail">
              <span>Selected strategy</span>
              <strong>
                {selectedStrategy?.name ?? userStrategy.strategy_id}
              </strong>
            </div>

            <div className="alerts-detail">
              <span>Subscription started</span>
              <strong>
                {userStrategy.selected_at
                  ? new Date(userStrategy.selected_at).toLocaleString()
                  : "Unavailable"}
              </strong>
            </div>

            <p className="alerts-description">
              Your email alert subscription is currently enabled for this
              strategy.
            </p>

            <button
              className="alerts-disable-button"
              type="button"
              onClick={() => void handleDisableAlerts()}
              disabled={isDisabling}
            >
              {isDisabling ? "Turning off..." : "Turn off email alerts"}
            </button>
          </>
        ) : (
          <>
            <p className="alerts-description">
              You don't currently have an active strategy subscription.
              Select a strategy to enable email alerts.
            </p>

            <Link className="alerts-link-button" to="/strategies">
              Choose a strategy
            </Link>
          </>
        )}
      </section>
    </div>
  );
}
