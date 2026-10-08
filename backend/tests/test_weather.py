"""
Unit tests for Weather Service and Open-Meteo integration.
"""
import pytest
from app.services.weather_service import (
    WeatherService,
    get_weather_desc_and_icon,
    categorize_comfort
)


def test_weather_code_mapping():
    desc, icon = get_weather_desc_and_icon(0)
    assert desc == "Ciel dégagé"
    assert icon == "☀️"

    desc, icon = get_weather_desc_and_icon(63)
    assert desc == "Pluie modérée"
    assert icon == "🌧️"

    desc, icon = get_weather_desc_and_icon(9999)
    assert desc == "Conditions variables"


def test_comfort_categorization():
    assert categorize_comfort(temp=20, rain=0, wind=10) == "Très agréable"
    assert categorize_comfort(temp=3, rain=0, wind=10) == "Très frais / Froid"
    assert categorize_comfort(temp=15, rain=1.5, wind=10) == "Pluvieux"
    assert categorize_comfort(temp=15, rain=4.0, wind=60) == "Tempétueux / Très humide"


@pytest.mark.asyncio
async def test_get_current_and_forecast_fallback():
    weather_resp = await WeatherService.get_current_and_forecast()
    assert weather_resp is not None
    assert weather_resp.location_name == "Technopole du Futuroscope"
    assert weather_resp.current.temperature is not None
    assert weather_resp.current.weather_description != ""
    assert len(weather_resp.hourly) > 0
