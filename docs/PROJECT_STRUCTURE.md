# Project Structure

```text
CRM/
  backend/
    app/
      api/
        v1/
          endpoints/
            health.py
            deals.py
            calculations.py
            parcels.py
            n8n.py
            integrations.py
          router.py
      core/
        config.py
      db/
        session.py
      models/
        deal.py
      repositories/
        deal_repository.py
      schemas/
        deal.py
        calculation.py
        n8n.py
        parcel.py
      services/
        deal_service.py
        calculation_service.py
        excel_service.py
        n8n_service.py
        parcel_service.py
      main.py
    tests/
    pyproject.toml
    Dockerfile

  frontend/
    src/
      api/
      app/
      components/
      features/
        calculations/
        contacts/
        deals/
        maps/
        tasks/
      pages/
      types/
      main.tsx
      styles.css
    package.json
    vite.config.ts
    Dockerfile

  infra/
    docker-compose.yml
    nginx/
      default.conf

  data/
    backups/
    imports/
    exports/

  docs/
    ARCHITECTURE.md
    N8N_PARZELLIERUNG_INTEGRATION.md
    PROJECT_STRUCTURE.md

  legacy prototype/reference files:
    Pipeline-CRM.html
    serve.js
    grundstueck_service.py
    Kalkulation.xlsx
    Projektkalkulation.xlsx
```

## Backend Pattern

Use this flow for every feature:

```text
endpoint -> service -> repository -> database/excel adapter
```

Example:

```text
POST /api/v1/n8n/deals
  -> N8NService.ingest_deal()
  -> DealRepository.create/update()
  -> Postgres or Excel storage
```

## Frontend Pattern

Use feature folders. Each feature owns its hooks/components for that domain.

Example:

```text
features/deals/
  useDeals.ts
  DealCard.tsx
  DealForm.tsx
```

Shared route-level screens live in `pages/`.

## Migration From Prototype

Recommended order:

1. Deals list and detail data model.
2. Project calculation module.
3. Map marker and parcel polygon module.
4. n8n ingestion.
5. Excel import/export.
6. Contacts, tasks, documents.
