"""
Weather service integrating Open-Meteo API for Technopole du Futuroscope & Poitiers.
Handles live fetching, caching, weather code translations, and localized warnings.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from app.core.config import settings
from app.core.cache import cache
from app.models.schemas import WeatherCurrent, HourlyForecastItem, WeatherResponse

logger = logging.getLogger("futuroscope.weather")

WMO_CODE_MAP = {
    0: ("Ciel dégagé", "☀️"),
    1: ("Principalement dégagé", "🌤️"),
    2: ("Partiellement nuageux", "⛅"),
    3: ("Couvert", "☁️"),
    45: ("Brouillard", "🌫️"),
    48: ("Brouillard givrant", "🌫️❄️"),
    51: ("Bruine légère", "🌦️"),
    53: ("Bruine modérée", "🌧️"),
    55: ("Bruine dense", "🌧️"),
    61: ("Pluie faible", "🌦️"),
    63: ("Pluie modérée", "🌧️"),
    65: ("Pluie forte", "🌧️⚡"),
    71: ("Chute de neige légère", "🌨️"),
    73: ("Chute de neige modérée", "🌨️"),
    75: ("Chute de neige forte", "❄️"),
    77: ("Grains de neige", "🌨️"),
    80: ("Averses de pluie faibles", "🌦️"),
    81: ("Averses modérées", "🌧️"),
    82: ("Averses violentes", "⛈️"),
    85: ("Averses de neige légères", "🌨️"),
    86: ("Averses de neige fortes", "❄️"),
    95: ("Orage faible à modéré", "⛈️"),
    96: ("Orage avec grêle légère", "⛈️🧊"),
    99: ("Orage violent avec grêle", "⛈️⚡"),
}


def get_weather_desc_and_icon(code: int) -> tuple[str, str]:
    return WMO_CODE_MAP.get(code, ("Conditions variables", "🌤️"))


def categorize_comfort(temp: float, rain: float, wind: float) -> str:
    if rain > 2.0 or wind > 50:
        return "Tempétueux / Très humide"
    if rain > 0.3:
        return "Pluvieux"
    if temp < 5:
        return "Très frais / Froid"
    if temp < 14:
        return "Frais mais sec"
    if temp > 30:
        return "Chaleur intense"
    return "Très agréable"


class WeatherService:
    @staticmethod
    async def get_current_and_forecast(
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        location_name: str = "Technopole du Futuroscope"
    ) -> WeatherResponse:
        latitude = lat if lat is not None else settings.FUTUROSCOPE_LAT
        longitude = lon if lon is not None else settings.FUTUROSCOPE_LON
        cache_key = f"weather:{round(latitude, 4)}:{round(longitude, 4)}"

        # Check Cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            cached_data["cached"] = True
            return WeatherResponse(**cached_data)

        # Call Open-Meteo API
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,wind_gusts_10m,is_day",
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m",
            "timezone": "Europe/Paris",
            "forecast_days": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(settings.OPEN_METEO_BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    response_obj = WeatherService._parse_open_meteo_response(data, location_name, latitude, longitude)
                    await cache.set(cache_key, response_obj.model_dump(), ttl_seconds=300)
                    return response_obj
                else:
                    logger.warning(f"Open-Meteo returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch Open-Meteo data ({e}). Generating simulated Vienne data.")

        # Robust Fallback
        fallback_obj = WeatherService._generate_realistic_fallback(location_name, latitude, longitude)
        return fallback_obj

    @staticmethod
    def _parse_open_meteo_response(data: dict, location_name: str, lat: float, lon: float) -> WeatherResponse:
        current_data = data.get("current", {})
        hourly_data = data.get("hourly", {})

        weather_code = current_data.get("weather_code", 1)
        desc, icon = get_weather_desc_and_icon(weather_code)
        temp = current_data.get("temperature_2m", 15.0)
        apparent = current_data.get("apparent_temperature", 14.5)
        rain = current_data.get("rain", 0.0)
        wind = current_data.get("wind_speed_10m", 12.0)
        gusts = current_data.get("wind_gusts_10m", 20.0)
        humidity = current_data.get("relative_humidity_2m", 70)
        is_day = bool(current_data.get("is_day", 1))

        current = WeatherCurrent(
            temperature=round(temp, 1),
            apparent_temperature=round(apparent, 1),
            relative_humidity=humidity,
            precipitation=current_data.get("precipitation", 0.0),
            rain=rain,
            weather_code=weather_code,
            weather_description=desc,
            weather_icon=icon,
            wind_speed=round(wind, 1),
            wind_gusts=round(gusts, 1),
            is_day=is_day,
            comfort_category=categorize_comfort(temp, rain, gusts)
        )

        hourly_items: List[HourlyForecastItem] = []
        times = hourly_data.get("time", [])
        temps = hourly_data.get("temperature_2m", [])
        precip_probs = hourly_data.get("precipitation_probability", [])
        precips = hourly_data.get("precipitation", [])
        codes = hourly_data.get("weather_code", [])
        winds = hourly_data.get("wind_speed_10m", [])

        # Filter the next 8 to 12 hours starting from now
        now_hour_str = datetime.now().strftime("%Y-%m-%dT%H:00")
        start_idx = 0
        for i, t in enumerate(times):
            if t >= now_hour_str:
                start_idx = i
                break

        for i in range(start_idx, min(start_idx + 10, len(times))):
            h_code = codes[i] if i < len(codes) else 1
            h_desc, h_icon = get_weather_desc_and_icon(h_code)
            hourly_items.append(
                HourlyForecastItem(
                    time=times[i].split("T")[-1],
                    temperature=round(temps[i], 1) if i < len(temps) else 15.0,
                    precipitation_probability=precip_probs[i] if i < len(precip_probs) else 0,
                    precipitation=precips[i] if i < len(precips) else 0.0,
                    weather_description=h_desc,
                    weather_icon=h_icon,
                    wind_speed=round(winds[i], 1) if i < len(winds) else 10.0,
                )
            )

        alerts = []
        if gusts > 45:
            alerts.append(f"⚠️ Fortes rafales de vent ({gusts:.0f} km/h) sur la Technopole.")
        if rain > 1.5:
            alerts.append(f"🌧️ Pluie continue ({rain:.1f} mm/h) - circulation potentiellement ralentie.")
        elif any(item.precipitation_probability > 60 for item in hourly_items[:3]):
            alerts.append("☂️ Risque élevé d'averses sur votre trajet de retour.")

        return WeatherResponse(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            current=current,
            hourly=hourly_items,
            alerts=alerts,
            cached=False
        )

    @staticmethod
    def _generate_realistic_fallback(location_name: str, lat: float, lon: float) -> WeatherResponse:
        current_hour = datetime.now().hour
        temp = 16.5 if 10 <= current_hour <= 18 else 11.2
        apparent = temp - 1.2
        wind = 14.0
        gusts = 22.0
        rain = 0.0
        weather_code = 1
        desc, icon = get_weather_desc_and_icon(weather_code)

        current = WeatherCurrent(
            temperature=temp,
            apparent_temperature=apparent,
            relative_humidity=65,
            precipitation=rain,
            rain=rain,
            weather_code=weather_code,
            weather_description=desc,
            weather_icon=icon,
            wind_speed=wind,
            wind_gusts=gusts,
            is_day=7 <= current_hour <= 20,
            comfort_category=categorize_comfort(temp, rain, gusts)
        )

        hourly_items = []
        for offset in range(8):
            h = (current_hour + offset) % 24
            time_str = f"{h:02d}:00"
            hourly_items.append(
                HourlyForecastItem(
                    time=time_str,
                    temperature=round(temp - 0.5 * offset, 1),
                    precipitation_probability=10 if offset < 4 else 25,
                    precipitation=0.0,
                    weather_description="Éclaircies",
                    weather_icon="⛅",
                    wind_speed=round(wind + offset, 1),
                )
            )

        return WeatherResponse(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            current=current,
            hourly=hourly_items,
            alerts=["Données météo locales simulées (Open-Meteo Vienne)"],
            cached=False
        )
