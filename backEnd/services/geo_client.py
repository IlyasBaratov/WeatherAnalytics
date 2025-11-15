from typing import Dict, Any, Optional, List
import httpx
from fastapi import HTTPException
from core.config import settings


class GeoClient:
    def __init__(self, base_url: str = "http://api.openweathermap.org/geo/1.0"):
        self.base_url = base_url

    async def get(self, path: str, params: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/{path}"
        timeout = httpx.Timeout(settings.api_timeout)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=502,
                        detail="OpenWeather API authentication failed (401). Check API key."
                    )
                response.raise_for_status()
                return response.json()
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Geocoding upstream request timed out")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Geocoding upstream request failed: {str(e)}")

    async def direct(self, q: str, appid: str, limit: int = 1) -> List[Dict[str, Any]]:
        return await self.get("direct", {"q": q, "limit": limit, "appid": appid})

    async def reverse(self, lat: float, lon: float, appid: str, limit: int = 1) -> List[Dict[str, Any]]:
        return await self.get("reverse", {"lat": lat, "lon": lon, "limit": limit, "appid": appid})