from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict, Any, List
from backEnd.core.config import settings
from backEnd.services.api_forecast_client import ApiForecastClient


def _pick_icon(weather_argument):
    if not weather_argument:
        return "☁️"
    main = (weather_argument[0].get("main") or "").lower()
    return {
        "clear": "☀️",
        "clouds": "☁️",
        "rain": "🌧️",
        "drizzle": "🌦️",
        "thunderstorm": "⛈️",
        "snow": "🌨️",
        "mist": "🌫️",
        "fog": "🌫️",
        "haze": "🌫️",
    }.get(main, "☁️")


def _to_local_time(ts_utc: int, offset_sec: int) -> datetime:
    return datetime.fromtimestamp(ts_utc, tz=timezone.utc) + timedelta(seconds=offset_sec)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _precip_mm(item: Dict[str, Any]) -> float:
    rain = item.get("rain") or {}
    snow = item.get("snow") or {}
    return _safe_float(rain.get("3h")) + _safe_float(snow.get("3h"))


def _weather_main(item: Dict[str, Any]) -> str:
    weather = item.get("weather") or []
    if not weather:
        return ""
    return (weather[0].get("main") or "").lower()


def _weather_description(item: Dict[str, Any]) -> str:
    weather = item.get("weather") or []
    if not weather:
        return "Conditions update"
    return (weather[0].get("description") or "Conditions update").capitalize()


def _wind_display_speed(speed: float, units: str | None) -> float:
    if units == "imperial":
        return speed
    if units == "standard":
        return speed
    return speed * 3.6


def _wind_unit(units: str | None) -> str:
    if units == "imperial":
        return "mph"
    if units == "standard":
        return "m/s"
    return "km/h"


def _format_time_range(start: datetime, hours: int = 3) -> str:
    end = start + timedelta(hours=hours)
    start_label = start.strftime("%I %p").lstrip("0")
    end_label = end.strftime("%I %p").lstrip("0")
    return f"{start_label}-{end_label}"


def _build_weather_insight(items: List[Dict[str, Any]], time_zone: int, units: str | None) -> Dict[str, Any]:
    window = items[:8]
    if not window:
        return {
            "severity": "low",
            "headline": "Not enough forecast data for a 24-hour brief.",
            "risks": ["Forecast details are unavailable right now."],
            "changes": ["Try refreshing or searching another location."],
            "actions": ["Check conditions again before heading out."],
        }

    local_items = [
        {
            "raw": item,
            "time": _to_local_time(int(item.get("dt") or 0), time_zone),
            "temp": _safe_float(item.get("main", {}).get("temp")),
            "pop": round(_safe_float(item.get("pop")) * 100),
            "precip": _precip_mm(item),
            "wind": _wind_display_speed(_safe_float(item.get("wind", {}).get("speed")), units),
            "main": _weather_main(item),
            "description": _weather_description(item),
        }
        for item in window
    ]

    wind_unit = _wind_unit(units)
    temp_unit = "F" if units == "imperial" else ("K" if units == "standard" else "C")
    pop_peak = max(local_items, key=lambda x: x["pop"])
    wind_peak = max(local_items, key=lambda x: x["wind"])
    temp_peak = max(local_items, key=lambda x: x["temp"])
    temp_low = min(local_items, key=lambda x: x["temp"])
    current_temp = local_items[0]["temp"]
    final_temp = local_items[-1]["temp"]
    temp_delta = round(final_temp - current_temp)

    wet_items = [
        item for item in local_items
        if item["pop"] >= 45
        or item["precip"] >= 0.2
        or item["main"] in {"rain", "drizzle", "thunderstorm", "snow"}
    ]
    storm_items = [item for item in local_items if item["main"] == "thunderstorm"]
    snow_items = [item for item in local_items if item["main"] == "snow"]
    fog_items = [item for item in local_items if item["main"] in {"mist", "fog", "haze"}]

    wind_threshold = 25 if units != "imperial" else 16
    hot_threshold = 32 if units != "imperial" else 90
    cold_threshold = 0 if units != "imperial" else 32

    risks: List[str] = []
    severity = "low"

    if storm_items:
        risks.append(f"Thunderstorm risk around {_format_time_range(storm_items[0]['time'])}.")
        severity = "elevated"
    elif snow_items:
        risks.append(f"Snow possible around {_format_time_range(snow_items[0]['time'])}.")
        severity = "elevated"
    elif wet_items:
        risks.append(f"Rain risk from {_format_time_range(wet_items[0]['time'])}; peak chance {pop_peak['pop']}%.")
        severity = "moderate"

    if wind_peak["wind"] >= wind_threshold:
        risks.append(f"Wind peaks near {round(wind_peak['wind'])} {wind_unit} around {wind_peak['time'].strftime('%I %p').lstrip('0')}.")
        severity = "elevated" if severity == "moderate" else severity

    if temp_peak["temp"] >= hot_threshold:
        risks.append(f"Heat stress possible near {round(temp_peak['temp'])} {temp_unit}.")
        severity = "moderate" if severity == "low" else severity
    elif temp_low["temp"] <= cold_threshold:
        risks.append(f"Freezing conditions possible near {round(temp_low['temp'])} {temp_unit}.")
        severity = "moderate" if severity == "low" else severity

    if fog_items and len(risks) < 3:
        risks.append(f"Low visibility possible around {_format_time_range(fog_items[0]['time'])}.")
        severity = "moderate" if severity == "low" else severity

    if not risks:
        risks.append("No major weather risks flagged in the next 24 hours.")

    changes = []
    if abs(temp_delta) >= (8 if units == "imperial" else 4):
        direction = "warms" if temp_delta > 0 else "cools"
        changes.append(f"Temperature {direction} by about {abs(temp_delta)} {temp_unit} through the next 24 hours.")
    else:
        changes.append(f"Temperature stays fairly steady, ranging {round(temp_low['temp'])}-{round(temp_peak['temp'])} {temp_unit}.")

    if wet_items:
        changes.append(f"Precipitation chance climbs as high as {pop_peak['pop']}% around {pop_peak['time'].strftime('%I %p').lstrip('0')}.")
    else:
        changes.append("Precipitation risk stays low across the upcoming 24 hours.")

    if wind_peak["wind"] - local_items[0]["wind"] >= (10 if units != "imperial" else 6):
        changes.append(f"Wind picks up from {round(local_items[0]['wind'])} to {round(wind_peak['wind'])} {wind_unit}.")

    actions = []
    if wet_items:
        actions.append(f"Carry umbrella {_format_time_range(wet_items[0]['time'])}.")
    if wind_peak["wind"] >= wind_threshold:
        actions.append(f"Secure loose outdoor items before {wind_peak['time'].strftime('%I %p').lstrip('0')}.")
    if temp_peak["temp"] >= hot_threshold:
        actions.append(f"Hydrate and avoid hard efforts near {temp_peak['time'].strftime('%I %p').lstrip('0')}.")
    elif temp_low["temp"] <= cold_threshold:
        actions.append(f"Layer up for the coldest window around {temp_low['time'].strftime('%I %p').lstrip('0')}.")

    comfortable_low = 45 if units == "imperial" else 7
    comfortable_high = 78 if units == "imperial" else 26
    run_candidates = [
        item for item in local_items
        if 5 <= item["time"].hour <= 20
        and comfortable_low <= item["temp"] <= comfortable_high
        and item["pop"] < 35
        and item["wind"] < wind_threshold
    ]
    if run_candidates:
        actions.append(f"Best run window: {_format_time_range(run_candidates[0]['time'])}.")

    if not actions:
        actions.append("Keep outdoor plans flexible and check the hourly forecast before leaving.")

    if severity == "low":
        headline = "Low-impact day with manageable conditions."
    elif severity == "moderate":
        headline = "Some weather friction expected today."
    else:
        headline = "Elevated weather risk in the next 24 hours."

    return {
        "severity": severity,
        "headline": headline,
        "risks": risks[:3],
        "changes": changes[:3],
        "actions": actions[:3],
    }


class WeatherService:
    def __init__(self, client=None):
        self.client = client if client is not None else ApiForecastClient()

    async def fetch_data(self, lat: float, lon: float, units: str | None = None) -> Dict[str, Any]:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.api_weather_key,
            "units": units or settings.units,
        }
        return await self.client._make_request("forecast", params)

    def build_context(self, data: Dict[str, Any], max_days=7, units: str | None = None) -> Dict[str, Any]:
        units = units or settings.units
        city = data.get("city", {})
        place = f'{city.get("name", "")}, {city.get("country", "")}'.strip(", ")
        if not place:
            place = "Unknown"
        time_zone = int(city.get("timezone", 0))
        now_local = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=time_zone)
        nice_date = now_local.strftime("%A, %b %d, %Y")
        items: List[Dict[str, Any]] = data.get("list", [])
        first = items[0] if items else {}
        main = first.get("main", {})
        wind = first.get("wind", {})
        current_wind = _wind_display_speed(_safe_float(wind.get("speed")), units)
        current_precip = _precip_mm(first)
        current = {
            "temp": round(float(main.get("temp", 0))),
            "feels_like": round(float(main.get("feels_like", 0))),
            "humidity": int(main.get("humidity", 0)),
            "wind": f'{round(current_wind)} {_wind_unit(units)}',
            "precip": f"{round(current_precip, 1)} mm" if current_precip else "0 mm",
            "icon": _pick_icon(first.get("weather", [])),
        }

        hourly = []
        for item in items[:8]:
            time = _to_local_time(int(item.get("dt") or 0), time_zone)
            temp = round(float(item.get("main", {}).get("temp", 0)))
            item_wind = _wind_display_speed(_safe_float(item.get("wind", {}).get("speed")), units)
            hourly.append({
                "time": time.strftime("%I %p").lstrip("0") if hasattr(time, "strftime") else "",
                "icon": _pick_icon(item.get("weather", [])),
                "temp": temp,
                "pop": round(_safe_float(item.get("pop")) * 100),
                "precip_mm": round(_precip_mm(item), 1),
                "wind": f"{round(item_wind)} {_wind_unit(units)}",
                "summary": _weather_description(item),
            })

        groups = defaultdict(list)
        for item in items:
            forecast_date = _to_local_time(item["dt"], time_zone).date()
            groups[forecast_date].append(item)
        daily = []
        for forecast_date in sorted(groups.keys())[:max_days]:
            temps = [float(x.get("main", {}).get("temp", 0)) for x in groups[forecast_date]]
            hi, lo = (round(max(temps)) if temps else 0, round(min(temps)) if temps else 0)
            mid = groups[forecast_date][len(groups[forecast_date]) // 2]
            daily.append({
                "name": forecast_date.strftime("%a"),
                "hi": hi,
                "lo": lo,
                "icon": _pick_icon(mid.get("weather", [])),
            })

        return {
            "place": place,
            "date": nice_date,
            "current": current,
            "hourly": hourly,
            "daily": daily,
            "insight": _build_weather_insight(items, time_zone, units),
        }
