
import { apiRequest } from "./apiClient";
import type { Signal } from "../types/api";

export async function getBtcSignal(): Promise<Signal> {
  return apiRequest<Signal>("/api/signals/btc", {
    requiresAuth: false,
  });
}
