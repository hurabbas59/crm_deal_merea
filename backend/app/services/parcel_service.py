from app.schemas.parcel import ParcelLookupResult


class ParcelService:
    async def lookup(self, lat: float, lng: float) -> ParcelLookupResult:
        # TODO: move the working logic from grundstueck_service.py here.
        # This service will call the public cadastral WFS, return polygon data,
        # and later persist the polygon against the property/deal.
        return ParcelLookupResult(
            ok=False,
            message=(
                "Parcel lookup service is scaffolded. "
                f"Next step: migrate grundstueck_service.py for lat={lat}, lng={lng}."
            ),
        )

