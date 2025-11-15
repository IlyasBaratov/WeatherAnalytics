import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Date, DateTime, Float, Numeric, ForeignKey, func
)
from sqlalchemy.orm import relationship

from core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# Simple ORM models for persistence. IDs are stored as strings for
# cross-database portability in local dev; in production with Postgres you
# can map to UUID types.


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(Text, unique=True, nullable=True)
    display_name = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Provider(Base):
    __tablename__ = "providers"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(Text, unique=True, nullable=False)
    base_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Location(Base):
    __tablename__ = "locations"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    canonical_name = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country_code = Column(String(2), nullable=True)
    admin1 = Column(Text, nullable=True)
    admin2 = Column(Text, nullable=True)
    postal_code = Column(Text, nullable=True)
    landmark = Column(Text, nullable=True)
    tz_name = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Request(Base):
    __tablename__ = "requests"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("providers.id"), nullable=True)
    query_raw = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    granularity = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    location = relationship("Location")
    provider = relationship("Provider")


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("providers.id"), nullable=False)
    kind = Column(Text, nullable=False)
    snapshot_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    forecast_time = Column(DateTime, nullable=False)
    horizon_hours = Column(Integer, nullable=True)
    temperature_c = Column(Numeric(6, 2), nullable=True)
    temp_min_c = Column(Numeric(6, 2), nullable=True)
    temp_max_c = Column(Numeric(6, 2), nullable=True)
    humidity_pct = Column(Numeric(5, 2), nullable=True)
    pressure_hpa = Column(Numeric(7, 2), nullable=True)
    wind_speed_ms = Column(Numeric(6, 2), nullable=True)
    wind_gust_ms = Column(Numeric(6, 2), nullable=True)
    wind_deg = Column(Numeric(5, 1), nullable=True)
    precip_mm = Column(Numeric(7, 2), nullable=True)
    snow_mm = Column(Numeric(7, 2), nullable=True)
    cloud_pct = Column(Numeric(5, 2), nullable=True)
    pop_pct = Column(Numeric(5, 2), nullable=True)
    weather_code = Column(Text, nullable=True)
    payload_raw = Column(Text, nullable=True)
    ingested_at = Column(DateTime, nullable=False, server_default=func.now())


class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("providers.id"), nullable=False)
    observed_at = Column(DateTime, nullable=False)
    temperature_c = Column(Numeric(6, 2), nullable=True)
    humidity_pct = Column(Numeric(5, 2), nullable=True)
    pressure_hpa = Column(Numeric(7, 2), nullable=True)
    wind_speed_ms = Column(Numeric(6, 2), nullable=True)
    wind_gust_ms = Column(Numeric(6, 2), nullable=True)
    wind_deg = Column(Numeric(5, 1), nullable=True)
    precip_mm = Column(Numeric(7, 2), nullable=True)
    snow_mm = Column(Numeric(7, 2), nullable=True)
    cloud_pct = Column(Numeric(5, 2), nullable=True)
    visibility_m = Column(Numeric(9, 2), nullable=True)
    uv_index = Column(Numeric(4, 2), nullable=True)
    weather_code = Column(Text, nullable=True)
    payload_raw = Column(Text, nullable=True)
    ingested_at = Column(DateTime, nullable=False, server_default=func.now())


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

