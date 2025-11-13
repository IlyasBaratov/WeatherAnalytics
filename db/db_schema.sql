
-- SQLite-compatible schema for WeatherAnalytics
-- Note: IDs stored as TEXT (UUID strings). Timestamps use DATETIME with CURRENT_TIMESTAMP defaults.
PRAGMA foreign_keys = ON;

-- =========================================
-- users (optional but useful)
-- =========================================
CREATE TABLE IF NOT EXISTS users (
id TEXT PRIMARY KEY,
  email        TEXT UNIQUE,
  display_name TEXT,
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- =========================================
-- providers (Open-Meteo, OpenWeather, etc.)
-- =========================================
CREATE TABLE IF NOT EXISTS providers (
id TEXT PRIMARY KEY,
name TEXT NOT NULL UNIQUE,
  base_url     TEXT,
  notes        TEXT,
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- locations — canonicalized places
-- =========================================
CREATE TABLE IF NOT EXISTS locations (
id TEXT PRIMARY KEY,
canonical_name TEXT NOT NULL,
latitude REAL NOT NULL,
longitude REAL NOT NULL,
country_code TEXT,
admin1 TEXT,
admin2 TEXT,
postal_code TEXT,
landmark TEXT,
tz_name TEXT,
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (latitude, longitude),
  UNIQUE (canonical_name, country_code, admin1, admin2, postal_code)
);
CREATE INDEX IF NOT EXISTS idx_locations_canon ON locations (canonical_name);
CREATE INDEX IF NOT EXISTS idx_locations_geo ON locations (latitude, longitude);

-- =========================================
-- requests — every user query (location + date range)
-- Max results window: 7 days (inclusive)
-- =========================================
CREATE TABLE IF NOT EXISTS requests (
id TEXT PRIMARY KEY,
user_id TEXT REFERENCES users (id) ON DELETE SET NULL,
location_id TEXT NOT NULL REFERENCES locations (id) ON DELETE CASCADE,
provider_id TEXT REFERENCES providers (id) ON DELETE SET NULL,
query_raw TEXT,
  start_date     DATE NOT NULL,
  end_date       DATE NOT NULL,
  granularity    TEXT NOT NULL CHECK (granularity IN ('current','hourly','daily')),
status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ok', 'error')),
  error_message  TEXT,
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
CHECK (
  julianday (end_date) - julianday (start_date) <= 7
)
);
CREATE INDEX IF NOT EXISTS idx_requests_loc_dates ON requests (location_id, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_requests_user ON requests (user_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests (status);

-- =========================================
-- weather_observations — point-in-time actuals (past/current)
-- =========================================
CREATE TABLE IF NOT EXISTS weather_observations (
id TEXT PRIMARY KEY,
location_id TEXT NOT NULL REFERENCES locations (id) ON DELETE CASCADE,
provider_id TEXT NOT NULL REFERENCES providers (id) ON DELETE CASCADE,
observed_at DATETIME NOT NULL,
temperature_c NUMERIC,
humidity_pct NUMERIC,
pressure_hpa NUMERIC,
wind_speed_ms NUMERIC,
wind_gust_ms NUMERIC,
wind_deg NUMERIC,
precip_mm NUMERIC,
snow_mm NUMERIC,
cloud_pct NUMERIC,
visibility_m NUMERIC,
uv_index NUMERIC,
weather_code TEXT,
payload_raw TEXT,
ingested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (location_id, provider_id, observed_at)
);
CREATE INDEX IF NOT EXISTS idx_obs_loc_time ON weather_observations (location_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_obs_provider_time ON weather_observations (provider_id, observed_at);

-- =========================================
-- weather_forecasts — snapshot of predictions
-- =========================================
CREATE TABLE IF NOT EXISTS weather_forecasts (
id TEXT PRIMARY KEY,
location_id TEXT NOT NULL REFERENCES locations (id) ON DELETE CASCADE,
provider_id TEXT NOT NULL REFERENCES providers (id) ON DELETE CASCADE,
kind TEXT NOT NULL CHECK (kind IN ('hourly', 'daily')),
snapshot_time DATETIME NOT NULL,
forecast_time DATETIME NOT NULL,
horizon_hours INTEGER,
temperature_c NUMERIC,
temp_min_c NUMERIC,
temp_max_c NUMERIC,
humidity_pct NUMERIC,
pressure_hpa NUMERIC,
wind_speed_ms NUMERIC,
wind_gust_ms NUMERIC,
wind_deg NUMERIC,
precip_mm NUMERIC,
snow_mm NUMERIC,
cloud_pct NUMERIC,
pop_pct NUMERIC,
  weather_code    TEXT,
payload_raw TEXT,
ingested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (location_id, provider_id, kind, snapshot_time, forecast_time)
);
CREATE INDEX IF NOT EXISTS idx_fc_loc_time ON weather_forecasts (location_id, forecast_time);
CREATE INDEX IF NOT EXISTS idx_fc_loc_kind_snap ON weather_forecasts (location_id, kind, snapshot_time);

-- =========================================
-- favorites (optional)
-- =========================================
CREATE TABLE IF NOT EXISTS favorites (
id TEXT PRIMARY KEY,
user_id TEXT REFERENCES users (id) ON DELETE SET NULL,
location_id TEXT NOT NULL REFERENCES locations (id) ON DELETE CASCADE,
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Helpful view
CREATE VIEW IF NOT EXISTS v_recent_requests AS
SELECT
  r.*,
  u.email AS user_email,
  l.canonical_name
FROM requests r
LEFT JOIN users u ON u.id = r.user_id
JOIN locations l ON l.id = r.location_id
ORDER BY r.created_at DESC;
