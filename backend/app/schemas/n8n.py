from pydantic import BaseModel, ConfigDict, Field

from app.schemas.deal import ContactData, PropertyData


class N8NEmailData(BaseModel):
    model_config = ConfigDict(extra="allow")

    email_id: str | None = None
    mailbox: str | None = None
    subject: str | None = None
    from_name: str | None = None
    from_email: str | None = None
    date: str | None = None
    body_clean: str | None = None
    web_link: str | None = None


class N8NClassificationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    message_type: str | None = None
    is_real_estate_offer: bool | None = None
    confidence: float | None = None
    reason: str | None = None
    recommended_label: str | None = None


class N8NNormalizedDealData(BaseModel):
    model_config = ConfigDict(extra="allow")

    deal_title: str | None = None
    property_type: str | None = None
    address_full: str | None = None
    street: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    purchase_price_eur: float | None = None
    living_area_sqm: float | None = None
    land_area_sqm: float | None = None
    commercial_area_sqm: float | None = None
    number_of_units: int | None = None
    annual_rent_eur: float | None = None
    yield_percent: float | None = None
    commission_percent: float | None = None
    parking_spaces: int | None = None
    number_of_rooms: float | None = None
    gross_floor_area_sqm: float | None = None
    number_of_parcels: int | None = None
    description: str | None = None


class N8NNormalizedContactData(BaseModel):
    model_config = ConfigDict(extra="allow")

    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None


class N8NNormalizedOrganizationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    website: str | None = None


class N8NRouteData(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_mailbox: str | None = None
    target_pipeline_name: str | None = None
    pipeline_name: str | None = None
    pipeline_id: int | None = None
    stage_id: int | None = None
    target_phase: str | None = None
    routing_reason: str | None = None


class N8NDealPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    source: str = "n8n"
    source_reference: str | None = None
    title: str | None = None
    type: str = "Projektentwicklung"
    phase: str = "Neues Angebot"
    property: PropertyData = Field(default_factory=PropertyData)
    contact: ContactData | None = None
    notes: str | None = None

    email: N8NEmailData | None = None
    classification: N8NClassificationData | None = None
    normalized_deal: N8NNormalizedDealData | None = None
    normalized_contact: N8NNormalizedContactData | None = None
    normalized_organization: N8NNormalizedOrganizationData | None = None
    route: N8NRouteData | None = None
    pipedrive_route: N8NRouteData | None = None


class N8NImportResult(BaseModel):
    ok: bool
    action: str
    deal_id: str
