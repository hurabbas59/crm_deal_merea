from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.repositories.deal_repository import deal_repository
from app.schemas.n8n import N8NDealPayload, N8NImportResult
from app.services.n8n_service import N8NService

router = APIRouter()


@router.post("/email-offers", response_model=N8NImportResult)
def ingest_email_offer(
    payload: N8NDealPayload,
    x_n8n_token: str | None = Header(default=None),
) -> N8NImportResult:
    if settings.n8n_webhook_token and x_n8n_token != settings.n8n_webhook_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid n8n token")
    return N8NService(deal_repository).ingest_deal(payload)


@router.post("/email-offers/parzellierung", response_model=N8NImportResult)
def ingest_parzellierung_email_offer(
    payload: N8NDealPayload,
    x_n8n_token: str | None = Header(default=None),
) -> N8NImportResult:
    if settings.n8n_webhook_token and x_n8n_token != settings.n8n_webhook_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid n8n token")
    return N8NService(deal_repository).ingest_deal(payload, force_parzellierung=True)
