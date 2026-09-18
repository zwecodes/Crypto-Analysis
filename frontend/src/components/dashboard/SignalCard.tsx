import type { Signal } from "../../types/api";
import "./DashboardCard.css";
import "./SignalCard.css";

interface SignalCardProps {
  signal: Signal;
}

const SIGNAL_BADGE_CLASS: Record<Signal["signal"], string> = {
  BUY: "signal-badge signal-buy",
  HOLD: "signal-badge signal-hold",
  SELL: "signal-badge signal-sell",
};

export function SignalCard({ signal }: SignalCardProps) {
  const confidencePercent = Math.round(signal.confidence * 100);
  const timestampLabel = new Date(signal.timestamp * 1000).toLocaleString();

  return (
    <div className="dashboard-card signal-card">
      <span className="dashboard-card-title">Current Signal</span>
      <span className={SIGNAL_BADGE_CLASS[signal.signal]}>{signal.signal}</span>

      <div className="signal-detail">
        <span className="dashboard-card-label">Confidence</span>
        <span className="dashboard-card-value">{confidencePercent}%</span>
      </div>

      <div className="signal-detail">
        <span className="dashboard-card-label">Timestamp</span>
        <span className="dashboard-card-value signal-timestamp">
          {timestampLabel}
        </span>
      </div>
    </div>
  );
}