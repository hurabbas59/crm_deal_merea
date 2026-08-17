from app.repositories.deal_repository import InMemoryDealRepository
from app.schemas.deal import DealCreate, DealRead, DealUpdate


class DealService:
    def __init__(self, repository: InMemoryDealRepository) -> None:
        self.repository = repository

    def list_deals(self) -> list[DealRead]:
        return self.repository.list()

    def get_deal(self, deal_id: str) -> DealRead | None:
        return self.repository.get(deal_id)

    def create_deal(self, payload: DealCreate) -> DealRead:
        return self.repository.create(payload)

    def update_deal(self, deal_id: str, payload: DealUpdate) -> DealRead | None:
        return self.repository.update(deal_id, payload)

