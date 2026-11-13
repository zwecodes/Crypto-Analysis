import type { IndicatorSummaryItem } from "../../types/dashboard";
import "./DashboardCard.css";
import "./IndicatorCard.css";

interface IndicatorCardProps {
  item: IndicatorSummaryItem;
}

/**
 * Displays the latest technical indicator value and its description.
 * Indicator values are calculated by the backend and passed through
 * DashboardPage.
 */
export function IndicatorCard({ item }: IndicatorCardProps) {
  return (
    <div className="dashboard-card indicator-card">
      <span className="dashboard-card-title">{item.label}</span>
      <span className="dashboard-card-value indicator-value">{item.value}</span>
      <span className="indicator-description">{item.description}</span>
    </div>
  );
}