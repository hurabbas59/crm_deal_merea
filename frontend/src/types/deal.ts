export type DealPhase =
  | "new"
  | "review"
  | "calculation"
  | "loi"
  | "due_diligence"
  | "notary"
  | "cancelled";

export type DealType = "project_development" | "multi_family";

export type DealProperty = {
  street?: string | null;
  postal_code?: string | null;
  city?: string | null;
  state?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  land_area_m2?: number | null;
  living_area_m2?: number | null;
  units?: number | null;
};

export type Deal = {
  deal_id: string;
  title: string;
  type: DealType;
  phase: DealPhase;
  source?: string | null;
  source_reference?: string | null;
  cancellation_reason?: string | null;
  notes?: string | null;
  property: DealProperty;
  created_at: string;
  updated_at: string;
};

