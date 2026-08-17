from pydantic import BaseModel


class ParcelLookupResult(BaseModel):
    ok: bool
    label: str | None = None
    national_cadastral_reference: str | None = None
    area_qm: float | None = None
    length_m: float | None = None
    width_m: float | None = None
    polygon: list[list[float]] = []
    ground_value_eur_m2: float | None = None
    message: str | None = None

