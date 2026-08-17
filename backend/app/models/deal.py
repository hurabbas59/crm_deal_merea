from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Deal(Base):
    __tablename__ = "deals"

    deal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False, default="project_development")
    phase: Mapped[str] = mapped_column(String(64), nullable=False, default="new")
    source: Mapped[str | None] = mapped_column(String(128))
    source_reference: Mapped[str | None] = mapped_column(String(255), unique=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    property: Mapped["Property"] = relationship(back_populates="deal", cascade="all, delete-orphan")


class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.deal_id"), nullable=False)
    street: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(128))
    state: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(8), default="DE")
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    land_area_m2: Mapped[float | None] = mapped_column(Float)
    living_area_m2: Mapped[float | None] = mapped_column(Float)
    units: Mapped[int | None]
    polygon_json: Mapped[str | None] = mapped_column(Text)
    ground_value_eur_m2: Mapped[float | None] = mapped_column(Float)

    deal: Mapped[Deal] = relationship(back_populates="property")

