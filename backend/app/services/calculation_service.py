from app.schemas.calculation import CalculationInput, CalculationResult, ParcelCalculationResult


def calculate_project_development(payload: CalculationInput) -> CalculationResult:
    parcel_count = len(payload.parcels)
    acquisition_costs = payload.net_purchase_price * (
        payload.transfer_tax_pct
        + payload.notary_pct
        + payload.broker_pct
        + payload.other_acquisition_costs_pct
    ) / 100
    gross_purchase_price = payload.net_purchase_price + acquisition_costs

    total_extra_costs = 0.0
    for cost in payload.extra_costs:
        if cost.mode.lower() in {"je haus", "je_haus", "per_house"}:
            total_extra_costs += cost.amount * parcel_count
        else:
            total_extra_costs += cost.amount

    gik = gross_purchase_price + total_extra_costs
    equity = gik * payload.equity_pct / 100
    debt = gik - equity
    interest_costs = payload.interest_rate_pct_pa / 100 * debt / 12 * payload.term_months
    financing_fee = payload.financing_fee_pct / 100 * debt
    financing_costs = interest_costs + financing_fee

    land_per_parcel = payload.land_area_m2 / parcel_count if parcel_count else 0
    land_cost_per_parcel = gross_purchase_price / parcel_count if parcel_count else 0
    extra_cost_per_parcel = total_extra_costs / parcel_count if parcel_count else 0

    parcel_results: list[ParcelCalculationResult] = []
    total_sales_revenue = 0.0
    total_parcel_margin = 0.0

    for parcel in payload.parcels:
        house_cost = parcel.living_area_m2 * parcel.construction_cost_eur_m2
        parcel_land_area = parcel.land_area_m2 if parcel.land_area_m2 is not None else land_per_parcel
        production_cost = land_cost_per_parcel + house_cost + extra_cost_per_parcel
        contribution_margin = parcel.sale_price_house - production_cost
        total_sales_revenue += parcel.sale_price_house
        total_parcel_margin += contribution_margin
        parcel_results.append(
            ParcelCalculationResult(
                parcel_number=parcel.parcel_number,
                house_cost=house_cost,
                land_area_m2=parcel_land_area,
                production_cost=production_cost,
                contribution_margin=contribution_margin,
            )
        )

    sales_costs = payload.sales_cost_pct / 100 * total_sales_revenue
    other_revenue_costs = payload.other_revenue_cost_pct / 100 * total_sales_revenue
    contribution_margin = total_parcel_margin - financing_costs - sales_costs - other_revenue_costs

    return CalculationResult(
        acquisition_costs=acquisition_costs,
        gross_purchase_price=gross_purchase_price,
        total_extra_costs=total_extra_costs,
        gik=gik,
        equity=equity,
        debt=debt,
        financing_costs=financing_costs,
        total_sales_revenue=total_sales_revenue,
        contribution_margin=contribution_margin,
        margin_pct=(contribution_margin / gik * 100) if gik else None,
        equity_return_pct=(contribution_margin / equity * 100) if equity else None,
        parcels=parcel_results,
    )

