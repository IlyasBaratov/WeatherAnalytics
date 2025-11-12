import pathlib

from fastapi import FastAPI, Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from backEnd.services import api_forecast_client
from backEnd.services.api_forecast_client import ApiForecastClient

app = FastAPI()
base_dir = pathlib.Path(__file__).resolve().parent.parent
frontend_dir = base_dir / "frontend"/"html"
static_dir = base_dir / "frontend"/"css"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(frontend_dir))

@app.get("/")
async def root(request: Request):
    sample = {
        "place": "Ashgabat",
        "date": "Tuesday, Aug 5, 2025",
        "current": {
            "temp": 20, "icon": "☀️",
            "feels_like": 18, "humidity": 46, "wind": "14 km/h", "precip": "0 mm"
        },
        "daily": [
            {"name": "Tue", "hi": 20, "lo": 14, "icon": "🌧️"},
            {"name": "Wed", "hi": 21, "lo": 15, "icon": "🌧️"},
            {"name": "Thu", "hi": 24, "lo": 14, "icon": "☀️"},
            {"name": "Fri", "hi": 25, "lo": 13, "icon": "⛅"},
            {"name": "Sat", "hi": 21, "lo": 15, "icon": "🌩️"},
            {"name": "Sun", "hi": 25, "lo": 16, "icon": "🌧️"},
            {"name": "Mon", "hi": 24, "lo": 15, "icon": "🌫️"},
        ],
        "hourly": [
            {"time": "3 PM", "icon": "🌥️", "temp": 20},
            {"time": "4 PM", "icon": "🌥️", "temp": 20},
            {"time": "5 PM", "icon": "🌤️", "temp": 20},
            {"time": "6 PM", "icon": "🌧️", "temp": 19},
            {"time": "7 PM", "icon": "🌧️", "temp": 18},
            {"time": "8 PM", "icon": "🌧️", "temp": 18},
            {"time": "9 PM", "icon": "☁️", "temp": 17},
            {"time": "10 PM", "icon": "☁️", "temp": 17},
        ],

    }
    return templates.TemplateResponse("index.html", {"request": request, **sample})

    # return FileResponse(frontend_dir / "index.html")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/weather")
async def weather():
    params = {"lat": 47.6061, "lon": 122.3328, 'appid':'7f043836018ef59e851eaeb9fb2b3580'}
    forecast_service =ApiForecastClient()
    return await forecast_service._make_request('forecast', params)


#47.861694, -122.009278