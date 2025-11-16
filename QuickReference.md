# 🔗 Weather Dashboard - Quick Reference

## 🌐 Live URLs

### Production Environment

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | https://weatherdemo.online | Main web interface |
| **API Base** | https://api.weatherdemo.online | Backend API endpoints |
| **API Docs (Swagger)** | https://api.weatherdemo.online/docs | Interactive API documentation |
| **API Docs (ReDoc)** | https://api.weatherdemo.online/redoc | Alternative API documentation |

---

## 📡 API Endpoints Quick Reference

### Base URL
```
https://api.weatherdemo.online/api/weather
```

### Main Endpoints

#### 1. Current Weather Summary
```bash
GET https://api.weatherdemo.online/api/weather/summary?q=Seattle
```

#### 2. Fetch Weather for Date Range (Simplified)
```bash
GET https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20
```

#### 3. Get Stored Forecasts
```bash
GET https://api.weatherdemo.online/api/weather/forecast/range/stored?start_date=2025-11-15&end_date=2025-11-20
```

#### 4. Advanced Weather Range (Multi-Location)
```bash
GET https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-20&q=London
```

---

## 🧪 Quick Test Commands

### Test Current Weather
```bash
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"
```

### Test Date Range Forecast
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Test with Python
```python
import requests

response = requests.get(
    "https://api.weatherdemo.online/api/weather/forecast/range",
    params={
        "start_date": "2025-11-15",
        "end_date": "2025-11-20"
    }
)
print(response.json())
```

### Test with JavaScript
```javascript
fetch('https://api.weatherdemo.online/api/weather/summary?q=Seattle')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🏗️ Architecture Overview

```
User Browser
     │
     ├─── Frontend: https://weatherdemo.online
     │    (HTML/CSS/JS Interface)
     │
     └─── Backend API: https://api.weatherdemo.online
          (FastAPI REST API)
               │
               └─── OpenWeather API
                    (External Weather Data)
```

---

## 📊 Full Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather/summary` | Current weather summary |
| GET | `/api/weather/forecast/range` | Fetch & store date range |
| GET | `/api/weather/forecast/range/stored` | Get stored forecasts |
| GET | `/api/weather/range` | Advanced date range (any location) |
| GET | `/api/weather/requests` | List all requests |
| GET | `/api/weather/requests/{id}` | Get request details |
| GET | `/api/weather/forecasts` | List forecasts with filters |
| GET | `/api/weather/favorites` | List favorite locations |
| POST | `/api/weather/favorites` | Add favorite location |
| DELETE | `/api/weather/favorites/{id}` | Remove favorite |

---

## 🔑 Common Query Parameters

### Location Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `q` | string | `Seattle` | City name or address |
| `lat` | float | `47.6061` | Latitude |
| `lon` | float | `-122.3328` | Longitude |

### Date Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `start_date` | date | `2025-11-15` | Start date (YYYY-MM-DD) |
| `end_date` | date | `2025-11-20` | End date (max 7 days from start) |

### Optional Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `store_in_db` | boolean | `true` | Store data in database |
| `granularity` | string | `hourly` | hourly or daily |

---

## 💡 Usage Examples

### Example 1: Get Current Weather
```bash
# For Seattle
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# For London
curl "https://api.weatherdemo.online/api/weather/summary?q=London"

# By coordinates (Tokyo)
curl "https://api.weatherdemo.online/api/weather/summary?lat=35.6762&lon=139.6503"
```

### Example 2: Get 5-Day Forecast
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Example 3: Get Week Forecast for Multiple Cities
```bash
# New York
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-22&q=New York"

# Paris
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-22&q=Paris"

# Tokyo
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-22&q=Tokyo"
```

### Example 4: Retrieve Stored Data
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range/stored?start_date=2025-11-15&end_date=2025-11-20"
```

---

## 🚦 HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Data retrieved successfully |
| 400 | Bad Request | Invalid date range |
| 404 | Not Found | Location or resource not found |
| 502 | Bad Gateway | OpenWeather API error |
| 504 | Gateway Timeout | API timeout |

---

## 📦 Response Format Examples

### Weather Summary Response
```json
{
  "place": "Seattle, WA, US",
  "date": "Friday, Nov 15, 2025",
  "current": {
    "temp": 12,
    "feels_like": 10,
    "humidity": 75,
    "wind": "5 km/h",
    "icon": "☁️"
  },
  "hourly": [...],
  "daily": [...]
}
```

### Date Range Response
```json
{
  "success": true,
  "message": "Weather data fetched and stored",
  "location": {
    "place": "Seattle, WA, US",
    "latitude": 47.6061,
    "longitude": -122.3328
  },
  "storage": {
    "forecasts_stored": 48,
    "request_id": "abc-123"
  }
}
```

---

## 🔐 Environment Setup

For local development, create `.env`:

```env
API_WEATHER_KEY=your_openweather_api_key
DEFAULT_LAT=47.6061
DEFAULT_LON=-122.3328
API_TIMEOUT=10.0
WEATHER_UNITS=metric
```

---

## 📱 Frontend Integration

### Fetch Weather in JavaScript
```javascript
async function getWeather(city) {
  const response = await fetch(
    `https://api.weatherdemo.online/api/weather/summary?q=${city}`
  );
  const data = await response.json();
  return data;
}

// Usage
getWeather('Seattle').then(weather => {
  console.log(`Temperature: ${weather.current.temp}°C`);
});
```

### React Example
```jsx
import { useState, useEffect } from 'react';

function WeatherWidget({ city = 'Seattle' }) {
  const [weather, setWeather] = useState(null);
  
  useEffect(() => {
    fetch(`https://api.weatherdemo.online/api/weather/summary?q=${city}`)
      .then(res => res.json())
      .then(data => setWeather(data));
  }, [city]);
  
  return (
    <div>
      {weather && (
        <>
          <h2>{weather.place}</h2>
          <p>Temperature: {weather.current.temp}°C</p>
        </>
      )}
    </div>
  );
}
```

---

## 🎯 Quick Start Checklist

- [ ] Visit https://weatherdemo.online
- [ ] Test API at https://api.weatherdemo.online/docs
- [ ] Try a simple request: `curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"`
- [ ] Fetch date range: `curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"`
- [ ] Check stored data endpoint
- [ ] Integrate into your application

---

## 🆘 Common Issues

### CORS Error
If you get CORS errors, ensure your frontend is accessing:
- `https://api.weatherdemo.online` (not `https://weatherdemo.online`)

### 404 Not Found
Make sure you're using the full path:
- ✅ `https://api.weatherdemo.online/api/weather/summary`
- ❌ `https://api.weatherdemo.online/summary`

### Date Range Error
Date range cannot exceed 7 days:
- ✅ `start_date=2025-11-15&end_date=2025-11-22` (7 days)
- ❌ `start_date=2025-11-15&end_date=2025-11-30` (15 days)

---

## 📚 Additional Resources

- **Full Documentation:** See README_UPDATED.md
- **GitHub Repository:** https://github.com/IlyasBaratov/WeatherAnalytics
- **OpenWeather Docs:** https://openweathermap.org/api

---

**Last Updated:** November 2025

Made with ☀️ by Ilyas Baratov