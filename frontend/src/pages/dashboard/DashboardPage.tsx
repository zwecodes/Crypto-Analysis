import { MarketSummaryCard } from "../../components/dashboard/MarketSummaryCard";
import { BtcPriceChart } from "../../components/dashboard/BtcPriceChart";
import { SignalCard } from "../../components/dashboard/SignalCard";
import { IndicatorCard } from "../../components/dashboard/IndicatorCard";
import { MarketStatusCard } from "../../components/dashboard/MarketStatusCard";
import {
  mockMarketSummary,
  mockSignal,
  mockIndicators,
  mockMarketStatus,
  mockChartData,
} from "../../data/dashboardMockData";
import "./DashboardPage.css";

/**
 * Task 2 scope: dashboard UI built entirely on mock data from
 * data/dashboardMockData.ts. No Binance/backend/Supabase/ML calls happen
 * here — replacing the mock imports with real fetched data in a later
 * task should not require changing any component below.
 */
export function DashboardPage() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="dashboard-page-subtitle">Bitcoin market overview</p>
        </div>
        <span className="dashboard-demo-badge">Demo data</span>
      </div>

      <MarketSummaryCard data={mockMarketSummary} />

      <BtcPriceChart data={mockChartData} />

      <div className="dashboard-grid">
        <SignalCard signal={mockSignal} />
        {mockIndicators.map((item) => (
          <IndicatorCard key={item.label} item={item} />
        ))}
        <MarketStatusCard status={mockMarketStatus} />
      </div>
    </div>
  );
}
