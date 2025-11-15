from typing import Optional, Tuple
from core.config import settings
from .geo_client import GeoClient

class GeoService:
    def __init__(self, client: GeoClient | None = None):
        self.client = client or GeoClient()
    async def  resolve_coords_from_query(self, q: str) -> Optional[Tuple[float, float, str]]:
        '''Returns latitude, longitude and city name of the given query.'''

        rows = await self.client.direct(q=q, appid = settings.api_weather_key, limit = 1)
        if not rows:
            return None
        row = rows[0]
        lat, lon = float(row["lat"]), float(row["lon"])
        name = row.get("name") or ""
        country = row.get("country") or ""
        state = row.get("state") or ""
        place = ", ".join([p for p in [name, state, country] if p])
        return (lat, lon, place)
    async def resolve_place_from_coords(self, lat:float, lon:float) -> Optional[str]:
        '''Returns city name of the given latitude and longitude.'''
        rows = await self.client.reverse(lat=lat, lon=lon, appid=settings.api_weather_key, limit=1)
        print(rows)
        if not rows:
            return None
        row = rows[0]
        name = row.get("name") or ""
        country = row.get("country") or ""
        state = row.get("state") or ""
        return ", ".join([p for p in [name, state, country] if p]) or None
