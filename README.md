# MEREA CRM

Internal CRM for property deal intake, pipeline review, project-development calculations, map/parcel display, and n8n automation ingestion.

## Recommended Architecture

This project uses a modular FastAPI backend and a React frontend. The backend is organized by feature areas such as deals, calculations, n8n imports, Excel import/export, and map/parcel lookup.
```text
frontend/  React + Vite + TypeScript
backend/   FastAPI API + services + data adapters
infra/     Docker/Nginx/deployment files
data/      local Excel import/export/backups during development
docs/      architecture and implementation notes
```

Backend layers:

```text
API routers -> services -> repositories/adapters -> Postgres or Excel
```

Frontend layers:

```text
pages -> feature modules -> shared components -> API client
```

The old prototype files are intentionally kept for reference:

- `Pipeline-CRM.html`
- `serve.js`
- `grundstueck_service.py`
- `Kalkulation.xlsx`
- `Projektkalkulation.xlsx`

## First Target

1. Build FastAPI backend skeleton.
2. Define database models and schemas from the Excel files.
3. Add `GET /api/v1/deals` and `GET /api/v1/deals/{deal_id}`.
4. Build React/Vite UI shell.
5. Replace prototype `localStorage` with API calls.
6. Add n8n endpoint for deal creation.
7. Add calculation and map parcel services.

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Infrastructure:

```bash
docker compose -f infra/docker-compose.yml up -d db
```

