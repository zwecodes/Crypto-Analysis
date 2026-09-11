import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { ChartPoint } from "../../types/dashboard";
import "./BtcPriceChart.css";

interface BtcPriceChartProps {
  data: ChartPoint[];
}

interface ChartRow {
  time: string;
  price: number;
}

function formatHour(timestampSeconds: number): string {
  return new Date(timestampSeconds * 1000).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatPrice(value: number): string {
  return `$${Math.round(value).toLocaleString()}`;
}

/**
 * Renders mock BTC price data only (Task 2 scope). Takes a plain
 * ChartPoint[] (timestamp + close price) — the same minimal shape a real
 * Candle[] from GET /api/prices/btc would provide, so swapping in real data
 * later means changing only the caller, not this component.
 */
export function BtcPriceChart({ data }: BtcPriceChartProps) {
  const chartRows: ChartRow[] = data.map((point) => ({
    time: formatHour(point.timestamp),
    price: point.close,
  }));

  return (
    <div className="btc-price-chart">
      <span className="dashboard-card-title">BTC / USD — Last 24 Hours</span>
      <div className="btc-price-chart-canvas">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={chartRows}
            margin={{ top: 10, right: 16, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e5e9" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={24} />
            <YAxis
              domain={["auto", "auto"]}
              tickFormatter={formatPrice}
              tick={{ fontSize: 12 }}
              width={70}
            />
                        <Tooltip
              formatter={(value) =>
                formatPrice(typeof value === "number" ? value : Number(value))
              }
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
