from datetime import datetime
from uuid import uuid4

from app.schemas.deal import DealCreate, DealRead, DealUpdate


class InMemoryDealRepository:
    """Temporary repository for API scaffolding.

    Replace this with PostgresRepository or ExcelRepository once the schema is finalized.
    """

    def __init__(self) -> None:
        self._deals: dict[str, DealRead] = {}

    def list(self) -> list[DealRead]:
        return sorted(self._deals.values(), key=lambda deal: deal.updated_at, reverse=True)

    def get(self, deal_id: str) -> DealRead | None:
        return self._deals.get(deal_id)

    def create(self, payload: DealCreate) -> DealRead:
        now = datetime.utcnow()
        deal_id = payload.deal_id or f"deal_{uuid4().hex}"
        deal = DealRead(**payload.model_dump(exclude={"deal_id"}), deal_id=deal_id, created_at=now, updated_at=now)
        self._deals[deal_id] = deal
        return deal

    def update(self, deal_id: str, payload: DealUpdate) -> DealRead | None:
        existing = self.get(deal_id)
        if not existing:
            return None
        data = existing.model_dump()
        for key, value in payload.model_dump(exclude_unset=True).items():
            data[key] = value
        data["updated_at"] = datetime.utcnow()
        deal = DealRead(**data)
        self._deals[deal_id] = deal
        return deal

    def find_by_source_reference(self, source_reference: str) -> DealRead | None:
        for deal in self._deals.values():
            if deal.source_reference == source_reference:
                return deal
        return None


deal_repository = InMemoryDealRepository()

