# CRM Architecture Plan

## Purpose

This document explains the planned architecture for the internal property deal CRM. The current project is a working frontend prototype with local browser storage, Excel import/export, calculations, and map display. The goal is to turn it into a complete internal system where n8n automations create ready-to-use deal data and users can view, create, update, calculate, and inspect property deals on the website.

The system is intended for internal use, with low data volume and mostly text/numeric property data. Login/authentication is not required for the first version.

## Current Codebase Summary

The current folder contains these main files:

- `Pipeline-CRM.html`
  - Main frontend application.
  - Contains all HTML, CSS, and JavaScript in one file.
  - Shows dashboard, pipeline, contacts, map, tasks, documents, deal details, and project calculations.
  - Currently stores data in browser `localStorage`.
  - Already includes Excel import/export/sync logic using SheetJS.

- `serve.js`
  - Small local Node.js static file server.
  - Serves `Pipeline-CRM.html` at `http://localhost:8080/`.

- `grundstueck_service.py`
  - Local Python service.
  - Fetches Hessen cadastral parcel data from public WFS endpoints.
  - Returns parcel polygon, area, length, width, and Bodenrichtwert for a given latitude/longitude.

- `Kalkulation.xlsx`
  - Current multi-deal workbook.
  - Already has CRM-style data sheets: `Pipeline`, `Parzellen`, and `Baunebenkosten`.

- `Projektkalkulation.xlsx`
  - Single-project calculation template.
  - Contains the business logic/formulas for project development calculations.

## High-Level Target Architecture

Recommended production-style internal architecture:

```text
Email / source systems
        |
        v
n8n automation
        |
        v
Backend API
        |
        v
Data source
Excel files or lightweight database
        |
        v
Frontend website
```

The frontend should not write directly to Excel from the browser in the final version. A backend should sit between the website, n8n, Excel/database, and external APIs. This keeps writes controlled and avoids corrupted files.

## Frontend

### Role

The frontend is the user interface. It should be responsible for displaying data, collecting user input, showing calculations, and rendering maps. It should not contain secret API keys or directly edit shared Excel files.

### Main Views

The current frontend already supports these screens:

- Dashboard
  - Pipeline volume.
  - Number of active deals.
  - Average margin.
  - Overdue tasks.
  - Funnel/conversion chart.
  - New deals over time.
  - Cancelled deals grouped by reason.

- Pipeline
  - Kanban view.
  - List view.
  - Search and filters.
  - Deal phases such as `Neues Angebot`, `Prüfung`, `Kalkulation`, `LOI`, `Due Diligence`, `Notar`, and `Absagen`.

- Deal detail page
  - Address.
  - Deal status.
  - Property type.
  - Grundstück data.
  - Calculation section.
  - Summary/result section.
  - Tasks.
  - Document links.

- Contacts
  - Contact list.
  - Roles such as owner, broker, notary, and other.
  - Deal-to-contact linking.

- Map
  - Shows all deals with coordinates.
  - Shows a marker for each deal.
  - Can show parcel boundaries/polygons for exact property display.

### Frontend Data Flow

Current flow:

```text
Browser localStorage
        |
        v
Pipeline-CRM.html state
        |
        v
UI rendering
```

Target flow:

```text
Backend API
        |
        v
Frontend state
        |
        v
UI rendering
```

Example frontend API calls:

```text
GET    /api/deals
GET    /api/deals/:dealId
POST   /api/deals
PATCH  /api/deals/:dealId
DELETE /api/deals/:dealId

GET    /api/contacts
POST   /api/contacts
PATCH  /api/contacts/:contactId

GET    /api/tasks
POST   /api/deals/:dealId/tasks
PATCH  /api/deals/:dealId/tasks/:taskId

GET    /api/deals/:dealId/calculation
PATCH  /api/deals/:dealId/calculation
POST   /api/deals/:dealId/recalculate
```

### Frontend Responsibilities

The frontend should:

- Render dashboards and pipeline views.
- Show deal details.
- Let users create and edit deals.
- Let users edit calculation inputs.
- Display calculation results returned by backend or calculated locally from backend-provided data.
- Display map markers and property polygons.
- Show validation errors from the backend.
- Provide refresh/reload controls when data is updated by n8n.

The frontend should not:

- Store the main shared data in browser `localStorage`.
- Keep secret API keys.
- Write shared Excel files directly.
- Call Propstack or other protected external APIs directly.

## Backend

### Role

The backend is the control layer. It should handle data access, n8n webhooks, Excel/database writes, calculations, map parcel lookup, validation, and backups.

The backend can be built using:

- Node.js with Express/Fastify, or
- Python with FastAPI.

For this project, Node.js may be convenient because the current frontend is JavaScript-heavy and SheetJS can also be used server-side for Excel operations.

### Backend Responsibilities

The backend should:

- Serve API endpoints for the frontend.
- Receive prepared deal data from n8n.
- Read and write Excel files or a lightweight database.
- Prevent simultaneous Excel writes using a write queue/lock.
- Normalize incoming data into the CRM schema.
- Generate stable IDs for deals, contacts, parcels, tasks, etc.
- Recalculate project financials.
- Fetch parcel boundary/polygon data from cadastral services.
- Store map coordinates and polygon data.
- Create backups before modifying Excel files.
- Return meaningful errors for failed n8n imports or user edits.

### Backend API Design

Core endpoints:

```text
GET /api/health
```

Returns whether the backend is running.

```text
GET /api/deals
```

Returns all deals for list, Kanban, dashboard, and map views.

```text
GET /api/deals/:dealId
```

Returns one deal with related property, calculation, parcels, extra costs, tasks, contacts, and documents.

```text
POST /api/deals
```

Creates a new deal from website form data or n8n data.

```text
PATCH /api/deals/:dealId
```

Updates a deal.

```text
DELETE /api/deals/:dealId
```

Deletes or archives a deal. Prefer archive for safety.

```text
POST /api/n8n/deals
```

Webhook endpoint for n8n to create or update deals.

```text
POST /api/property/parcel?lat=...&lng=...
```

Fetches exact property parcel data based on coordinates.

```text
POST /api/excel/import
GET  /api/excel/export
```

Optional import/export endpoints.

### Backend Write Safety

If Excel is used as the data source, write safety is very important.

Problem:

```text
Website user edits a deal
n8n also sends a new deal at the same time
Both write to Excel
Excel file may be corrupted or one write may overwrite the other
```

Solution:

```text
All writes go through backend
Backend queues writes
Backend locks file during write
Backend creates backup
Backend writes new file
Backend releases lock
```

Example write process:

```text
1. Receive create/update request
2. Validate request
3. Load current workbook/data
4. Apply change in memory
5. Recalculate affected deal
6. Create timestamped backup
7. Write workbook atomically
8. Return updated deal
```

## Data Source Options

There are two realistic data-source approaches.

### Option A: Excel as Data Source

This matches the current requirement.

```text
Backend reads/writes Excel files
Frontend reads data through backend API
n8n sends data to backend API
```

Pros:

- Simple and familiar.
- Works for low data volume.
- Easy to open and inspect manually.
- Good for internal tools.
- Matches the current workbook logic.

Cons:

- Requires careful write locking.
- Not ideal for many concurrent users.
- Relationships are more fragile than in a database.
- Querying/filtering is less efficient than a database.
- Excel can become messy if schema is not controlled.

Recommended Excel structure:

```text
crm-data.xlsx
  Pipeline
  Parzellen
  Baunebenkosten
  Contacts
  Tasks
  Documents
  ActivityLog
```

### Option B: Lightweight Free Database

Instead of Excel as the source of truth, use a free/low-cost database such as Turso, Supabase, Neon, or SQLite.

Pros:

- Safer writes.
- Cleaner relationships.
- Easier APIs.
- Better long-term maintainability.
- Easier filtering and reporting.

Cons:

- Less familiar than Excel.
- Needs database setup.
- Manager/team may prefer Excel-based storage.

For the current requirement, Excel can be used first, but the backend should be written in a way that could later swap Excel for a database.

## Excel Workbook Understanding

### `Kalkulation.xlsx`

This file is already shaped like a small CRM database.

It has three sheets:

```text
Pipeline
Parzellen
Baunebenkosten
```

#### Pipeline Sheet

One row per deal/project.

Columns:

```text
ID
Titel
Typ
Phase
Straße
PLZ
Ort
Bundesland
Grundstücksgröße_m2
Wohnfläche_m2
Parzellen_Einheiten
Nettokaufpreis
GIK
Deckungsbeitrag
Marge_Pct
EK_Rendite_Pct
Latitude
Longitude
Google_Maps_Link
Eingezeichnete_Flaeche_m2
Ansprechpartner
Telefon
Email
Quelle
AbsageGrund
ErstelltAm
AktualisiertAm
```

#### Parzellen Sheet

Multiple parcel/house rows per deal.

Linked by:

```text
Parzellen.Objekt_ID = Pipeline.ID
```

Columns:

```text
Objekt_ID
Objekt_Titel
Parzelle_Nr
Wohnflaeche_m2
Baukosten_je_m2
Hauskosten
Grundstueck_m2
Verkaufspreis_Haus
Gestehungskosten
Deckungsbeitrag
```

#### Baunebenkosten Sheet

Multiple extra-cost rows per deal.

Linked by:

```text
Baunebenkosten.Objekt_ID = Pipeline.ID
```

Columns:

```text
Objekt_ID
Objekt_Titel
Bezeichnung
Modus
Ansatz
Gesamt
```

### `Projektkalkulation.xlsx`

This file is a single-project calculator template, not a multi-deal database.

It has one sheet:

```text
Kalkulation
```

Sections:

```text
Grundstück & Ankauf
Baunebenkosten
Parzellen max. 10
Finanzierung
Vertrieb & Verkaufserlös
Ergebnis
```

It contains formulas for:

- Erwerbsnebenkosten.
- Bruttokaufpreis.
- Baunebenkosten total.
- Number of active parcels.
- Average land per parcel.
- Land cost per parcel.
- House costs.
- Gestehungskosten.
- Deckungsbeitrag.
- GIK.
- Equity and debt.
- Interest costs.
- Sales costs.
- Project result.
- Project margin.
- Equity return.

This file should be used as the business logic reference for the calculation engine.

## Recommended Excel Schema

If Excel remains the data source, use one controlled workbook:

```text
crm-data.xlsx
```

Recommended sheets:

```text
Pipeline
Properties
Contacts
Parzellen
Baunebenkosten
Calculations
Tasks
Documents
ActivityLog
```

### Pipeline

Stores one row per deal.

Suggested columns:

```text
deal_id
title
type
phase
source
source_reference
property_id
contact_id
created_at
updated_at
archived
absage_grund
notes
```

### Properties

Stores property/address/map data.

Suggested columns:

```text
property_id
deal_id
street
postal_code
city
state
country
latitude
longitude
google_maps_link
grundstuecksgroesse_m2
wohnflaeche_m2
einheiten
flurstueck_label
flurstueck_reference
polygon_json
polygon_area_m2
grundstueck_laenge_m
grundstueck_breite_m
bodenrichtwert_eur_m2
bodenrichtwert_stichtag
bodenrichtwert_nutzung
```

### Contacts

Stores people/companies.

Suggested columns:

```text
contact_id
name
company
role
phone
email
notes
created_at
updated_at
```

### Parzellen

Stores parcel/house rows for project-development deals.

Suggested columns:

```text
parcel_id
deal_id
parcel_number
wohnflaeche_m2
baukosten_je_m2
hauskosten
grundstueck_m2
verkaufspreis_haus
gestehungskosten
deckungsbeitrag
```

### Baunebenkosten

Stores extra costs per deal.

Suggested columns:

```text
cost_id
deal_id
label
mode
ansatz
gesamt
```

`mode` values:

```text
je Haus
Pauschal
```

### Calculations

Stores deal-level calculation inputs and outputs.

Suggested columns:

```text
calculation_id
deal_id
nettokaufpreis
kaufpreiswunsch
grunderwerbsteuer_pct
notarkosten_pct
maklerkosten_pct
sonstige_erwerbsnebenkosten_pct
eigenkapital_pct
zinssatz_pct_pa
laufzeit_monate
bearbeitungsgebuehr_pct
vertriebskosten_pct
sonstige_kosten_ertrag_pct
gik
deckungsbeitrag
marge_pct
ek_rendite_pct
updated_at
```

### Tasks

Stores tasks linked to deals.

Suggested columns:

```text
task_id
deal_id
text
category
responsible
due_date
done
created_at
updated_at
```

### Documents

Stores document links only.

Suggested columns:

```text
document_id
deal_id
name
url
note
created_at
updated_at
```

### ActivityLog

Stores import and user activity.

Suggested columns:

```text
activity_id
timestamp
source
action
entity_type
entity_id
message
status
raw_payload_json
```

## Calculation Logic

The calculation logic from `Projektkalkulation.xlsx` should be implemented in backend or shared JavaScript.

Important: store calculation inputs, not just result numbers.

Inputs to store:

```text
grundstuecksgroesse_m2
nettokaufpreis
kaufpreiswunsch
grunderwerbsteuer_pct
notarkosten_pct
maklerkosten_pct
sonstige_erwerbsnebenkosten_pct
baunebenkosten rows
parcel rows
eigenkapital_pct
zinssatz_pct_pa
laufzeit_monate
bearbeitungsgebuehr_pct
vertriebskosten_pct
sonstige_kosten_ertrag_pct
```

Outputs to calculate:

```text
erwerbsnebenkosten
bruttokaufpreis
gik
eigenkapital
fremdkapital
zinskosten
finanzierungskosten
verkaufserloes
deckungsbeitrag
marge_pct
ek_rendite_pct
gestehungskosten per parcel
deckungsbeitrag per parcel
```

The app can display output columns in Excel, but the backend/frontend should be able to recalculate them from stored inputs.

## n8n Service

### Role

n8n prepares incoming deal data from emails or other sources. Instead of sending that data to Pipedrive, n8n will send it to our backend.

### Example n8n Flow

```text
Email trigger
        |
        v
Parse email body and attachments
        |
        v
Extract property/deal fields
        |
        v
Normalize data
        |
        v
Call backend webhook
        |
        v
Backend creates or updates deal
        |
        v
Website shows the deal
```

### n8n to Backend Endpoint

Recommended endpoint:

```text
POST /api/n8n/deals
```

Example payload:

```json
{
  "source": "email",
  "source_reference": "email-message-id-or-thread-id",
  "title": "Karlsbader Straße 1, 65439 Flörsheim",
  "type": "Projektentwicklung",
  "phase": "Neues Angebot",
  "property": {
    "street": "Karlsbader Straße 1",
    "postal_code": "65439",
    "city": "Flörsheim",
    "state": "Hessen",
    "latitude": 50.0025072,
    "longitude": 8.4016706,
    "grundstuecksgroesse_m2": 1037
  },
  "contact": {
    "name": "Max Mustermann",
    "company": "Beispiel Immobilien",
    "phone": "+49...",
    "email": "max@example.com",
    "role": "Makler"
  },
  "calculation": {
    "nettokaufpreis": 390000,
    "grunderwerbsteuer_pct": 6,
    "notarkosten_pct": 1.5,
    "maklerkosten_pct": 6
  },
  "notes": "Imported from email automation"
}
```

### Duplicate Handling

n8n or backend should avoid creating duplicate deals.

Possible matching fields:

```text
source_reference
Propstack/Pipedrive/external ID
email message ID
street + postal code + city
latitude + longitude
```

Recommended:

```text
If source_reference exists, use it as primary duplicate key.
If no source_reference exists, fallback to normalized address.
```

### n8n Error Handling

Backend should return clear responses:

```json
{
  "ok": true,
  "action": "created",
  "deal_id": "deal_123"
}
```

or:

```json
{
  "ok": false,
  "error": "Missing required field: property.street"
}
```

n8n should log failed requests and optionally notify the team.

## Map and Exact Property Display

### Current Map Logic

The frontend uses Leaflet.

Basic marker display:

```text
Latitude + Longitude
        |
        v
Leaflet marker
```

Exact parcel display:

```text
Latitude + Longitude
        |
        v
Backend/Python parcel lookup
        |
        v
Parcel polygon
        |
        v
Leaflet polygon
```

The current Python service fetches cadastral parcel data from Hessen public WFS endpoints.

### Target Map Flow

Move the local Python logic into the backend:

```text
Frontend asks backend for parcel
        |
        v
Backend calls cadastral WFS
        |
        v
Backend returns polygon + area + dimensions
        |
        v
Backend stores polygon
        |
        v
Frontend displays polygon
```

Recommended endpoint:

```text
GET /api/property/parcel?lat=50.0025&lng=8.4016
```

Response:

```json
{
  "ok": true,
  "label": "Flurstück label",
  "nationalCadastralReference": "reference",
  "area_qm": 1037,
  "length_m": 42.1,
  "width_m": 24.6,
  "polygon": [[50.0025, 8.4016], [50.0026, 8.4017]],
  "bodenrichtwert_eur_m2": 500,
  "bodenrichtwert_stichtag": "2024-01-01"
}
```

### Persisting Exact Property Data

The current `Kalkulation.xlsx` stores:

```text
Latitude
Longitude
Eingezeichnete_Flaeche_m2
```

To persist exact boundaries, add:

```text
Polygon_JSON
Flurstueck_Label
Flurstueck_Reference
Grundstueck_Laenge_m
Grundstueck_Breite_m
Bodenrichtwert_EUR_m2
Bodenrichtwert_Stichtag
```

Better option:

```text
Properties.polygon_json
```

This avoids re-fetching parcel data every time the page loads.

## Deployment

Because the app is internal and data volume is low, deployment can stay lightweight.

Possible deployment setups:

### Simple VPS

```text
One small VPS
Node/FastAPI backend
Static frontend
Excel files stored on disk
Daily backups
```

Pros:

- Simple.
- Full control.
- Good for Excel file storage.

Cons:

- Server management required.

### Vercel/Render/Fly + External Storage

```text
Frontend/backend deployed serverlessly
Excel stored in object storage or database
```

Pros:

- Easy deployment.
- Low operational work.

Cons:

- Excel file writes require persistent storage solution.
- Serverless local filesystem is usually not persistent.

### Recommended If Excel Is Main Data Source

Use a small VPS or persistent backend environment where the Excel files can safely live on disk.

Minimum requirements:

```text
1 small Node.js or Python backend
256MB-512MB RAM
Persistent disk
Daily backups
Internal-only access if possible
```

## Suggested Implementation Phases

### Phase 1: Data Schema and Backend Foundation

Duration: 2-4 working days.

Tasks:

- Finalize Excel schema.
- Build backend API skeleton.
- Implement Excel read/write layer.
- Add file lock/write queue.
- Add backups.
- Add `GET /api/deals`.
- Add `GET /api/deals/:dealId`.

### Phase 2: Frontend Backend Integration

Duration: 3-5 working days.

Tasks:

- Replace `localStorage` deal loading with backend API.
- Connect pipeline list/Kanban to backend data.
- Connect deal detail page.
- Implement create/update deal via backend.
- Keep frontend state clean and reloadable.

### Phase 3: n8n Integration

Duration: 2-4 working days.

Tasks:

- Add `POST /api/n8n/deals`.
- Define n8n payload.
- Add validation.
- Add duplicate detection.
- Add activity logs.
- Test with sample email-created data.

### Phase 4: Calculation and Map Completion

Duration: 4-7 working days.

Tasks:

- Move calculation logic into backend or shared module.
- Store calculation inputs.
- Recalculate outputs after edits/imports.
- Move parcel lookup into backend.
- Store polygon data.
- Render exact property boundaries from stored polygons.

### Phase 5: Polish and Internal Production

Duration: 3-5 working days.

Tasks:

- Better error handling.
- Import/export admin tools.
- Backup restore procedure.
- Deployment.
- Documentation.
- Testing with real n8n data.

## Timeline for Manager

Recommended estimate:

```text
Basic backend-connected MVP: 1-2 weeks
Stable internal production version: 2-3 weeks
Polished version with stronger validation, backups, map parcel persistence, and n8n logging: 3-4 weeks
```

## Recommended Next Step

Before implementation, decide these points:

1. Should Excel remain the official source of truth for version 1?
2. Should we use one workbook or separate workbooks?
3. What fields will n8n send for each deal?
4. Should users be able to edit all imported fields, or only calculation/status fields?
5. Should exact property polygons be fetched automatically on import, or only when a user opens a deal and clicks a button?

Recommended first technical step:

```text
Create backend skeleton + Excel read/write layer for the current Kalkulation.xlsx schema.
```

After that, connect the frontend to `GET /api/deals` and `GET /api/deals/:id`.
