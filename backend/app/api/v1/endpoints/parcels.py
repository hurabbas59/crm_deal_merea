from fastapi import APIRouter

from app.schemas.parcel import ParcelLookupResult
from app.services.parcel_service import ParcelService

router = APIRouter()


@router.get("/lookup", response_model=ParcelLookupResult)
async def lookup_parcel(lat: float, lng: float) -> ParcelLookupResult:
    return await ParcelService().lookup(lat=lat, lng=lng)

