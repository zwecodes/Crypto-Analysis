import type { MarketStatus } from "../../types/dashboard";
import "./DashboardCard.css";
import "./MarketStatusCard.css";

interface MarketStatusCardProps {
  status: MarketStatus;
}

export function MarketStatusCard({ status }: MarketStatusCardProps) {
  const lastUpdatedLabel = new Date(status.lastUpdated).toLocaleString();

  return (
    <div className="dashboard-card market-status-card">
      <span className="dashboard-card-title">Market Status</span>
      <span className="dashboard-card-value">{status.pair}</span>
      <span
        className={
          status.status === "Active"
            ? "market-status-badge market-status-active"
            : "market-status-badge market-status-inactive"
        }
      >
        {status.status}
      </span>

      <div className="market-status-updated">
        <span className="dashboard-card-label">Last Updated</span>
        <span className="dashboard-card-value">{lastUpdatedLabel}</span>
      </div>
    </div>
  );
}