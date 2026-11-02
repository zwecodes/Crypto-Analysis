
import { apiRequest } from "./apiClient";
import type {
  Strategy,
  StrategiesResponse,
  UserStrategy,
} from "../types/api";

export async function getStrategies(): Promise<Strategy[]> {
  const response = await apiRequest<StrategiesResponse>("/api/strategies", {
    requiresAuth: false,
  });

  return response.strategies;
}

export async function getUserStrategy(): Promise<UserStrategy> {
  return apiRequest<UserStrategy>("/api/user/strategy");
}

export async function selectUserStrategy(
  strategyId: string
): Promise<UserStrategy> {
  return apiRequest<UserStrategy>("/api/user/strategy", {
    method: "POST",
    body: { strategy_id: strategyId },
  });
}

export async function deselectUserStrategy(): Promise<void> {
  return apiRequest<void>("/api/user/strategy", {
    method: "DELETE",
  });
}
