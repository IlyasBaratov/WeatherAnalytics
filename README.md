# 🌦 Weather Data Dashboard

A **FastAPI-based Weather Analytics Platform** integrated with the **OpenWeather API** and **YouTube Data API** to deliver real-time weather data, forecasts, and local news videos with persistent storage, clean architecture, and a modern frontend.

**🌐 Live Demo:** [https://weatherdemo.online](https://weatherdemo.online)  
**📌 API Base URL:** [https://api.weatherdemo.online](https://api.weatherdemo.online)

---

## 🎯 Project Overview

This is a **production-ready FastAPI application** that seamlessly integrates with multiple APIs to provide:

- 🌍 **Global weather data** and forecasts  
- 🌡 **Current, hourly, and daily conditions**  
- 💨 **Wind, humidity, and precipitation analytics**  
- 🗺 **Geocoding support** (city name → coordinates)  
- 📺 **Local news videos** powered by YouTube Data API (**NEW!**)
- 💾 **Persistent database storage** with SQLAlchemy  
- 📅 **Date range forecasts** (up to 7 days)  
- ⚙️ **Environment-based configuration** using Pydantic v2  
- 🧱 **Clean modular architecture** (Routers / Services / Clients / Models)  
- 🌐 **CORS-enabled API** for frontend communication  
- ⚡ **Async HTTP calls** using `httpx`  
- 🪶 **Modern HTML/CSS/JS frontend** with smooth animations  

---

## ✨ Key Features

### 🌦 Weather Data Integration
- **Current Weather** – temperature, feels-like, humidity, wind  
- **5-Day Forecast** – 3-hour interval forecast (OpenWeather 5-day API)  
- **Hourly Forecast** – upcoming hours with temperature and icons  
- **Daily Forecast** – min/max temperature and weather status  
- **Date Range Queries** – fetch weather for specific date ranges (max 7 days)
- **Dynamic Weather Icons** – automatically selected from API  
- **Database Storage** – all forecasts persisted for historical analysis

### 📺 YouTube Integration (**NEW!**)
- **Local News Videos** – Automatically fetch relevant local news videos for any city
- **Smart Search** – Uses city name and country code for accurate results
- **Video Metadata** – Title, channel, thumbnail, publish date, and direct links
- **Graceful Fallback** – Weather data still works if YouTube API fails
- **Responsive Display** – Beautiful video cards with hover effects

### 🏗 Technical Features
- ⚡ **Async/Await** – High-performance non-blocking I/O  
- 🔐 **Pydantic Settings v2** – Simple environment variable management  
- 💾 **SQLAlchemy ORM** – Database models for locations, forecasts, and requests  
- 📊 **Weather Analytics** – Store and query historical weather data  
- 🔨 **Clean Architecture** – Separation of concerns (API / Services / Core / Models)  
- 🌐 **CORS Middleware** – Frontend integration-ready  
- 🧩 **Type Safety** – Full typing and validation  
- 🎯 **Simplified API** – Date-only endpoints for easy integration  

---

## 🆕 New Features

### 📺 YouTube Local News Integration

The weather summary endpoint now automatically fetches local news videos relevant to the searched location.

**Features:**
- Automatic video search based on city name
- Region-specific results using country codes
- Up to 4 latest local news videos per request
- Complete video metadata (title, channel, thumbnail, date, URL)
- Non-blocking: Weather data always loads even if YouTube fails

**API Response Example:**
```json
{
  "place": "Seattle, WA, US",
  "current": [ "..."  ],
  "hourly": [ "..." ],
  "daily": [ "..." ],
  "videos": [
    {
      "video_id": "abc123",
      "title": "Seattle Weather Update - November 2025",
      "channel_title": "KING 5 News",
      "published_at": "2025-11-18T10:30:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123/mqdefault.jpg",
      "url": "https://www.youtube.com/watch?v=abc123"
    }
  ]
}
```

### 📅 Date Range Weather Endpoints

#### **Simple API** (Recommended)
Fetch weather data with just start and end dates - no location parameters needed!

```bash
GET /api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20
```

#### **Advanced API**
Fetch weather for any location with flexible parameters:

```bash
GET /api/weather/range?start_date=2025-11-15&end_date=2025-11-20&q=London
```

### 💾 Database Features
- **Automatic storage** of all weather forecasts
- **Location tracking** with geocoding
- **Request history** for analytics
- **Weather observations** for historical data
- **User favorites** for quick access

---

## 📊 Data Management

### Weather Context JSON Structure
```json
{
  "place": "Seattle, WA, US",
  "date": "Friday, Nov 18, 2025",
  "current": {
    "temp": 12,
    "feels_like": 10,
    "humidity": 75,
    "wind": "5 km/h",
    "precip": "0 mm",
    "icon": "☁️"
  },
  "hourly": ["..."],
  "daily": ["..."],
  "videos": ["..."]
}
```

### Database Schema
- **`users`** - User accounts and profiles
- **`providers`** - Weather data providers (OpenWeather, etc.)
- **`locations`** - Geocoded locations with coordinates
- **`requests`** - API request tracking
- **`weather_forecasts`** - Hourly/daily forecast data
- **`weather_observations`** - Historical observations
- **`favorites`** - User favorite locations

### APIs Used
- `https://api.openweathermap.org/data/2.5/forecast` - Weather forecasts
- `https://api.openweathermap.org/geo/1.0/direct` - Forward geocoding
- `https://api.openweathermap.org/geo/1.0/reverse` - Reverse geocoding
- `https://www.googleapis.com/youtube/v3/search` - YouTube video search (**NEW!**)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+  
- [OpenWeather API Key](https://openweathermap.org/api) (free tier available)
- [YouTube Data API Key](https://console.cloud.google.com/apis/api/youtube.googleapis.com) (free tier available) (**NEW!**)
- SQLite (included) or PostgreSQL (optional)

---

### 🧩 Installation

#### 1️⃣ Clone the repository
```bash
git clone https://github.com/IlyasBaratov/WeatherAnalytics.git
cd WeatherProject
```

#### 2️⃣ Create and activate virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
pip install requests

# macOS/Linux
source .venv/bin/activate
pip install requests
```

#### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure environment variables
Create a `.env` file in the root directory:
```env
# OpenWeather API
API_WEATHER_KEY=your_openweather_api_key_here

# YouTube Data API (NEW!)
API_YOUTUBE_KEY=your_youtube_api_key_here

# Default Location (Seattle, WA)
DEFAULT_LAT=47.6061
DEFAULT_LON=-122.3328

# API Settings
API_TIMEOUT=10.0
WEATHER_UNITS=metric

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./weather.db
```

#### 🔑 Getting API Keys

**OpenWeather API:**
1. Visit [OpenWeather](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add to your `.env` file as `API_WEATHER_KEY`

**YouTube Data API (NEW!):**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Create credentials (API Key)
5. Add to your `.env` file as `API_YOUTUBE_KEY`

#### 5️⃣ Run the application

##### Option A: Backend + Frontend Separately

**Terminal 1 - Backend:**
```bash
uvicorn backEnd.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontEnd
python -m http.server 3000
```

##### Option B: Production Mode
```bash
uvicorn backEnd.main:app --host 0.0.0.0 --port 8000
```

#### 6️⃣ Access the App
- **Frontend:** http://localhost:3000/html/index.html
- **API Docs:** http://localhost:8000/docs
- **Live Demo:** https://weatherdemo.online
- **Live API:** https://api.weatherdemo.online

---

## 🗂️ Project Structure

```
WeatherProject/
├── backEnd/
│   ├── core/
│   │   ├── config.py          # Settings and environment variables
│   │   └── database.py        # Database connection and session
│   ├── api/
│   │   └── routers/
│   │       ├── pages.py       # HTML template rendering
│   │       └── weather.py     # Weather API endpoints
│   ├── services/
│   │   ├── api_forecast_client.py  # OpenWeather API client
│   │   ├── geo_client.py           # Geocoding API client
│   │   ├── geo_service.py          # Geocoding service layer
│   │   ├── weather_service.py      # Weather service layer
│   │   ├── youtube_client.py       # YouTube API client (NEW!)
│   │   └── youtube_service.py      # YouTube service layer (NEW!)
│   ├── models/
│   │   └── model.py           # SQLAlchemy database models
│   ├── __init__.py
│   └── main.py                # FastAPI application entry point
├── frontEnd/
│   ├── html/
│   │   └── index.html         # Main web interface (updated with video display)
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend JavaScript
├── .env                        # Environment configuration (not in repo)
├── requirements.txt            # Python dependencies
├── weather.db                  # SQLite database (auto-created)
└── README.md                   # Project documentation
```

---

## 🌐 API Documentation

**Base URL (Production):** `https://api.weatherdemo.online/api/weather`  
**Base URL (Local):** `http://localhost:8000/api/weather`

---

### 📡 Endpoints

#### 1️⃣ **Weather Summary** (Current Conditions + Videos)

```http
GET /api/weather/summary
```

**Description:**  
Fetch current weather summary with hourly and daily forecasts, plus local news videos.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | ❌ Optional | City name (e.g., "Seattle", "London") |
| `lat` | float | ❌ Optional | Latitude |
| `lon` | float | ❌ Optional | Longitude |
| `days` | int | ❌ Optional | Number of forecast days (1-7, default: 7) |

**Example Requests:**
```bash
# City name
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# City with custom days
curl "https://api.weatherdemo.online/api/weather/summary?q=London&days=5"

# Coordinates
curl "https://api.weatherdemo.online/api/weather/summary?lat=47.6061&lon=-122.3328"

# Default location
curl "https://api.weatherdemo.online/api/weather/summary"
```

**Example Response:**
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
      "video_id": "dQw4w9WgXcQ",
      "title": "Seattle Weather Update - Heavy Rain Expected",
      "channel_title": "KING 5 News",
      "published_at": "2025-11-18T08:30:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
```

---

#### 2️⃣ **Weather Forecast Range** (Simplified - NEW! ⭐)

```http
GET /api/weather/forecast/range
```

**Description:**  
Fetch and store weather forecasts for a date range using default location.  
**Only requires start_date and end_date!**

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date | ✅ Yes | Start date (YYYY-MM-DD) |
| `end_date` | date | ✅ Yes | End date (YYYY-MM-DD, max 7 days from start) |

**Example Requests:**
```bash
# Fetch 5 days of weather
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"

# Fetch full week
curl "https://api.weatherdemo.online/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-22"
```

---

#### 3️⃣ **Get Stored Forecasts**

```http
GET /api/weather/forecast/range/stored
```

**Description:**  
Retrieve previously stored weather forecasts from database.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date | ✅ Yes | Start date (YYYY-MM-DD) |
| `end_date` | date | ✅ Yes | End date (YYYY-MM-DD) |

---

#### 4️⃣ **Advanced Weather Range** (Multi-Location)

```http
GET /api/weather/range
```

**Description:**  
Fetch weather for any location with custom parameters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date | ✅ Yes | Start date (YYYY-MM-DD) |
| `end_date` | date | ✅ Yes | End date (max 7 days from start) |
| `q` | string | ❌ Optional | City name |
| `lat` | float | ❌ Optional | Latitude |
| `lon` | float | ❌ Optional | Longitude |
| `store_in_db` | boolean | ❌ Optional | Store data (default: true) |

---

### 🗄️ Database Endpoints

#### 5️⃣ **List All Requests**
```http
GET /api/weather/requests
```

#### 6️⃣ **Get Request Details**
```http
GET /api/weather/requests/{request_id}
```

#### 7️⃣ **List All Forecasts**
```http
GET /api/weather/forecasts?location_id=xyz&start_date=2025-11-15&end_date=2025-11-20
```

#### 8️⃣ **Manage Favorites**
```http
GET /api/weather/favorites
POST /api/weather/favorites
DELETE /api/weather/favorites/{favorite_id}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_WEATHER_KEY` | OpenWeather API key | - | ✅ Yes |
| `API_YOUTUBE_KEY` | YouTube Data API key | - | ✅ Yes |
| `DEFAULT_LAT` | Default latitude | 47.6061 | ✅ Yes |
| `DEFAULT_LON` | Default longitude | -122.3328 | ✅ Yes |
| `API_TIMEOUT` | API request timeout (seconds) | 10.0 | ❌ No |
| `WEATHER_UNITS` | Temperature units (metric/imperial) | metric | ❌ No |
| `DATABASE_URL` | Database connection string | sqlite:///./weather.db | ❌ No |

---

## 🧪 Testing

### Using cURL
```bash
# Test weather summary with videos
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# Test date range (local)
curl "http://localhost:8000/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Using Python
```python
import requests

# Fetch weather with videos
response = requests.get(
    "https://api.weatherdemo.online/api/weather/summary",
    params={"q": "Seattle"}
)
data = response.json()

print(f"Temperature: {data['current']['temp']}°C")
print(f"Videos found: {len(data.get('videos', []))}")

for video in data.get('videos', []):
    print(f"- {video['title']} by {video['channel_title']}")
```

### Interactive API Docs

Visit the auto-generated documentation:
- **Swagger UI:** https://api.weatherdemo.online/docs
- **ReDoc:** https://api.weatherdemo.online/redoc

---

## 🛣️ Roadmap

- [x] ✅ Date range weather forecasts
- [x] ✅ Database storage with SQLAlchemy
- [x] ✅ Location favorites
- [x] ✅ Request tracking and history
- [x] ✅ Production deployment
- [x] ✅ YouTube local news integration
- [x] ✅ Modern animated frontend
- [ ] Add One Call 3.0 API integration for historical data
- [ ] Add Dockerfile & docker-compose setup
- [ ] Add metric/imperial toggle on frontend
- [ ] Add Redis caching for API responses
- [ ] Add comprehensive unit tests (pytest)
- [ ] Add weather alerts and notifications
- [ ] Add user authentication
- [ ] Add data visualization charts
- [ ] Add weather comparison between locations
- [ ] Add mobile app (React Native)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

**Ilyas Baratov** - [GitHub](https://github.com/IlyasBaratov)

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **OpenWeather** - Weather data provider
- **YouTube Data API** - Video content integration
- **httpx** - Async HTTP client
- All contributors and open source community

---

## 📞 Support

For questions, issues, or feature requests:
- 🐛 **Issues:** [GitHub Issues](https://github.com/IlyasBaratov/WeatherAnalytics/issues)
- 📧 **Email:** Contact through GitHub
- 🌐 **Frontend:** https://weatherdemo.online
- 📌 **API:** https://api.weatherdemo.online

---

## 🎯 Quick Links

- 🌐 **Live Demo:** [https://weatherdemo.online](https://weatherdemo.online)
- 📌 **API Base URL:** [https://api.weatherdemo.online](https://api.weatherdemo.online)
- 📚 **API Docs (Swagger):** [https://api.weatherdemo.online/docs](https://api.weatherdemo.online/docs)
- 📖 **API Docs (ReDoc):** [https://api.weatherdemo.online/redoc](https://api.weatherdemo.online/redoc)
- 🔗 **GitHub:** [https://github.com/IlyasBaratov/WeatherAnalytics](https://github.com/IlyasBaratov/WeatherAnalytics)
- 🌤️ **OpenWeather API:** [https://openweathermap.org/api](https://openweathermap.org/api)
- 📺 **YouTube Data API:** [https://developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)

---

**Made with ☀️ and 💻 by Ilyas Baratov**

*Last updated: November 2025*