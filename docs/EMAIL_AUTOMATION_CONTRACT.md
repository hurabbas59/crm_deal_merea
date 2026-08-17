# Email Automation Contract

## Purpose

The new email automation should send structured property offer data directly to this CRM. It should not send data in a Pipedrive-specific or Propstack-specific shape. The CRM backend owns validation, duplicate handling, storage, calculation defaults, and later database writes.

## Target Flow

```text
info@mereagroup.de receives a new property offer email
        |
        v
n8n fetches the email
        |
        v
n8n extracts attachments, expose links, and email text
        |
        v
n8n classifies the email as Immobilienangebot or Sonstiges
        |
        v
n8n extracts structured deal/contact/property fields
        |
        v
n8n sends the normalized payload to FastAPI
        |
        v
FastAPI creates or updates a Parzellierung deal
        |
        v
React CRM displays the deal and users manage calculations manually
```

## Recommended Endpoint

Use this endpoint for `info@mereagroup.de` Parzellierung offers:

```text
POST /api/v1/integrations/email-offers/parzellierung
```

Header:

```text
x-n8n-token: <shared secret from N8N_WEBHOOK_TOKEN>
```

Generic endpoint, if later needed:

```text
POST /api/v1/integrations/email-offers
```

Legacy-compatible endpoint kept for old n8n tests:

```text
POST /api/v1/n8n/parzellierung/deals
```

## Payload Shape

Recommended payload:

```json
{
  "source": "n8n_email",
  "source_reference": "outlook-message-id-or-internet-message-id",
  "email": {
    "email_id": "outlook-message-id",
    "mailbox": "info@mereagroup.de",
    "subject": "Karben - Raiffeisenstraße 12",
    "from_name": "Broker Name",
    "from_email": "broker@example.com",
    "date": "2026-08-17T10:00:00Z",
    "web_link": "https://outlook.office.com/..."
  },
  "classification": {
    "message_type": "direct_offer",
    "is_real_estate_offer": true,
    "confidence": 0.92,
    "recommended_label": "Immobilienangebot",
    "reason": "Direct property offer with address and price"
  },
  "route": {
    "source_mailbox": "info@mereagroup.de",
    "pipeline_name": "Parzellierung",
    "target_phase": "Neues Angebot",
    "routing_reason": "Email came from info@mereagroup.de"
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
    "description": "Extracted notes from email, expose, or attachments"
  },
  "normalized_contact": {
    "first_name": "",
    "last_name": "",
    "full_name": "Broker Name",
    "email": "broker@example.com",
    "phone": "+49...",
    "mobile": ""
  },
  "normalized_organization": {
    "name": "Broker GmbH",
    "website": "https://example.com"
  },
  "raw": {
    "email_text": "Optional full extracted text",
    "attachment_names": ["expose.pdf"]
  }
}
```

## Duplicate Handling

The backend should use this priority:

```text
1. source_reference
2. email.email_id
3. email.web_link
4. normalized address fallback
```

The current scaffold already uses `source_reference`, `email.email_id`, or `email.web_link`. Address-based duplicate logic will be added when the Postgres repository is implemented.

## Manual Deals

Manual deals stay part of the CRM:

```text
POST /api/v1/deals
```

Manual and automation-created deals should share the same database tables. The difference is only metadata:

```text
automation deal -> source = n8n_email
manual deal     -> source = manual
```

## Calculation Ownership

n8n should only send starting property/commercial fields:

```text
purchase_price_eur
land_area_sqm
living_area_sqm
number_of_units
commission_percent
number_of_parcels
```

The CRM owns the calculation workflow:

```text
purchase assumptions
parcel rows
extra costs
financing assumptions
GIK
Deckungsbeitrag
Marge
EK-Rendite
```

Users can edit these values manually after the deal is created.

## Response

Success:

```json
{
  "ok": true,
  "action": "created",
  "deal_id": "deal_..."
}
```

If the same email/deal is sent again:

```json
{
  "ok": true,
  "action": "updated",
  "deal_id": "deal_..."
}
```

