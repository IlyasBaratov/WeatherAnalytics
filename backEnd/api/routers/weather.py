from typing import Optional
from fastapi import APIRouter, Query, Depends
from services.weather_service import WeatherService
from services.geo_service import GeoService
from core.config import settings
from fastapi import Body, HTTPException, status
from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from starlette.concurrency import run_in_threadpool
from core.database import get_db
from sqlalchemy.orm import Session
import json

from models.model import Provider, Location, Request as RequestModel, WeatherForecast, Favorite

router = APIRouter(prefix="/api/weather", tags=["weather"])

def get_weather_service() -> WeatherService:
    return WeatherService()

def get_geocoding_service() -> GeoService:
    return GeoService()

@router.get("/summary")
async def summary(
    q: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    wx: WeatherService = Depends(get_weather_service),
    geo: GeoService = Depends(get_geocoding_service),
):
    if q:
        resolved = await geo.resolve_coords_from_query(q)
        if resolved:
            lat, lon, place = resolved
        else:
            lat, lon = settings.default_lat, settings.default_lon
            place = None
    else:
        lat = lat or settings.default_lat
        lon = lon or settings.default_lon
        place = await geo.resolve_place_from_coords(lat, lon)

    data = await wx.fetch_data(lat, lon)
    ctx = wx.build_context(data)
    ctx["place"] = place or ctx.get("place") or f"{lat:.4f}, {lon:.4f}"
    return ctx


# -----------------------------
# CRUD: requests and favorites
# -----------------------------


class CreateRequestBody(BaseModel):
    q: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    start_date: date
    end_date: date
    granularity: str = Field("hourly")


def validate_date_range(start_date: date, end_date: date):
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    if (end_date - start_date).days > 7:
        raise HTTPException(status_code=400, detail="date range may not exceed 7 days")


def db_get_or_create_provider(db: Session, name: str, base_url: str) -> Provider:
    p = db.query(Provider).filter(Provider.name == name).first()
    if p:
        return p
    p = Provider(name=name, base_url=base_url)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def db_get_or_create_location(db: Session, lat: float, lon: float, canonical_name: str | None = None) -> Location:
    # round coordinates to 5 decimals to match schema uniqueness
    key_lat = round(float(lat), 5)
    key_lon = round(float(lon), 5)
    loc = db.query(Location).filter(Location.latitude == key_lat, Location.longitude == key_lon).first()
    if loc:
        return loc
    loc = Location(latitude=key_lat, longitude=key_lon, canonical_name=canonical_name or f"{key_lat:.5f}, {key_lon:.5f}")
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def db_create_request(db: Session, user_id: str | None, location_id: str, provider_id: str, query_raw: str | None, start_date: date, end_date: date, granularity: str) -> RequestModel:
    req = RequestModel(user_id=user_id, location_id=location_id, provider_id=provider_id, query_raw=query_raw, start_date=start_date, end_date=end_date, granularity=granularity, status="ok")
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def db_store_forecasts(db: Session, location: Location, provider: Provider, data: dict, start_date: date, end_date: date):
    # store hourly forecasts from OpenWeather 'list' items
    now = datetime.utcnow()
    stored = 0
    items = data.get("list", [])
    for item in items:
        dt = datetime.utcfromtimestamp(int(item.get("dt", 0)))
        if dt.date() < start_date or dt.date() > end_date:
            continue
        main = item.get("main", {})
        wf = WeatherForecast(
            location_id=location.id,
            provider_id=provider.id,
            kind="hourly",
            snapshot_time=now,
            forecast_time=dt,
            temperature_c=main.get("temp"),
            temp_min_c=main.get("temp_min"),
            temp_max_c=main.get("temp_max"),
            humidity_pct=main.get("humidity"),
            payload_raw=json.dumps(item),
        )
        db.add(wf)
        stored += 1
    db.commit()
    return stored


@router.post("/requests", status_code=201)
async def create_request(body: CreateRequestBody, wx: WeatherService = Depends(get_weather_service), geo: GeoService = Depends(get_geocoding_service), db: Session = Depends(get_db)):
    validate_date_range(body.start_date, body.end_date)

    # Resolve location
    if body.q:
        resolved = await geo.resolve_coords_from_query(body.q)
        if not resolved:
            raise HTTPException(status_code=400, detail="Could not resolve location query")
        lat, lon, place = resolved
    else:
        if body.lat is None or body.lon is None:
            raise HTTPException(status_code=400, detail="Provide either 'q' or lat and lon")
        lat, lon = body.lat, body.lon
        place = await geo.resolve_place_from_coords(lat, lon)

    # Run DB create operations in threadpool
    provider = await run_in_threadpool(db_get_or_create_provider, db, "openweather", "https://api.openweathermap.org/data/2.5")
    location = await run_in_threadpool(db_get_or_create_location, db, lat, lon, place)

    # Fetch data from upstream
    data = await wx.fetch_data(lat, lon)

    # store forecasts in DB (sync)
    stored = await run_in_threadpool(db_store_forecasts, db, location, provider, data, body.start_date, body.end_date)

    # create request record
    req = await run_in_threadpool(
        db_create_request,
        db,
        None,
        str(location.id),
        str(provider.id),
        body.q or f"{lat},{lon}",
        body.start_date,
        body.end_date,
        body.granularity,
    )

    return {"request_id": req.id, "forecasts_stored": stored}


@router.get("/requests")
async def list_requests(db: Session = Depends(get_db)):
    def _list(db: Session):
        rows = db.query(RequestModel).order_by(RequestModel.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "query_raw": r.query_raw,
                "start_date": r.start_date.isoformat(),
                "end_date": r.end_date.isoformat(),
                "location_id": r.location_id,
            }
            for r in rows
        ]

    return await run_in_threadpool(_list, db)


@router.get("/requests/{request_id}")
async def get_request(request_id: str, db: Session = Depends(get_db)):
    def _get(db: Session):
        r = db.query(RequestModel).filter(RequestModel.id == request_id).first()
        if not r:
            return None
        # return forecasts stored for location in that date range
        fcs = db.query(WeatherForecast).filter(WeatherForecast.location_id == r.location_id, WeatherForecast.forecast_time >= r.start_date, WeatherForecast.forecast_time <= (r.end_date + timedelta(days=1))).all()
        return {"request": {"id": r.id, "query_raw": r.query_raw}, "forecasts": [{"forecast_time": f.forecast_time.isoformat(), "temp": str(f.temperature_c)} for f in fcs]}

    out = await run_in_threadpool(_get, db)
    if out is None:
        raise HTTPException(status_code=404, detail="request not found")
    return out


@router.delete("/requests/{request_id}", status_code=204)
async def delete_request(request_id: str, db: Session = Depends(get_db)):
    def _delete(db: Session):
        r = db.query(RequestModel).filter(RequestModel.id == request_id).first()
        if not r:
            return False
        db.delete(r)
        db.commit()
        return True

    ok = await run_in_threadpool(_delete, db)
    if not ok:
        raise HTTPException(status_code=404, detail="request not found")
    return None


class FavoriteBody(BaseModel):
    q: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@router.post("/favorites", status_code=201)
async def create_favorite(body: FavoriteBody, geo: GeoService = Depends(get_geocoding_service), db: Session = Depends(get_db)):
    # resolve location
    if body.q:
        resolved = await geo.resolve_coords_from_query(body.q)
        if not resolved:
            raise HTTPException(status_code=400, detail="Could not resolve location query")
        lat, lon, place = resolved
    else:
        if body.lat is None or body.lon is None:
            raise HTTPException(status_code=400, detail="Provide either 'q' or lat and lon")
        lat, lon = body.lat, body.lon
        place = await geo.resolve_place_from_coords(lat, lon)

    location = await run_in_threadpool(db_get_or_create_location, db, lat, lon, place)

    def _create(db: Session):
        fav = Favorite(user_id=None, location_id=location.id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return {
            "id": fav.id,
            "location_id": fav.location_id,
            "place": location.canonical_name,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }

    return await run_in_threadpool(_create, db)


@router.get("/favorites")
async def list_favorites(db: Session = Depends(get_db)):
    def _list(db: Session):
        rows = (
            db.query(Favorite, Location)
            .join(Location, Favorite.location_id == Location.id)
            .order_by(Favorite.created_at.desc())
            .all()
        )
        out = []
        for fav, loc in rows:
            out.append({
                "id": fav.id,
                "location_id": fav.location_id,
                "place": loc.canonical_name,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            })
        return out

    return await run_in_threadpool(_list, db)


@router.delete("/favorites/{fav_id}", status_code=204)
async def delete_favorite(fav_id: str, db: Session = Depends(get_db)):
    def _delete(db: Session):
        f = db.query(Favorite).filter(Favorite.id == fav_id).first()
        if not f:
            return False
        db.delete(f)
        db.commit()
        return True

    ok = await run_in_threadpool(_delete, db)
    if not ok:
        raise HTTPException(status_code=404, detail="favorite not found")
    return None


# -----------------------------
# Additional CRUD for forecasts and requests (READ/UPDATE/DELETE)
# -----------------------------

class ForecastFilter(BaseModel):
    location_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@router.get("/forecasts")
async def list_forecasts(
    location_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    def _list(db: Session):
        q = db.query(WeatherForecast)
        if location_id:
            q = q.filter(WeatherForecast.location_id == location_id)
        if start_date:
            q = q.filter(WeatherForecast.forecast_time >= start_date)
        if end_date:
            # include the full end day
            q = q.filter(WeatherForecast.forecast_time < (end_date + timedelta(days=1)))
        rows = q.order_by(WeatherForecast.forecast_time.asc()).limit(1000).all()
        return [
            {
                "id": f.id,
                "location_id": f.location_id,
                "forecast_time": f.forecast_time.isoformat(),
                "temperature_c": (str(f.temperature_c) if f.temperature_c is not None else None),
                "humidity_pct": (str(f.humidity_pct) if f.humidity_pct is not None else None),
                "kind": f.kind,
            }
            for f in rows
        ]

    return await run_in_threadpool(_list, db)


class UpdateForecastBody(BaseModel):
    temperature_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_gust_ms: Optional[float] = None
    wind_deg: Optional[float] = None
    precip_mm: Optional[float] = None
    snow_mm: Optional[float] = None
    cloud_pct: Optional[float] = None
    pop_pct: Optional[float] = None
    weather_code: Optional[str] = None


@router.patch("/forecasts/{forecast_id}")
async def update_forecast(forecast_id: str, body: UpdateForecastBody, db: Session = Depends(get_db)):
    def _update(db: Session):
        f = db.query(WeatherForecast).filter(WeatherForecast.id == forecast_id).first()
        if not f:
            return None
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(f, field, value)
        db.add(f)
        db.commit()
        db.refresh(f)
        return {
            "id": f.id,
            "forecast_time": f.forecast_time.isoformat(),
            "temperature_c": (str(f.temperature_c) if f.temperature_c is not None else None),
            "humidity_pct": (str(f.humidity_pct) if f.humidity_pct is not None else None),
            "weather_code": f.weather_code,
        }

    out = await run_in_threadpool(_update, db)
    if out is None:
        raise HTTPException(status_code=404, detail="forecast not found")
    return out


@router.delete("/forecasts/{forecast_id}", status_code=204)
async def delete_forecast(forecast_id: str, db: Session = Depends(get_db)):
    def _delete(db: Session):
        f = db.query(WeatherForecast).filter(WeatherForecast.id == forecast_id).first()
        if not f:
            return False
        db.delete(f)
        db.commit()
        return True

    ok = await run_in_threadpool(_delete, db)
    if not ok:
        raise HTTPException(status_code=404, detail="forecast not found")
    return None


class UpdateRequestBody(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


@router.patch("/requests/{request_id}")
async def update_request(request_id: str, body: UpdateRequestBody, db: Session = Depends(get_db)):
    # validate date range if provided
    if body.start_date and body.end_date:
        validate_date_range(body.start_date, body.end_date)
    # additional value checks
    if body.granularity and body.granularity not in {"current", "hourly", "daily"}:
        raise HTTPException(status_code=400, detail="granularity must be one of: current, hourly, daily")
    if body.status and body.status not in {"pending", "ok", "error"}:
        raise HTTPException(status_code=400, detail="status must be one of: pending, ok, error")

    def _update(db: Session):
        r = db.query(RequestModel).filter(RequestModel.id == request_id).first()
        if not r:
            return None
        if body.start_date is not None:
            setattr(r, "start_date", body.start_date)
        if body.end_date is not None:
            setattr(r, "end_date", body.end_date)
        if body.granularity is not None:
            setattr(r, "granularity", body.granularity)
        if body.status is not None:
            setattr(r, "status", body.status)
        if body.error_message is not None:
            setattr(r, "error_message", body.error_message)
        db.add(r)
        db.commit()
        db.refresh(r)
        return {
            "id": r.id,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat(),
            "granularity": r.granularity,
            "status": r.status,
        }

    out = await run_in_threadpool(_update, db)
    if out is None:
        raise HTTPException(status_code=404, detail="request not found")
    return out
