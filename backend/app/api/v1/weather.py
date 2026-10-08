"""
Weather API endpoints for Technopole du Futuroscope and Poitiers.
"""
from typing import Optional
from fastapi import APIRouter, Query
from app.core.config import settings
from app.models.schemas import WeatherResponse
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Météo Locale (Vienne 86)"])


@router.get("", response_model=WeatherResponse, summary="Météo actuelle et prévisions pour la Technopole du Futuroscope")
async def get_technopole_weather(
    lat: Optional[float] = Query(None, description="Latitude personnalisée"),
    lon: Optional[float] = Query(None, description="Longitude personnalisée")
):
    return await WeatherService.get_current_and_forecast(
        lat=lat if lat is not None else settings.FUTUROSCOPE_LAT,
        lon=lon if lon is not None else settings.FUTUROSCOPE_LON,
        location_name="Technopole du Futuroscope"
    )


@router.get("/poitiers", response_model=WeatherResponse, summary="Météo actuelle pour Poitiers Centre")
async def get_poitiers_weather():
    return await WeatherService.get_current_and_forecast(
        lat=settings.POITIERS_LAT,
        lon=settings.POITIERS_LON,
        location_name="Poitiers Centre (Gare Toumaï)"
    )
