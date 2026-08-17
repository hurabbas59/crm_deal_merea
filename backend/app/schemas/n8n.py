from pydantic import BaseModel, Field

from app.schemas.deal import ContactData, PropertyData


class N8NDealPayload(BaseModel):
    source: str = "n8n"
    source_reference: str | None = None
    title: str
    type: str = "Projektentwicklung"
    phase: str = "Neues Angebot"
    property: PropertyData = Field(default_factory=PropertyData)
    contact: ContactData | None = None
    notes: str | None = None


class N8NImportResult(BaseModel):
    ok: bool
    action: str
    deal_id: str
