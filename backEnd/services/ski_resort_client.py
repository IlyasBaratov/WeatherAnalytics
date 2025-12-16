from typing import Optional, Dict, Any, Tuple
from urllib.parse import quote

import httpx
from fastapi import HTTPException

from backEnd.core.config import settings


class SkiResortClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ski-resort-forecast.p.rapidapi.com",
    ) -> None:
        self.api_key = api_key or settings.api_ski_key
        self.base_url = base_url
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.api_timeout),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )

    async def close(self):
        await self._client.aclose()

    def slug(self, resort_name: str) -> str:
        return quote(resort_name.strip())

    async def get(
            self,
            path: str,
            params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise HTTPException(
                status_code=500,
                detail="Ski API key not configured. Set API_SKI_KEY in .env.",
            )

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "ski-resort-forecast.p.rapidapi.com",
        }

        try:

            resp = await self._client.get(url, headers=headers, params=params)

            # If upstream returns 4xx/5xx, keep your current behavior
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                preview = (e.response.text or "")[:300]
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Ski API error {e.response.status_code}: {preview}",
                )

            # NEW: Guard against non-JSON payloads (HTML error pages, etc.)
            ctype = (resp.headers.get("content-type") or "").lower()
            if "application/json" not in ctype:
                preview = (resp.text or "")[:300]
                raise HTTPException(
                    status_code=502,
                    detail=f"Ski API returned non-JSON response (content-type={ctype}). Preview: {preview}",
                )

            # NEW: Guard against broken JSON
            try:
                return resp.json()
            except ValueError:
                preview = (resp.text or "")[:300]
                raise HTTPException(
                    status_code=502,
                    detail=f"Ski API returned invalid JSON. Preview: {preview}",
                )

        except httpx.ReadTimeout:
            raise HTTPException(
                status_code=504,
                detail="Ski resorts upstream request timed out",
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Ski resorts API request failed: {str(e)}",
            )

    # ----- endpoints -----

    async def get_hourly_forecast(
        self,
        resort_name: str,
        *,
        units: str = "m",      # default metric (per your screenshot)
        elevation: str = "top",
    ) -> Dict[str, Any]:
        slug = self.slug(resort_name)
        params = {"units": units, "el": elevation}
        return await self.get(f"{slug}/hourly", params=params)
    async def get_daily_forecast(self,
                                 resort_name: str,
                                 *,
                                 units: str = "i",
                                 elevation: str = "top", ) -> Dict[str, Any]:
        slug = self.slug(resort_name)
        params = {"units": units, "el": elevation}
        return await self.get(f"{slug}/forecast", params=params)

    async def get_snow_conditions(
        self,
        resort_name: str,
        *,
        units: str = "i",      # imperial, as in HA example
    ) -> Dict[str, Any]:
        slug = self.slug(resort_name)
        params = {"units": units}
        return await self.get(f"{slug}/snowConditions", params=params)

    async def get_multi_day_forecast(
        self,
        resort_name: str,
        *,
        units: str = "i",
        elevation: str = "top",
    ) -> Dict[str, Any]:
        slug = self.slug(resort_name)
        params = {"units": units, "el": elevation}
        return await self.get(f"{slug}/forecast", params=params)

    async def list_regions(self) -> Dict[str, Any]:
        return await self.get("regions")

    async def list_resorts_by_region(self, region: str) -> Dict[str, Any]:
        return await self.get("resorts", params={"region": region})

