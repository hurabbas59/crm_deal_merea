from fastapi import APIRouter, HTTPException, status

from app.repositories.deal_repository import deal_repository
from app.schemas.deal import DealCreate, DealRead, DealUpdate
from app.services.deal_service import DealService

router = APIRouter()


def get_service() -> DealService:
    return DealService(deal_repository)


@router.get("", response_model=list[DealRead])
def list_deals() -> list[DealRead]:
    return get_service().list_deals()


@router.get("/{deal_id}", response_model=DealRead)
def get_deal(deal_id: str) -> DealRead:
    deal = get_service().get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
def create_deal(payload: DealCreate) -> DealRead:
    return get_service().create_deal(payload)


@router.patch("/{deal_id}", response_model=DealRead)
def update_deal(deal_id: str, payload: DealUpdate) -> DealRead:
    deal = get_service().update_deal(deal_id, payload)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal

