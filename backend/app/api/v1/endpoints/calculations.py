from fastapi import APIRouter

from app.schemas.calculation import CalculationInput, CalculationResult
from app.services.calculation_service import calculate_project_development

router = APIRouter()


@router.post("/project-development", response_model=CalculationResult)
def calculate(payload: CalculationInput) -> CalculationResult:
    return calculate_project_development(payload)

