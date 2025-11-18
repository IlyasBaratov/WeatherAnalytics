# 📗 Weather Dashboard - Quick Reference

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

#### 1. Current Weather Summary + Local News Videos ⭐ NEW!
```bash
GET https://api.weatherdemo.online/api/weather/summary?q=Seattle
```

**Response includes:**
- Current weather conditions
- Hourly forecast (next 6 hours)
- Daily forecast (up to 7 days)
- **Local news videos** from YouTube (up to 4 videos)

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

### Test Current Weather with Videos
```bash
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"
```

### Test Different Cities
```bash
# New York with videos
curl "https://api.weatherdemo.online/api/weather/summary?q=New York"

# London with 5-day forecast
curl "https://api.weatherdemo.online/api/weather/summary?q=London&days=5"

# Tokyo
curl "https://api.weatherdemo.online/api/weather/summary?q=Tokyo"
```

### Test Date Range Forecast
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Test with Python
```python
import requests

# Get weather with videos
response = requests.get(
    "https://api.weatherdemo.online/api/weather/summary",
    params={"q": "Seattle"}
)
data = response.json()

# Display results
print(f"Location: {data['place']}")
print(f"Temperature: {data['current']['temp']}°C")
print(f"\nLocal News Videos:")
for video in data.get('videos', []):
    print(f"- {video['title']}")
    print(f"  Channel: {video['channel_title']}")
    print(f"  URL: {video['url']}\n")
```

### Test with JavaScript
```javascript
// Fetch weather with videos
fetch('https://api.weatherdemo.online/api/weather/summary?q=Seattle')
  .then(response => response.json())
  .then(data => {
    console.log(`Temperature: ${data.current.temp}°C`);
    console.log(`Videos found: ${data.videos?.length || 0}`);
    
    data.videos?.forEach(video => {
      console.log(`- ${video.title} by ${video.channel_title}`);
    });
  });
```

---

## 🗂️ Architecture Overview

```
User Browser
     │
     ├─── Frontend: https://weatherdemo.online
     │    (HTML/CSS/JS Interface with Video Display)
     │
     └─── Backend API: https://api.weatherdemo.online
          (FastAPI REST API)
               │
               ├─── OpenWeather API
               │    (Weather Data)
               │
               └─── YouTube Data API ⭐ NEW!
                    (Local News Videos)
```

---

## 📊 Full Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather/summary` | Current weather + videos ⭐ |
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
| `days` | int | `7` | Number of forecast days (1-7) |
| `store_in_db` | boolean | `true` | Store data in database |
| `granularity` | string | `hourly` | hourly or daily |

---

## 💡 Usage Examples

### Example 1: Get Weather with Local News
```bash
# Seattle with news videos
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# London with news videos
curl "https://api.weatherdemo.online/api/weather/summary?q=London"

# New York with 3-day forecast
curl "https://api.weatherdemo.online/api/weather/summary?q=New York&days=3"
```

### Example 2: Get 5-Day Forecast
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Example 3: Get Week Forecast for Multiple Cities
```bash
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
| 502 | Bad Gateway | OpenWeather/YouTube API error |
| 504 | Gateway Timeout | API timeout |

---

## 📦 Response Format Examples

### Weather Summary with Videos Response ⭐
```json
{
  "place": "Seattle, WA, US",
  "date": "Tuesday, Nov 18, 2025",
  "current": {
    "temp": 12,
    "feels_like": 10,
    "humidity": 75,
    "wind": "5 km/h",
    "precip": "0 mm",
    "icon": "☁️"
  },
  "hourly": [
    {"time": "12 PM", "icon": "☁️", "temp": 12},
    {"time": "3 PM", "icon": "🌧️", "temp": 11}
  ],
  "daily": [
    {"name": "Tue", "hi": 15, "lo": 10, "icon": "☁️"},
    {"name": "Wed", "hi": 14, "lo": 9, "icon": "🌧️"}
  ],
  "videos": [
    {
      "video_id": "abc123xyz",
      "title": "Seattle Weather: Rain Expected This Week",
      "channel_title": "KING 5 News",
      "published_at": "2025-11-18T08:30:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123xyz/mqdefault.jpg",
      "url": "https://www.youtube.com/watch?v=abc123xyz"
    },
    {
      "video_id": "def456uvw",
      "title": "Local Weather Update - November 18",
      "channel_title": "KOMO 4 News",
      "published_at": "2025-11-18T07:00:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/def456uvw/mqdefault.jpg",
      "url": "https://www.youtube.com/watch?v=def456uvw"
    }
  ]
}
```

### Video Object Structure
```json
{
  "video_id": "string",
  "title": "string",
  "channel_title": "string",
  "published_at": "ISO 8601 datetime",
  "thumbnail_url": "string (URL)",
  "url": "string (YouTube watch URL)"
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

## 📝 Environment Setup

For local development, create `.env`:

```env
# Weather API
API_WEATHER_KEY=your_openweather_api_key

# YouTube API (NEW!)
API_YOUTUBE_KEY=your_youtube_api_key

# Default Location
DEFAULT_LAT=47.6061
DEFAULT_LON=-122.3328

# Settings
API_TIMEOUT=10.0
WEATHER_UNITS=metric
```

---

## 📱 Frontend Integration

### Fetch Weather with Videos in JavaScript
```javascript
async function getWeatherWithVideos(city) {
  const response = await fetch(
    `https://api.weatherdemo.online/api/weather/summary?q=${city}`
  );
  const data = await response.json();
  return data;
}

// Usage
getWeatherWithVideos('Seattle').then(weather => {
  console.log(`Temperature: ${weather.current.temp}°C`);
  console.log(`Videos: ${weather.videos?.length || 0}`);
  
  weather.videos?.forEach(video => {
    console.log(`- ${video.title} (${video.channel_title})`);
  });
});
```

### React Example with Videos
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
          
          <h3>Local News</h3>
          <ul>
            {weather.videos?.map(video => (
              <li key={video.video_id}>
                <a href={video.url} target="_blank" rel="noopener">
                  {video.title}
                </a>
                <p>by {video.channel_title}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
```

### Display Video Thumbnails
```javascript
function renderVideoCard(video) {
  return `
    <div class="video-card">
      <img src="${video.thumbnail_url}" alt="${video.title}">
      <h4>${video.title}</h4>
      <p>${video.channel_title}</p>
      <a href="${video.url}" target="_blank">Watch on YouTube</a>
    </div>
  `;
}

// Usage
const videosList = document.getElementById('videos');
data.videos?.forEach(video => {
  videosList.innerHTML += renderVideoCard(video);
});
```

---

## 🎯 Quick Start Checklist

- [ ] Visit https://weatherdemo.online
- [ ] Test API at https://api.weatherdemo.online/docs
- [ ] Try weather summary: `curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"`
- [ ] Check video integration in response
- [ ] Test date range: `curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"`
- [ ] Explore different cities
- [ ] Integrate into your application

---

## 🆘 Common Issues

### CORS Error
If you get CORS errors, ensure your frontend is accessing:
- ✅ `https://api.weatherdemo.online` (not `https://weatherdemo.online`)

### 404 Not Found
Make sure you're using the full path:
- ✅ `https://api.weatherdemo.online/api/weather/summary`
- ❌ `https://api.weatherdemo.online/summary`

### No Videos Returned
Videos array may be empty if:
- YouTube API quota exceeded
- No relevant videos found for location
- YouTube API key not configured
- API temporarily unavailable

**Note:** Weather data will still load even if videos fail!

### Date Range Error
Date range cannot exceed 7 days:
- ✅ `start_date=2025-11-15&end_date=2025-11-22` (7 days)
- ❌ `start_date=2025-11-15&end_date=2025-11-30` (15 days)

---

## 🔧 API Keys Required

### OpenWeather API
- **Free Tier:** 1,000 calls/day
- **Get Key:** https://openweathermap.org/api
- **Add to .env:** `API_WEATHER_KEY=your_key`

### YouTube Data API ⭐
- **Free Tier:** 10,000 units/day (100 video searches)
- **Get Key:** https://console.cloud.google.com/apis/api/youtube.googleapis.com
- **Add to .env:** `API_YOUTUBE_KEY=your_key`

---

## 📚 Additional Resources

- **Full Documentation:** See README.md
- **GitHub Repository:** https://github.com/IlyasBaratov/WeatherAnalytics
- **OpenWeather Docs:** https://openweathermap.org/api
- **YouTube API Docs:** https://developers.google.com/youtube/v3

---

## 🎨 New Features Summary

### ✅ YouTube Integration
- Automatic local news video search
- Smart region-based filtering
- Video metadata (title, channel, thumbnail, date)
- Direct YouTube links
- Graceful fallback if API fails

### ✅ Enhanced Frontend
- Beautiful video card display
- Smooth animations and hover effects
- Responsive video thumbnails
- "Watch on YouTube" buttons
- Mobile-friendly design

### ✅ Robust Error Handling
- Weather always loads even if videos fail
- Proper error logging
- User-friendly empty states
- No breaking changes to existing API

---

**Last Updated:** November 18, 2025

Made with ☀️ and 📺 by Ilyas Baratov