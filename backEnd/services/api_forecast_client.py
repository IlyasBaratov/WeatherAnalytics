from typing import Optional, Dict, Any

import httpx
from fastapi import HTTPException
from core.config import settings


class ApiForecastClient:

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Simple OpenWeather forecast client.
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openweathermap.org/data/2.5"

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        # ensure API key is always sent
        params = params or {}
        if self.api_key:
            params.setdefault("appid", self.api_key)

        timeout = httpx.Timeout(settings.api_timeout)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.ReadTimeout:
            # propagate as HTTPException so FastAPI returns a 504
            raise HTTPException(status_code=504, detail="Upstream API request timed out")
        except httpx.HTTPStatusError as e:
            # re-raise as 502 Bad Gateway
            raise HTTPException(status_code=502, detail=f"Upstream API returned error: {e.response.status_code}")
        except httpx.HTTPError as e:
            # catch other transport errors
            raise HTTPException(status_code=502, detail=f"Upstream API request failed: {str(e)}")
