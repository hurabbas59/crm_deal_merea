from app.repositories.deal_repository import InMemoryDealRepository
from app.schemas.deal import ContactData, DealCreate, DealUpdate, PropertyData
from app.schemas.n8n import N8NDealPayload, N8NImportResult


PHASE_MAP = {
    "Neues Angebot": "new",
    "Prüfung": "review",
    "Kalkulation": "calculation",
    "LOI": "loi",
    "Due Diligence": "due_diligence",
    "Notar": "notary",
    "Absagen": "cancelled",
}

TYPE_MAP = {
    "Projektentwicklung": "project_development",
    "MFH-Aufteilung": "multi_family",
}


class N8NService:
    def __init__(self, repository: InMemoryDealRepository) -> None:
        self.repository = repository

    def ingest_deal(
        self,
        payload: N8NDealPayload,
        force_parzellierung: bool = False,
    ) -> N8NImportResult:
        normalized_deal = payload.normalized_deal
        normalized_contact = payload.normalized_contact
        normalized_organization = payload.normalized_organization
        email = payload.email
        route = payload.route or payload.pipedrive_route

        source_reference = (
            payload.source_reference
            or (email.email_id if email else None)
            or (email.web_link if email else None)
        )
        existing = (
            self.repository.find_by_source_reference(source_reference)
            if source_reference
            else None
        )

        is_parzellierung = force_parzellierung or (
            route is not None
            and (
                route.target_pipeline_name == "Parzellierung"
                or route.pipeline_name == "Parzellierung"
                or route.pipeline_id == 5
                or route.target_phase == "Parzellierung"
                or (route.source_mailbox or "").lower().find("info@mereagroup.de") >= 0
            )
        )

        title = (
            payload.title
            or (normalized_deal.deal_title if normalized_deal else None)
            or (email.subject if email else None)
            or "New Parzellierung Deal"
        )

        property_data = payload.property
        if normalized_deal:
            normalized_country = (normalized_deal.country or "").lower()
            property_data = PropertyData(
                street=normalized_deal.street or normalized_deal.address_full,
                postal_code=normalized_deal.postal_code,
                city=normalized_deal.city,
                country=(
                    "DE"
                    if normalized_country in {"germany", "deutschland", "de"}
                    else normalized_deal.country
                ),
                land_area_m2=normalized_deal.land_area_sqm,
                living_area_m2=normalized_deal.living_area_sqm,
                units=normalized_deal.number_of_units,
            )

        contact_data = payload.contact
        if normalized_contact:
            contact_data = ContactData(
                name=normalized_contact.full_name
                or " ".join(
                    part
                    for part in [normalized_contact.first_name, normalized_contact.last_name]
                    if part
                )
                or None,
                company=normalized_organization.name if normalized_organization else None,
                role="Anbieter",
                phone=normalized_contact.phone or normalized_contact.mobile,
                email=normalized_contact.email,
            )

        notes_parts = []
        if payload.notes:
            notes_parts.append(payload.notes)
        if normalized_deal and normalized_deal.description:
            notes_parts.append(normalized_deal.description)
        if payload.classification and payload.classification.reason:
            notes_parts.append(f"n8n classification: {payload.classification.reason}")

        mapped = {
            "title": title,
            "type": (
                "project_development"
                if is_parzellierung
                else TYPE_MAP.get(payload.type, "project_development")
            ),
            "phase": PHASE_MAP.get((route.target_phase if route else None) or payload.phase, "new"),
            "source": payload.source,
            "source_reference": source_reference,
            "property": property_data,
            "contact": contact_data,
            "notes": "\n\n".join(notes_parts) if notes_parts else None,
        }

        if existing:
            deal = self.repository.update(existing.deal_id, DealUpdate(**mapped))
            return N8NImportResult(ok=True, action="updated", deal_id=deal.deal_id)

        deal = self.repository.create(DealCreate(**mapped))
        return N8NImportResult(ok=True, action="created", deal_id=deal.deal_id)
