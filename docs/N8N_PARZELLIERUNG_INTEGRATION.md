# n8n Parzellierung Integration

## Current Automation

The pasted n8n workflow currently does this:

```text
Outlook inboxes
  - ankauf@mereagroup.de
  - info@mereagroup.de
        |
        v
Merge and dedupe emails
        |
        v
Download and extract attachment/link text
        |
        v
LLM classification
        |
        v
If Immobilienangebot
        |
        v
Structured extraction LLM
        |
        v
Normalize deal/contact/organization data
        |
        v
Search/create Pipedrive person and organization
        |
        v
Create Pipedrive deal
        |
        v
Forward original email to Pipedrive and mark Outlook processed
```

The routing node currently maps:

```text
info@mereagroup.de   -> Pipedrive pipeline: Parzellierung, pipeline_id=5, stage_id=40
ankauf@mereagroup.de -> Pipedrive pipeline: Ankauf, pipeline_id=2, stage_id=6
```

For this CRM, we only care about:

```text
info@mereagroup.de -> Parzellierung deals in our CRM
```

## Target Change

Replace the Pipedrive deal creation destination for Parzellierung with our CRM backend.

Current step:

```text
Create Pipedrive Deal
POST https://api.pipedrive.com/v1/deals
```

New recommended step:

```text
Create CRM Parzellierung Deal
POST https://crm-domain.example.com/api/v1/integrations/email-offers/parzellierung
```

Header:

```text
x-n8n-token: <shared secret>
```

## Backend Endpoint

The backend now has a dedicated integration endpoint:

```text
POST /api/v1/integrations/email-offers/parzellierung
```

Legacy-compatible endpoint:

```text
POST /api/v1/n8n/parzellierung/deals
```

This endpoint accepts the actual workflow shape, including:

```text
email
classification
normalized_deal
normalized_contact
normalized_organization
pipedrive_route
```

The old generic endpoint still exists:

```text
POST /api/v1/n8n/deals
```

## Recommended n8n Payload

Send the item after `Normalize Extracted Deal Data` and `Set Target Pipedrive Route`.

Minimum useful payload:

```json
{
  "source": "n8n_outlook_info",
  "email": {
    "email_id": "outlook-message-id",
    "mailbox": "info@mereagroup.de",
    "subject": "Karben - Raiffeisenstraße 12",
    "from_name": "Broker Name",
    "from_email": "broker@example.com",
    "date": "2026-08-17T10:00:00Z"
  },
  "classification": {
    "message_type": "direct_offer",
    "is_real_estate_offer": true,
    "confidence": 0.92,
    "recommended_label": "Immobilienangebot",
    "reason": "Direct property offer with address and price"
  },
  "normalized_deal": {
    "deal_title": "Karben - Raiffeisenstraße 12",
    "property_type": "Baugrundstück",
    "address_full": "Raiffeisenstraße 12, Karben",
    "street": "Raiffeisenstraße 12",
    "city": "Karben",
    "postal_code": "",
    "country": "Germany",
    "purchase_price_eur": 990000,
    "living_area_sqm": null,
    "land_area_sqm": 2500,
    "commercial_area_sqm": null,
    "number_of_units": null,
    "annual_rent_eur": null,
    "yield_percent": null,
    "commission_percent": 3.57,
    "parking_spaces": null,
    "number_of_rooms": null,
    "gross_floor_area_sqm": null,
    "number_of_parcels": null,
    "description": "Extracted summary or expose notes"
  },
  "normalized_contact": {
    "full_name": "Broker Name",
    "email": "broker@example.com",
    "phone": "+49...",
    "mobile": ""
  },
  "normalized_organization": {
    "name": "Broker GmbH",
    "website": "https://example.com"
  },
  "pipedrive_route": {
    "source_mailbox": "info@mereagroup.de",
    "target_pipeline_name": "Parzellierung",
    "pipeline_id": 5,
    "stage_id": 40,
    "routing_reason": "Email came from info@mereagroup.de"
  }
}
```

## CRM Mapping

The backend maps the n8n fields like this:

```text
normalized_deal.deal_title       -> deal.title
info@mereagroup.de route         -> deal.type = project_development
payload/source email ID          -> deal.source_reference
normalized_deal.street           -> property.street
normalized_deal.city             -> property.city
normalized_deal.postal_code      -> property.postal_code
normalized_deal.land_area_sqm    -> property.land_area_m2
normalized_deal.living_area_sqm  -> property.living_area_m2
normalized_deal.number_of_units  -> property.units
normalized_contact               -> contact
normalized_organization.name     -> contact.company
normalized_deal.description      -> deal.notes
classification.reason            -> deal.notes/debug context
```

## Manual Deal Creation

Manual deal creation remains a normal CRM feature.

Users can create deals from the website with:

```text
POST /api/v1/deals
```

Manual and n8n-created deals use the same data model. The only difference is:

```text
n8n deals have source/source_reference/email metadata
manual deals may have source = manual
```

## Calculations

Deal creation only creates the base deal/property/contact record.

Calculations are managed inside the CRM:

```text
deal
  -> calculation inputs
  -> parcel rows
  -> extra cost rows
  -> calculated GIK, margin, EK return, etc.
```

n8n may provide starting values such as:

```text
purchase_price_eur
land_area_sqm
living_area_sqm
number_of_units
commission_percent
```

The user can then edit calculation assumptions manually in the CRM.

## Outlook Processing

The existing workflow marks emails as processed using Outlook categories.

We should keep this idea:

```text
MEREAProcessed
Immobilienangebot
Sonstiges
```

For our CRM, after a successful backend response, n8n should mark the email processed.

Backend response:

```json
{
  "ok": true,
  "action": "created",
  "deal_id": "deal_..."
}
```

Then n8n can add an Outlook category like:

```text
MEREACRMCreated
```

or keep:

```text
MEREAProcessed
```

## Important Implementation Note

Do not let n8n write directly into the database or Excel files.

Correct:

```text
n8n -> FastAPI endpoint -> service validation -> repository -> database
```

This keeps duplicate detection, validation, calculation defaults, and logs in one place.
