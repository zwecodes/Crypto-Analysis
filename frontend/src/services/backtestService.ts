
import { apiRequest } from "./apiClient";
import type { BacktestResult } from "../types/api";

export interface BacktestQuery {
  start_date?: string;
  end_date?: string;
}

export async function getBacktestResult(
  strategyId: string,
  query: BacktestQuery = {}
): Promise<BacktestResult> {
  const params = new URLSearchParams();

  if (query.start_date) {
    params.set("start_date", query.start_date);
  }

  if (query.end_date) {
    params.set("end_date", query.end_date);
  }

  const queryString = params.toString();
  const path = `/api/backtest/${encodeURIComponent(strategyId)}${
    queryString ? `?${queryString}` : ""
  }`;

  return apiRequest<BacktestResult>(path);
}
