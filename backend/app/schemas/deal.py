from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

DealType = Literal["project_development", "multi_family"]
DealPhase = Literal["new", "review", "calculation", "loi", "due_diligence", "notary", "cancelled"]


class PropertyData(BaseModel):
    street: str | None = None
    postal_code: str | None = None
    city: str | None = None
    state: str | None = "Hessen"
    country: str | None = "DE"
    latitude: float | None = None
    longitude: float | None = None
    land_area_m2: float | None = None
    living_area_m2: float | None = None
    units: int | None = None
    polygon_json: str | None = None
    ground_value_eur_m2: float | None = None


class ContactData(BaseModel):
    name: str | None = None
    company: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None


class DealBase(BaseModel):
    title: str
    type: DealType = "project_development"
    phase: DealPhase = "new"
    source: str | None = None
    source_reference: str | None = None
    cancellation_reason: str | None = None
    notes: str | None = None
    property: PropertyData = Field(default_factory=PropertyData)
    contact: ContactData | None = None


class DealCreate(DealBase):
    deal_id: str | None = None


class DealUpdate(BaseModel):
    title: str | None = None
    phase: DealPhase | None = None
    source: str | None = None
    source_reference: str | None = None
    cancellation_reason: str | None = None
    notes: str | None = None
    property: PropertyData | None = None
    contact: ContactData | None = None


class DealRead(DealBase):
    deal_id: str = Field(default_factory=lambda: f"deal_{uuid4().hex}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

