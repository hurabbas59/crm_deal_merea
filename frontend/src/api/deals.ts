import { apiRequest } from "./client";
import type { Deal } from "../types/deal";

export function listDeals() {
  return apiRequest<Deal[]>("/deals");
}

export function getDeal(dealId: string) {
  return apiRequest<Deal>(`/deals/${dealId}`);
}

