# Architecture

## Decision

Use:

- **Backend:** Python FastAPI.
- **Frontend:** React + Vite + TypeScript.
- **Primary data store:** Postgres on the Contabo/VPS server, if approved.
- **Excel:** import/export, reporting, and compatibility with current workbook logic.
- **Automation:** n8n sends normalized Parzellierung deal data into the backend API.

If the team still wants Excel as the official source of truth for version 1, the backend can use the Excel adapter first and later swap to Postgres. The API shape should remain the same either way.

## Why This Architecture Fits

The app is an internal CRM with low data volume but multiple operations:

- n8n creates deals from emails.
- Users create and update deals.
- Users review calculations.
- Users inspect map locations and exact parcel polygons.
- Data should be reliable and easy to back up.

FastAPI gives a clean backend for APIs and automation webhooks. React/Vite gives a lightweight internal dashboard frontend without the complexity of SSR.

## Backend Module Boundaries

```text
backend/app/api
```

FastAPI routers only. They validate request/response shape and call services.

```text
backend/app/services
```

Business logic:

- deal orchestration
- calculation logic
- Excel import/export
- n8n ingestion
- parcel lookup

```text
backend/app/repositories
```

Data access abstraction. Repositories hide whether data comes from Postgres or Excel.

```text
backend/app/models
```

Database models.

```text
backend/app/schemas
```

Pydantic request/response DTOs.

```text
backend/app/db
```

Database session, base metadata, migrations later.

## Frontend Module Boundaries

```text
frontend/src/api
```

Backend API client functions.

```text
frontend/src/features
```

Feature-specific UI and logic:

- deals
- calculations
- maps
- contacts
- tasks

```text
frontend/src/pages
```

Route-level screens.

```text
frontend/src/components
```

Shared UI/layout components.

## Data Flow

```text
n8n -> POST /api/v1/integrations/email-offers/parzellierung -> deal service -> repository -> Postgres/Excel
```

```text
React frontend -> GET /api/v1/deals -> FastAPI -> repository -> Postgres/Excel
```

```text
React frontend -> GET /api/v1/parcels/lookup?lat=...&lng=... -> parcel service -> cadastral API -> stored polygon
```

## Deployment Shape

For Contabo:

```text
Nginx
  - serves frontend build
  - proxies /api/v1 to FastAPI

FastAPI
  - runs with uvicorn/gunicorn or Docker

Postgres
  - local service on same VPS

n8n
  - same VPS or separate service
```
