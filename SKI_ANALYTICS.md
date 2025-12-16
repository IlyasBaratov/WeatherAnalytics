# 🏔️ Ski Resort Analytics (Website Module)

This module powers the **Ski Resort Forecast** page (`ski_index.html`). It pulls data from the RapidAPI provider **ski-resort-forecast** and renders:

- **Current snow conditions** (depths, fresh snow, last snowfall date)
- **Hourly forecast** (summary, wind, snow/rain, temperature)
- **Multi-day forecast** (AM / PM / Night blocks)
- **Resort directory by region** (optional helper for UI/autocomplete)

---

## Frontend

### Page
- `ski_index.html`

### Backend base URL
In `ski_index.html`, the API base is:

```js
const API_BASE_URL = "http://localhost:8000/api/ski";
```

Change this to your deployed API host when running in production (for example `https://api.weatherdemo.online/api/ski`).

---

## API Endpoints

All endpoints are under `/api/ski`.

### 1) Full resort package (recommended)
Returns **geo (best-effort) + hourly + multi-day forecast + snow conditions**.

```http
GET /api/ski/full?q=Stevens%20Pass&units=i&elevation=top
```

Query params:
- `q` (required): resort name
- `units` (optional): typically `i` (imperial) or `m` (metric)
- `elevation` (optional): `top`, `mid`, `base`

### 2) Hourly only
```http
GET /api/ski/hourly?q=Stevens%20Pass&units=i&elevation=top
```

### 3) Daily forecast only
```http
GET /api/ski/forecast?q=Stevens%20Pass&units=i&elevation=top
```

### 4) Snow conditions only
```http
GET /api/ski/snow?q=Stevens%20Pass&units=i
```

### 5) Resorts by region
```http
GET /api/ski/resorts?region=USA-Washington
```

> Region codes are defined by the upstream provider (examples: `USA-Colorado`, `USA-Utah`, `USA-Washington`).

---

## Response shape (what the frontend expects)

`ski_index.html` is built to consume `/api/ski/full` and expects nested objects that look like:

- `hourly.basicInfo` (name, region, elevations, url)
- `hourly.forecast[]` (time, summary, windSpeed, windDirection, snow, rain, maxTemp, windChill, humidity, freezeLevel)
- `snow.*` (topSnowDepth, botSnowDepth, freshSnowfall, lastSnowfallDate)
- `forecast.forecast5Day[]` with `am`, `pm`, `night` blocks
- `forecast.summary3Day` and `forecast.summaryDays4To6`

If the upstream provider changes field names, adjust the mapping in `ski_index.html`’s `render()` function.

---

## Reliability & common errors

### 502 “invalid JSON / non-JSON response”
The upstream ski provider occasionally returns an HTML error page instead of JSON (rate limiting, maintenance, transient failures). The backend client detects this and returns a **502** with a short preview.

What to do:
- Retry after a short delay
- Confirm your `API_SKI_KEY` is valid and not rate limited
- Check the resort spelling (some resorts are very strict)

### Slow responses
The request time mostly depends on upstream latency. If you want better UX:
- Add a cached “last good result” per resort (server-side)
- Frontend: show skeleton UI while loading
- Prefer `/api/ski/full` (one request) vs calling multiple endpoints

---

## Quick manual test

Open Swagger UI:
- `http://127.0.0.1:8000/docs`

Then try:
- `/api/ski/full?q=Jackson%20Hole&units=i&elevation=top`
- `/api/ski/resorts?region=USA-Washington`

