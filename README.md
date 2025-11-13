# 🌦 Weather Data Dashboard

A **FastAPI-based Weather Analytics Backend** integrated with the **OpenWeather API** to deliver real-time and forecast weather data with clean architecture and a lightweight frontend.

---

## 🎯 Project Overview

This is a **production-ready FastAPI application** that integrates seamlessly with the OpenWeather API to provide:

- 🌍 **Global weather data** and forecasts  
- 🌡 **Current, hourly, and daily conditions**  
- 💨 **Wind, humidity, and precipitation analytics**  
- 🗺 **Geocoding support** (city name → coordinates)  
- ⚙️ **Environment-based configuration** using Pydantic v2  
- 🧱 **Clean modular architecture** (Routers / Services / Clients)  
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
- **Dynamic Weather Icons** – automatically selected from API  

### 🏗 Technical Features
- ⚡ **Async/Await** – High-performance non-blocking I/O  
- 🔐 **Pydantic Settings v2** – Simple environment variable management  
- 💾 **Default fallback coordinates** from `.env`  
- 🔁 **Clean Architecture** – Separation of concerns (API / Services / Core)  
- 🌐 **CORS Middleware** – Frontend integration-ready  
- 🧩 **Type Safety** – Full typing and validation  

---

## 📊 Data Management

- **Weather Context JSON Structure**
  - `place` – City, region, and country name  
  - `date` – Current date  
  - `current` – Current temperature, humidity, wind speed, icon  
  - `hourly` – Hourly temperature forecast  
  - `daily` – Min/max temperature and weather icons  
- **APIs Used**
  - `https://api.openweathermap.org/data/2.5/forecast`
  - `https://api.openweathermap.org/geo/1.0/direct`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+  
- [OpenWeather API Key](https://openweathermap.org/api/one-call-3)  
- (Optional) Docker & Docker Compose  

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
. .venv/Scripts/activate
# macOS/Linux
source .venv/bin/activate
```
#### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
#### 5️⃣ Run the backend
##### Step_1(bash1)
```bash
cd frontEnd
python -m http.server 3000
```
##### Step2(bash2)
```bash
 uvicorn backEnd.main:app --reload
```
#### 6️⃣ Access the App
    http://localhost:3000/html/index.html


## Project Structure
```
WeatherProject/
├── backEnd/
│   ├── core/
│   │   └── config.py
│   ├── api/
│   │   └── routers/
│   │       ├── pages.py
│   │       └── weather.py
│   ├── services/
│   │   ├── api_forecast_client.py
│   │   ├── geo_client.py
│   │   ├── geo_service.py
│   │   └── weather_service.py
│   │   
│   ├── __init__.py
    └── main.py
├── frontEnd/
│   ├── html/
│   │   └── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── .env.example
├── requirements.txt
└── README.md

```
## 🌐 WeatherProject API Documentation

Base URL:
    ```http://localhost:8000/api/v1/weather```

---

## 📡 Overview

The WeatherProject API provides access to real-time and forecasted weather data from the **OpenWeather API**.  
It supports city-based queries with automatic geocoding, returning structured JSON ready for frontend display.

---

## 🧭 Endpoints

### 1️⃣ `GET /api/weather/summary`

**Description:**  
Fetch weather summary for a given city or fallback to default coordinates from `.env`.

**Query Parameters**
```
    | Parameter | Type | Required | Description |
    |------------|------|-----------|-------------|
    | `q` | string | ❌ Optional | City name (e.g. `Seattle`, `Ashgabat`) |
```

**Example Requests**
```bash
# Get Seattle weather
GET /api/weather/summary?q=Seattle

# Get default weather (from .env coordinates)
GET /api/weather/summary
```

**Example Response**
```json
{
  "place": "Seattle, Washington, US",
  "date": "2025-11-13",
  "current": {
    "temp": 11,
    "feels_like": 9,
    "humidity": 88,
    "wind": "12 km/h",
    "precip": "0 mm",
    "icon": "10d"
  },
  "hourly": [
    {"time": "1 PM", "icon": "10d", "temp": 10},
    {"time": "4 PM", "icon": "10d", "temp": 9}
  ],
  "daily": [
    {"day": "Thu", "min": 8, "max": 13, "icon": "10d"},
    {"day": "Fri", "min": 7, "max": 12, "icon": "04d"}
  ]
}
```
## 🚧 Roadmap

- [ ] Add One Call 3.0 API integration

- [ ] Add Dockerfile & docker-compose

- [ ] Add metric/imperial toggle on frontend

- [ ] Add caching with Redis

- [ ] Add unit tests (pytest)
## 📄 License
----
## 👥 Authors
**Ilyas Baratov** - [GitHub](https://github.com/IlyasBaratov)

## 🙏 Acknowledgments

- FastAPI framework and community
- SQLAlchemy ORM
- Pydantic validation library

#### For questions or support, please open an issue on GitHub.

---

**Made with ☀️ and 💻 by Ilyas Baratov