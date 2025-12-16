# backEnd/api/routers/ski.py

from fastapi import APIRouter, Depends, Query

from backEnd.services.ski_resort_service import SkiResortService
import asyncio

router = APIRouter(prefix="/api/ski", tags=["ski"])
ski_service = SkiResortService()

def get_ski_service() -> SkiResortService:
    return ski_service
async def cleanup_ski_service():
    # close shared httpx client if your SkiResortClient has aclose()
    await ski_service.client.close()


@router.get("/geo")
async def ski_resort_geo(
    q: str = Query(..., description="Ski resort name (e.g. 'Jackson Hole')"),
    svc: SkiResortService = Depends(get_ski_service),
):
    return await svc.get_resort_geo(q)


@router.get("/hourly")
async def ski_resort_hourly(
    q: str = Query(..., description="Ski resort name"),
    units: str = Query(
        "i",
        description="Units for ski API (usually 'i' = imperial)",
    ),
    elevation: str = Query(
        "top",
        description="Elevation (top, mid, base) if supported by the API",
    ),
    svc: SkiResortService = Depends(get_ski_service),
):
    return await svc.get_resort_hourly(q, units=units, elevation=elevation)
@router.get("/forecast")
async def ski_resort_daily(
        q: str = Query(..., description="Ski resort name"),
        units: str = Query(
            "i",
            description="Units for ski API (usually 'i' = imperial)",
        ),
        elevation: str = Query(
            "top",
            description="Elevation (top, mid, base) if supported by the API",
        ),
        svc: SkiResortService = Depends(get_ski_service),
):
    return await svc.get_resort_forecast(q, units=units, elevation=elevation)

@router.get("/snow")
async def ski_resort_snow(
    q: str = Query(..., description="Ski resort name"),
    units: str = Query(
        "i",
        description="Units for ski API (usually 'i' = imperial)",
    ),
    svc: SkiResortService = Depends(get_ski_service),
):
    """
    Resort name -> geo + current snow conditions.

    Example:
        GET /api/ski/snow?q=Jackson%20Hole
    """
    return await svc.get_resort_snow(q, units=units)


@router.get("/full")
async def ski_resort_full(
    q: str = Query(..., description="Ski resort name"),
    units: str = Query(
        "i",
        description="Units for ski API (usually 'i' = imperial)",
    ),
    elevation: str = Query(
        "top",
        description="Elevation (top, mid, base) if supported by the API",
    ),
    svc: SkiResortService = Depends(get_ski_service),
):
    """
    Resort name -> geo + hourly + multi-day forecast + snow conditions.

    Example:
        GET /api/ski/full?q=Jackson%20Hole
    """
    return await svc.get_resort_full(q, units=units, elevation=elevation)
@router.get("/resorts")
async def ski_resorts_by_region(
    region: str = Query(..., description="Region code (e.g. 'USA-Idaho', 'USA-Colorado')"),
    svc: SkiResortService = Depends(get_ski_service),
):
    return await svc.get_resorts_by_region(region)