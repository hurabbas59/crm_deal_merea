import { useDeals } from "../features/deals/useDeals";

export function DashboardPage() {
  const { data: deals = [], isLoading } = useDeals();
  const activeDeals = deals.filter((deal) => deal.phase !== "cancelled");

  return (
    <section>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Pipeline overview from the FastAPI backend.</p>
      </div>
      <div className="kpi-grid">
        <div className="panel">
          <span className="muted">Active deals</span>
          <strong className="kpi">{isLoading ? "..." : activeDeals.length}</strong>
        </div>
        <div className="panel">
          <span className="muted">Total deals</span>
          <strong className="kpi">{isLoading ? "..." : deals.length}</strong>
        </div>
      </div>
    </section>
  );
}

