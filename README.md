# 🌦 Weather Data Dashboard

A **FastAPI-based Weather Analytics Platform** integrated with the **OpenWeather API** to deliver real-time and forecast weather data with persistent storage, clean architecture, and a lightweight frontend.

**🌐 Live Demo:** [https://weatherdemo.online](https://weatherdemo.online)  
**🔌 API Base URL:** [https://api.weatherdemo.online](https://api.weatherdemo.online)

---

## 🎯 Project Overview

This is a **production-ready FastAPI application** that seamlessly integrates with the OpenWeather API to provide:

- 🌍 **Global weather data** and forecasts  
- 🌡 **Current, hourly, and daily conditions**  
- 💨 **Wind, humidity, and precipitation analytics**  
- 🗺 **Geocoding support** (city name → coordinates)  
- 💾 **Persistent database storage** with SQLAlchemy  
- 📅 **Date range forecasts** (up to 7 days)  
- ⚙️ **Environment-based configuration** using Pydantic v2  
- 🧱 **Clean modular architecture** (Routers / Services / Clients / Models)  
- 🌐 **CORS-enabled API** for frontend communication  
- ⚡ **Async HTTP calls** using `httpx`  
- 🪶 **Simple HTML/CSS/JS frontend** for quick visualization  

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

### 🏗 Technical Features
- ⚡ **Async/Await** – High-performance non-blocking I/O  
- 🔐 **Pydantic Settings v2** – Simple environment variable management  
- 💾 **SQLAlchemy ORM** – Database models for locations, forecasts, and requests  
- 📊 **Weather Analytics** – Store and query historical weather data  
- 🔁 **Clean Architecture** – Separation of concerns (API / Services / Core / Models)  
- 🌐 **CORS Middleware** – Frontend integration-ready  
- 🧩 **Type Safety** – Full typing and validation  
- 🎯 **Simplified API** – Date-only endpoints for easy integration  

---

## 🆕 New Features

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
  "date": "Friday, Nov 15, 2025",
  "current": {
    "temp": 12,
    "feels_like": 10,
    "humidity": 75,
    "wind": "5 km/h",
    "precip": "0 mm",
    "icon": "☁️"
  },
  "hourly": [...],
  "daily": [...]
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

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+  
- [OpenWeather API Key](https://openweathermap.org/api) (free tier available)
- SQLite (included) or PostgreSQL (optional)

---

### 🧩 Installation

#### 1️⃣ Clone the repository
```bash
git clone https://github.com/IlyasBaratov/WeatherProject.git
cd WeatherProject
```

#### 2️⃣ Create and activate virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
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

# Default Location (Seattle, WA)
DEFAULT_LAT=47.6061
DEFAULT_LON=-122.3328

# API Settings
API_TIMEOUT=10.0
WEATHER_UNITS=metric

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./weather.db
```

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

## 🏗️ Architecture

### Production Deployment
```
┌─────────────────────────┐
│  weatherdemo.online     │  ← Frontend (HTML/CSS/JS)
│  (Frontend App)         │
└───────────┬─────────────┘
            │
            │ API Calls
            ▼
┌─────────────────────────┐
│  api.weatherdemo.online │  ← Backend API (FastAPI)
│  (REST API)             │
└───────────┬─────────────┘
            │
            │ Fetches Data
            ▼
┌─────────────────────────┐
│  OpenWeather API        │  ← External Weather Service
└─────────────────────────┘
```

### Local Development
```
┌──────────────────┐     ┌──────────────────┐
│ localhost:3000   │────▶│ localhost:8000   │
│ (Frontend)       │     │ (Backend API)    │
└──────────────────┘     └──────────────────┘
```

---

## 📂 Project Structure

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
│   │   └── weather_service.py      # Weather service layer
│   ├── models/
│   │   └── model.py           # SQLAlchemy database models
│   ├── __init__.py
│   └── main.py                # FastAPI application entry point
├── frontEnd/
│   ├── html/
│   │   └── index.html         # Main web interface
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

#### 1️⃣ **Weather Summary** (Current Conditions)

```http
GET /api/weather/summary
```

**Description:**  
Fetch current weather summary with hourly and daily forecasts.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | ❌ Optional | City name (e.g., "Seattle", "London") |
| `lat` | float | ❌ Optional | Latitude |
| `lon` | float | ❌ Optional | Longitude |

**Example Requests:**
```bash
# City name
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# Coordinates
curl "https://api.weatherdemo.online/api/weather/summary?lat=47.6061&lon=-122.3328"

# Default location
curl "https://api.weatherdemo.online/api/weather/summary"
```

**Example Response:**
```json
{
  "place": "Seattle, WA, US",
  "date": "Friday, Nov 15, 2025",
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
    {"name": "Fri", "hi": 15, "lo": 10, "icon": "☁️"},
    {"name": "Sat", "hi": 14, "lo": 9, "icon": "🌧️"}
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

**Example Response:**
```json
{
  "success": true,
  "message": "Weather data fetched and stored for Seattle, WA, US",
  "location": {
    "place": "Seattle, WA, US",
    "latitude": 47.6061,
    "longitude": -122.3328
  },
  "date_range": {
    "start": "2025-11-15",
    "end": "2025-11-20",
    "days": 6
  },
  "storage": {
    "request_id": "abc-123-def",
    "location_id": "xyz-789",
    "provider": "OpenWeather",
    "forecasts_stored": 48,
    "timestamp": "2025-11-15T10:30:00"
  },
  "api_data": {
    "list": [...],
    "city": {...}
  }
}
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

**Example Request:**
```bash
curl "https://api.weatherdemo.online/api/weather/forecast/range/stored?start_date=2025-11-15&end_date=2025-11-20"
```

**Example Response:**
```json
{
  "success": true,
  "location": {
    "place": "Seattle, WA, US",
    "latitude": 47.6061,
    "longitude": -122.3328
  },
  "date_range": {
    "start": "2025-11-15",
    "end": "2025-11-20"
  },
  "count": 48,
  "forecasts": [
    {
      "id": "forecast-uuid",
      "forecast_time": "2025-11-15T12:00:00",
      "temperature_c": 12.5,
      "humidity_pct": 75.0,
      "wind_speed_ms": 5.2,
      "weather_code": "Clouds",
      ...
    }
  ]
}
```

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

**Example Requests:**
```bash
# By city name
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-20&q=London"

# By coordinates
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-20&lat=51.5074&lon=-0.1278"

# Preview without storing
curl "https://api.weatherdemo.online/api/weather/range?start_date=2025-11-15&end_date=2025-11-17&q=Tokyo&store_in_db=false"
```

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
| `DEFAULT_LAT` | Default latitude | 47.6061 | ✅ Yes |
| `DEFAULT_LON` | Default longitude | -122.3328 | ✅ Yes |
| `API_TIMEOUT` | API request timeout (seconds) | 10.0 | ❌ No |
| `WEATHER_UNITS` | Temperature units (metric/imperial) | metric | ❌ No |
| `DATABASE_URL` | Database connection string | sqlite:///./weather.db | ❌ No |

### Getting an API Key

1. Visit [OpenWeather](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add to your `.env` file

---

## 💾 Database

### Automatic Setup

The database is created automatically on first run:

```python
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
```

### Database Models

#### **Location**
```python
- id (UUID)
- canonical_name (string)
- latitude (float)
- longitude (float)
- country_code (string)
- timezone (string)
```

#### **WeatherForecast**
```python
- id (UUID)
- location_id (FK)
- forecast_time (datetime)
- temperature_c (decimal)
- humidity_pct (decimal)
- wind_speed_ms (decimal)
- weather_code (string)
- ... 15+ weather parameters
```

#### **Request**
```python
- id (UUID)
- location_id (FK)
- start_date (date)
- end_date (date)
- status (string)
- created_at (datetime)
```

---

## 🧪 Testing

### Using cURL
```bash
# Test weather summary
curl "https://api.weatherdemo.online/api/weather/summary?q=Seattle"

# Test date range (local)
curl "http://localhost:8000/api/weather/forecast/range?start_date=2025-11-15&end_date=2025-11-20"
```

### Using Python
```python
import requests

# Fetch weather
response = requests.get(
    "https://api.weatherdemo.online/api/weather/forecast/range",
    params={
        "start_date": "2025-11-15",
        "end_date": "2025-11-20"
    }
)
print(response.json())
```

### Interactive API Docs

Visit the auto-generated documentation:
- **Swagger UI:** https://api.weatherdemo.online/docs
- **ReDoc:** https://api.weatherdemo.online/redoc

---

## 🚀 Deployment

### Production Deployment (Current)

The app is deployed at **https://weatherdemo.online** using:
- **Server:** VPS/Cloud hosting
- **Web Server:** Nginx (reverse proxy)
- **ASGI Server:** Uvicorn
- **Database:** SQLite/PostgreSQL
- **SSL:** Let's Encrypt

### Deploy Your Own

#### Using Uvicorn (Production)
```bash
uvicorn backEnd.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Docker (Coming Soon)
```bash
docker-compose up -d
```

---

## 🛣️ Roadmap

- [x] ✅ Date range weather forecasts
- [x] ✅ Database storage with SQLAlchemy
- [x] ✅ Location favorites
- [x] ✅ Request tracking and history
- [x] ✅ Production deployment
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

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 API Response Examples

### Current Weather
```json
{
  "temp": 12,
  "feels_like": 10,
  "humidity": 75,
  "wind": "5 km/h",
  "icon": "☁️"
}
```

### Forecast Entry
```json
{
  "forecast_time": "2025-11-15T15:00:00",
  "temperature_c": 12.5,
  "temp_min_c": 11.0,
  "temp_max_c": 14.0,
  "humidity_pct": 75.0,
  "pressure_hpa": 1013.25,
  "wind_speed_ms": 5.2,
  "wind_deg": 180.0,
  "cloud_pct": 50.0,
  "pop_pct": 10.0,
  "weather_code": "Clouds"
}
```

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
- **httpx** - Async HTTP client
- All contributors and open source community

---

## 📞 Support

For questions, issues, or feature requests:
- 🐛 **Issues:** [GitHub Issues](https://github.com/IlyasBaratov/WeatherAnalytics/issues)
- 📧 **Email:** Contact through GitHub
- 🌐 **Frontend:** https://weatherdemo.online
- 🔌 **API:** https://api.weatherdemo.online

---

## 🎯 Quick Links

- 🌐 **Live Demo:** [https://weatherdemo.online](https://weatherdemo.online)
- 🔌 **API Base URL:** [https://api.weatherdemo.online](https://api.weatherdemo.online)
- 📚 **API Docs (Swagger):** [https://api.weatherdemo.online/docs](https://api.weatherdemo.online/docs)
- 📖 **API Docs (ReDoc):** [https://api.weatherdemo.online/redoc](https://api.weatherdemo.online/redoc)
- 🔗 **GitHub:** [https://github.com/IlyasBaratov/WeatherProject](https://github.com/IlyasBaratov/WeatherProject)
- 🌤️ **OpenWeather API:** [https://openweathermap.org/api](https://openweathermap.org/api)

---

**Made with ☀️ and 💻 by Ilyas Baratov**

*Last updated: November 2025*