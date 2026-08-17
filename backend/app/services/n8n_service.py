from app.repositories.deal_repository import InMemoryDealRepository
from app.schemas.deal import DealCreate, DealUpdate
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

    def ingest_deal(self, payload: N8NDealPayload) -> N8NImportResult:
        existing = (
            self.repository.find_by_source_reference(payload.source_reference)
            if payload.source_reference
            else None
        )
        mapped = {
            "title": payload.title,
            "type": TYPE_MAP.get(payload.type, "project_development"),
            "phase": PHASE_MAP.get(payload.phase, "new"),
            "source": payload.source,
            "source_reference": payload.source_reference,
            "property": payload.property,
            "contact": payload.contact,
            "notes": payload.notes,
        }

        if existing:
            deal = self.repository.update(existing.deal_id, DealUpdate(**mapped))
            return N8NImportResult(ok=True, action="updated", deal_id=deal.deal_id)

        deal = self.repository.create(DealCreate(**mapped))
        return N8NImportResult(ok=True, action="created", deal_id=deal.deal_id)

