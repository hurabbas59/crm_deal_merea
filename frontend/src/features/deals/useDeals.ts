import { useQuery } from "@tanstack/react-query";

import { getDeal, listDeals } from "../../api/deals";

export function useDeals() {
  return useQuery({
    queryKey: ["deals"],
    queryFn: listDeals
  });
}

export function useDeal(dealId: string | undefined) {
  return useQuery({
    queryKey: ["deals", dealId],
    queryFn: () => getDeal(dealId!),
    enabled: Boolean(dealId)
  });
}

