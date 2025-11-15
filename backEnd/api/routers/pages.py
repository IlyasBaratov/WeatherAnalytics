from typing import Optional
from fastapi import APIRouter, Request, Query, Depends
from services.weather_service import WeatherService
from services.geo_service import GeoService
from core.config import settings

router = APIRouter()
def get_weather_service() -> WeatherService:
    return WeatherService()
def get_geo_service() -> GeoService:
    return GeoService()
@router.get("/")
async def home(
        request: Request,
        q: Optional[str] = Query(None, description="Place name"),
        lat: Optional[float] = Query(None),
        lon : Optional[float] = Query(None),
        weather_service: WeatherService = Depends(get_weather_service),
        geo_service: GeoService = Depends(get_geo_service)):
    '''Determine the city and latitude and longitude of the given query.'''
    display_city = None
    if q:
        resolved = await geo_service.resolve_coords_from_query(q)
        if resolved:
            lat, lon, display_city = resolved
        else:
            lat = lat or settings.default_lat
            lon = lon or settings.default_lon
    if lat is None or lon is None:
        lat = settings.default_lat
        lon = settings.default_lon
    if not display_city:
        display_city = await geo_service.resolve_place_from_coords(lat, lon)
        if not display_city:
            display_city = f"{lat:.4f}, {lon:.4f}"


    '''fetch the weather data for the given latitude and longitude and build the context.'''
    data = await weather_service.fetch_data(lat, lon)
    context = weather_service.build_context(data)
    '''add the query to the context if it was provided.'''

    context["place"] = display_city or context.get("place") or f"{lat:.4f}, {lon:.4f}"

    '''render the page with the context.'''
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request, **context,})






