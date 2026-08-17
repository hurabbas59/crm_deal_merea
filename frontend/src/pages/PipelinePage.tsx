import { Link } from "react-router-dom";

import { useDeals } from "../features/deals/useDeals";

export function PipelinePage() {
  const { data: deals = [], isLoading, error } = useDeals();

  return (
    <section>
      <div className="page-header">
        <h1>Pipeline</h1>
        <p>First API-connected deal list. Kanban migration comes next.</p>
      </div>
      {isLoading && <div className="panel">Loading deals...</div>}
      {error && <div className="panel error">Could not load deals.</div>}
      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Phase</th>
              <th>Type</th>
              <th>City</th>
            </tr>
          </thead>
          <tbody>
            {deals.map((deal) => (
              <tr key={deal.deal_id}>
                <td>
                  <Link to={`/deals/${deal.deal_id}`}>{deal.title}</Link>
                </td>
                <td>{deal.phase}</td>
                <td>{deal.type}</td>
                <td>{deal.property.city ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

