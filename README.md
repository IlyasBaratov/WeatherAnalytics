# Weather + Ski Analytics Dashboard

A FastAPI analytics app with a static HTML/CSS/JavaScript frontend for weather forecasts, ski resort conditions, local news videos, AI-generated weather briefs, and account-based saved favorites.

Production links:

- App: https://app-weather-analytics.azurewebsites.net
- Swagger docs: https://app-weather-analytics.azurewebsites.net/api/docs
- ReDoc: https://app-weather-analytics.azurewebsites.net/api/redoc

## Features

- Weather summaries from OpenWeather with current, hourly, and daily forecast data.
- Ski resort analytics from the RapidAPI ski resort forecast API.
- Gemini AI weather briefs with severity, headline, risks, changes, and simple actions.
- YouTube local news videos for searched cities.
- Email/password authentication with signed bearer tokens.
- User-scoped favorites and request history.
- SQLAlchemy persistence for users, locations, providers, requests, forecasts, observations, and favorites.
- Runtime frontend configuration through `/env.js`.
- Docker Compose setup for API, frontend, Postgres, and pgAdmin.

## Authentication

The app includes local account auth.

- Passwords are stored as PBKDF2-SHA256 hashes with per-password salts.
- API sessions use signed bearer tokens.
- Tokens expire after `AUTH_TOKEN_EXPIRE_MINUTES`.
- Favorites, saved requests, request updates, and forecast mutations require authentication.
- Public weather and ski lookup endpoints remain available without login.

Auth endpoints:

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

Register:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"you@example.com\",\"password\":\"change-me-123\",\"display_name\":\"You\"}"
```

Login:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"you@example.com\",\"password\":\"change-me-123\"}"
```

Use the returned token for protected routes:

```bash
curl "http://localhost:8000/api/weather/favorites" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## AI Weather Briefs

`GET /api/weather/summary` builds a weather context and, when a Gemini API key is configured, asks Gemini to produce a concise dashboard brief.

The returned `insight` object includes:

```json
{
  "severity": "low",
  "headline": "Mild today with light wind.",
  "risks": ["Low rain risk through the next few hours."],
  "changes": ["Temperatures ease after sunset."],
  "actions": ["A light jacket is enough for the evening."],
  "source": "gemini"
}
```

If Gemini is not configured or fails, the endpoint falls back to the rule-based summary and keeps weather data loading.

## Quick Start

### Prerequisites

- Python 3.10+
- OpenWeather API key
- Optional: Google Gemini API key for AI weather briefs
- Optional: YouTube Data API key for local news videos
- Optional: RapidAPI ski resort forecast key
- Optional: Docker and Docker Compose

### Local Python Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backEnd.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- UI: http://localhost:8000/
- API docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health

### Docker Compose Setup

```bash
docker compose up --build
```

Default compose ports:

- API: http://localhost:8000
- UI: http://localhost:3000
- pgAdmin: http://localhost:5050
- Postgres: localhost:5432

## Environment Variables

Create a `.env` file in the project root.

```env
APP_NAME=Weather Analytics
DEBUG=False
VERSION=1.0.0

API_WEATHER_KEY=your_openweather_key
API_YOUTUBE_KEY=your_youtube_key
API_GEMINI_AI_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
API_SKI_KEY=your_rapidapi_ski_key

AUTH_SECRET_KEY=replace-with-a-long-random-secret
AUTH_TOKEN_EXPIRE_MINUTES=1440

DEFAULT_LAT=47.6061
DEFAULT_LON=-122.3328
WEATHER_UNITS=metric
API_TIMEOUT=10.0

DATABASE_URL=sqlite:///./db/weather.db
```

For Docker Compose with Postgres:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_DB=weather_db
DATABASE_URL=postgresql+psycopg2://postgres:1234@db:5432/weather_db
```

Important production note: set `AUTH_SECRET_KEY` to a strong private value. If it is omitted, the app uses a development fallback.

## API Overview

Base URL:

- Local API root: `http://localhost:8000/api`
- Local weather base: `http://localhost:8000/api/weather`
- Local ski base: `http://localhost:8000/api/ski`

### Weather

```http
GET /api/weather/summary
```

Query parameters:

| Parameter | Type | Required | Notes |
| --- | --- | --- | --- |
| `q` | string | No | City or place name |
| `lat` | float | No | Latitude |
| `lon` | float | No | Longitude |
| `days` | int | No | 1-7, default 7 |
| `units` | string | No | `metric` or `imperial` |

Example:

```bash
curl "http://localhost:8000/api/weather/summary?q=Seattle&days=3&units=metric"
```

### Protected Weather Data

These routes require `Authorization: Bearer <token>`:

```http
POST   /api/weather/requests
GET    /api/weather/requests
GET    /api/weather/requests/{request_id}
PATCH  /api/weather/requests/{request_id}
DELETE /api/weather/requests/{request_id}

GET    /api/weather/favorites
POST   /api/weather/favorites
DELETE /api/weather/favorites/{favorite_id}

PATCH  /api/weather/forecasts/{forecast_id}
DELETE /api/weather/forecasts/{forecast_id}
```

Forecast listing is public:

```http
GET /api/weather/forecasts
```

### Ski

```http
GET /api/ski/geo?q=Jackson%20Hole
GET /api/ski/hourly?q=Jackson%20Hole
GET /api/ski/forecast?q=Jackson%20Hole
GET /api/ski/snow?q=Jackson%20Hole
GET /api/ski/full?q=Jackson%20Hole
GET /api/ski/resorts?region=USA-Colorado
```

## Data Model

- `users`: account profile and password hash.
- `providers`: upstream providers such as OpenWeather.
- `locations`: canonical places and coordinates.
- `requests`: user-scoped saved weather requests.
- `weather_forecasts`: stored forecast snapshots.
- `weather_observations`: historical or current observations.
- `favorites`: user-scoped saved locations.

The app creates tables on startup for local development. Startup also adds `users.password_hash` to older databases when needed.

## Project Structure

```text
WeatherProject/
  backEnd/
    api/routers/
      auth.py              # Register, login, current user
      weather.py           # Weather, favorites, requests, forecasts
      ski.py               # Ski resort endpoints
    core/
      auth.py              # Password hashing and bearer token helpers
      config.py            # Pydantic settings
      database.py          # SQLAlchemy engine/session
    models/model.py        # SQLAlchemy models
    services/
      gemini_service.py    # AI weather brief generation
      weather_service.py   # Weather context building
      youtube_service.py   # Local news videos
  frontEnd/
    html/index.html        # Main UI with auth widget and dashboard
    html/ski_index.html    # Ski dashboard
    css/styles.css         # App styling
    docker-entrypoint.d/   # Runtime env.js generation
  db/db_schema.sql         # Database schema
  docker-compose.yml
  README.md
```

## Testing And Verification

Compile backend modules:

```bash
python -m compileall backEnd
```

Smoke test auth:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"change-me-123\"}"
```

Smoke test weather:

```bash
curl "http://localhost:8000/api/weather/summary?q=Seattle"
```

## Roadmap

- [x] Weather summary dashboard
- [x] Ski resort analytics
- [x] SQLAlchemy persistence
- [x] YouTube local news integration
- [x] Gemini AI weather briefs
- [x] Local authentication
- [x] User-scoped favorites
- [x] Docker Compose setup
- [ ] Add Redis caching for API responses
- [ ] Add comprehensive pytest coverage
- [ ] Add weather alerts and notifications
- [ ] Add dashboard charts and comparisons

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

Ilyas Baratov - https://github.com/IlyasBaratov

## Acknowledgments

- FastAPI
- SQLAlchemy
- Pydantic
- OpenWeather
- Google Gemini
- YouTube Data API
- httpx

Last updated: May 2026
