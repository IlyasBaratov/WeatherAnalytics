from datetime import datetime, timedelta, timezone, date
from collections import defaultdict
from typing import Dict, Any, List
from core.config import settings
from services.api_forecast_client import ApiForecastClient


def _pick_icon(weather_argument):
    if not weather_argument: return "☁️"
    main = (weather_argument[0].get("main") or "").lower()
    return {
        "clear": "☀️", "clouds": "☁️", "rain": "🌧️", "drizzle": "🌦️",
        "thunderstorm": "🌩️", "snow": "🌨️", "mist": "🌫️", "fog": "🌫️", "haze": "🌫️"
    }.get(main, "☁️")
def _to_local_time(ts_utc: int, offset_sec: int) -> datetime:
    return datetime.fromtimestamp(ts_utc, tz=timezone.utc) + timedelta(seconds=offset_sec)


class WeatherService:
    def __init__(self, client = None):
        self.client = client if client is not None else ApiForecastClient()
        
    async def fetch_data(self, lat: float, lon:float) -> Dict[str, Any]:
        params = {
            'lat': lat, 'lon': lon,
            'appid': settings.api_weather_key,
            'units': settings.units
        }
        return await self.client._make_request('forecast', params)
        
    def build_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        city = data.get("city", {})
        place = f'{city.get("name", "")}, {city.get("country", "")}'.strip(", ")
        if not place:
            place = "Unknown"
        time_zone = int(city.get("timezone", 0))
        now_local = datetime.utcnow().replace(tzinfo=timezone.utc)+timedelta(seconds=time_zone)
        nice_date = now_local.strftime("%A, %b %d, %Y")
        items: List[Dict[str, Any]] = data.get("list", [])
        first = items[0] if items else {}
        main = first.get("main", {})
        wind = first.get("wind", {})
        current = {
            "temp": round(float(main.get("temp", 0))),
            "feels_like": round(float(main.get("feels_like", 0))),
            "humidity": int(main.get("humidity", 0)),
            "wind": f'{round(float(wind.get("speed", 0)))} km/h',
            "precip": "0 mm",
            "icon": _pick_icon(first.get("weather", [])),
        }

        '''Hourly data: next 8 *3 hours'''
        hourly = []
        for item in items[:8]:
            time = _to_local_time(item.get("dt"), time_zone)
            temp = round(float(item.get("main", {}).get("temp", 0)))
            hourly.append({
                "time": time.strftime("%I %p").lstrip("0") if hasattr(time, "strftime") else "",
                "icon": _pick_icon(item.get("weather", [])),
                "temp": temp
            })

        '''Daily data: next 7 days'''
        groups = defaultdict(list)
        for item in items:
            date = _to_local_time(item["dt"], time_zone).date()
            groups[date].append(item)
        daily = []
        for date in sorted(groups.keys())[:7]:
            temps = [float(x.get("main", {}).get("temp", 0)) for x in groups[date]]
            hi, lo = (round(max(temps)) if temps else 0, round(min(temps)) if temps else 0)
            mid = groups[date][len(groups[date]) // 2]
            daily.append({"name": date.strftime("%a"), "hi": hi, "lo": lo, "icon": _pick_icon(mid.get("weather", []))})
        return{"place":place, "date":nice_date, "current":current, "hourly":hourly, "daily":daily}