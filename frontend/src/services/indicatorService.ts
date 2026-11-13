
import { apiRequest } from "./apiClient";
import type { IndicatorsResponse } from "../types/api";

interface GetBtcIndicatorsOptions {
  interval?: string;
  limit?: number;
  offset?: number;
}

export async function getBtcIndicators(
  options: GetBtcIndicatorsOptions = {}
): Promise<IndicatorsResponse> {
  const {
    interval = "1h",
    limit = 200,
    offset = 0,
  } = options;

  const params = new URLSearchParams({
    interval,
    limit: String(limit),
    offset: String(offset),
  });

  return apiRequest<IndicatorsResponse>(
    `/api/indicators/btc?${params.toString()}`,
    { requiresAuth: false }
  );
}
