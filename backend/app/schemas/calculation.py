from pydantic import BaseModel, Field


class ExtraCostInput(BaseModel):
    label: str
    mode: str = "Pauschal"
    amount: float = 0


class ParcelInput(BaseModel):
    parcel_number: int
    living_area_m2: float = 0
    construction_cost_eur_m2: float = 0
    sale_price_house: float = 0
    land_area_m2: float | None = None


class CalculationInput(BaseModel):
    land_area_m2: float = 0
    net_purchase_price: float = 0
    transfer_tax_pct: float = 6
    notary_pct: float = 1.5
    broker_pct: float = 6
    other_acquisition_costs_pct: float = 0.5
    equity_pct: float = 20
    interest_rate_pct_pa: float = 6
    term_months: int = 12
    financing_fee_pct: float = 0
    sales_cost_pct: float = 1.5
    other_revenue_cost_pct: float = 0
    extra_costs: list[ExtraCostInput] = Field(default_factory=list)
    parcels: list[ParcelInput] = Field(default_factory=list)


class ParcelCalculationResult(BaseModel):
    parcel_number: int
    house_cost: float
    land_area_m2: float
    production_cost: float
    contribution_margin: float


class CalculationResult(BaseModel):
    acquisition_costs: float
    gross_purchase_price: float
    total_extra_costs: float
    gik: float
    equity: float
    debt: float
    financing_costs: float
    total_sales_revenue: float
    contribution_margin: float
    margin_pct: float | None
    equity_return_pct: float | None
    parcels: list[ParcelCalculationResult]
