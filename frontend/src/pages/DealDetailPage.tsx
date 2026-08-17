import { useParams } from "react-router-dom";

import { useDeal } from "../features/deals/useDeals";

export function DealDetailPage() {
  const { dealId } = useParams();
  const { data: deal, isLoading, error } = useDeal(dealId);

  if (isLoading) return <div className="panel">Loading deal...</div>;
  if (error || !deal) return <div className="panel error">Deal not found.</div>;

  return (
    <section>
      <div className="page-header">
        <h1>{deal.title}</h1>
        <p>
          {deal.phase} · {deal.type}
        </p>
      </div>
      <div className="detail-grid">
        <div className="panel">
          <h2>Property</h2>
          <dl>
            <dt>Street</dt>
            <dd>{deal.property.street ?? "-"}</dd>
            <dt>City</dt>
            <dd>{deal.property.city ?? "-"}</dd>
            <dt>Land area</dt>
            <dd>{deal.property.land_area_m2 ?? "-"} m2</dd>
          </dl>
        </div>
        <div className="panel">
          <h2>Next Modules</h2>
          <p className="muted">Calculation panel, tasks, documents, and parcel map will be migrated here.</p>
        </div>
      </div>
    </section>
  );
}

