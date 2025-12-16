# backEnd/services/ski_resort_service.py
import asyncio
from typing import Optional, Dict, Any, Tuple

from fastapi import HTTPException

from backEnd.services.geo_service import GeoService
from backEnd.services.ski_resort_client import SkiResortClient


class SkiResortService:

    def __init__(
        self,
        client: Optional[SkiResortClient] = None,
        geo_service: Optional[GeoService] = None,
    ) -> None:
        self.client = client or SkiResortClient()
        self.geo = geo_service or GeoService()

    # ---------- helpers ----------

    async def _resolve_geo_strict(
        self,
        resort_query: str,
    ) -> Tuple[float, float, str]:
        """
        Strict geocoding (used by /api/ski/geo).
        """
        result = await self.geo.resolve_coords_from_query(resort_query)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Could not resolve location for resort '{resort_query}'",
            )
        return result  # (lat, lon, place)

    async def _try_resolve_geo(
        self,
        resort_query: str,
    ) -> Optional[Tuple[float, float, str]]:
        """
        Best-effort geocoding: try a few variants and
        return None if nothing found.
        """
        candidates = [
            f"{resort_query}, US",
            f"{resort_query}, USA",
            f"{resort_query} ski resort, US",
            resort_query,  # fallback last
        ]

        for q in candidates:
            result = await self.geo.resolve_coords_from_query(q)
            if result:
                lat, lon, place = result
                # place is like "Seattle, WA, US" from GeoService
                if not place.endswith("US"):
                    continue
                return result

        return None

    # ---------- public methods ----------

    async def get_resort_geo(
        self,
        resort_query: str,
    ) -> Dict[str, Any]:
        """
        Only geocoding (strict).
        """
        lat, lon, place = await self._resolve_geo_strict(resort_query)
        return {
            "query": resort_query,
            "place": place,
            "lat": lat,
            "lon": lon,
        }

    async def get_resort_hourly(
        self,
        resort_query: str,
        *,
        units: str = "i",
        elevation: str = "top",
    ) -> Dict[str, Any]:
        """
        Resort name -> geo (if available) + hourly forecast.
        """
        geo = await self._try_resolve_geo(resort_query)
        if geo:
            lat, lon, place = geo
        else:
            lat = lon = None
            place = resort_query

        hourly = await self.client.get_hourly_forecast(
            resort_query,
            units=units,
            elevation=elevation,
        )

        return {
            "query": resort_query,
            "geo": {"place": place, "lat": lat, "lon": lon},
            "hourly": hourly,
        }
    async def get_resort_forecast(self,
                               resort_query: str,
                               *,
                               units: str = "i",
                               elevation: str = "top", ) -> Dict[str, Any]:
        geo = await self._try_resolve_geo(resort_query)
        if geo:
            lat, lon, place = geo
        else:
            lat = lon = None
            place = resort_query

        daily = await self.client.get_daily_forecast(
            resort_query,
            units=units,
            elevation=elevation,
        )
        return {
            "query": resort_query,
            "geo": {"place": place, "lat": lat, "lon": lon},
            "daily": daily,
        }

    async def get_resort_snow(
        self,
        resort_query: str,
        *,
        units: str = "i",
    ) -> Dict[str, Any]:
        """
        Resort name -> geo (if available) + current snow conditions.
        """
        geo = await self._try_resolve_geo(resort_query)
        if geo:
            lat, lon, place = geo
        else:
            lat = lon = None
            place = resort_query

        snow = await self.client.get_snow_conditions(
            resort_query,
            units=units,
        )

        return {
            "query": resort_query,
            "geo": {"place": place, "lat": lat, "lon": lon},
            "snow": snow,
        }

    async def get_resort_full(
        self,
        resort_query: str,
        *,
        units: str = "i",
        elevation: str = "top",
    ) -> Dict[str, Any]:
        """
        Geo (if available) + hourly + multi-day + snow.
        """
        geo = await self._try_resolve_geo(resort_query)
        if geo:
            lat, lon, place = geo
        else:
            lat = lon = None
            place = resort_query

        hourly = await self.client.get_hourly_forecast(
            resort_query,
            units=units,
            elevation=elevation,
        )
        snow = await self.client.get_snow_conditions(
            resort_query,
            units=units,
        )
        forecast = await self.client.get_multi_day_forecast(
            resort_query,
            units=units,
            elevation=elevation,
        )

        return {
            "query": resort_query,
            "geo": {"place": place, "lat": lat, "lon": lon},
            "hourly": hourly,
            "snow": snow,
            "forecast": forecast,
        }

    async def get_resorts_by_region(self, region: str) -> Dict[str, Any]:
        return await self.client.list_resorts_by_region(region)
