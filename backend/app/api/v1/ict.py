"""
Indice de Confort de Trajet (ICT) API endpoints.
Provides real-time predictive commute index and simulation capabilities.
"""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.models.schemas import ICTResponse, WeatherCurrent, WeatherResponse, Departure
from app.services.weather_service import WeatherService
from app.services.vitalis_service import VitalisService
from app.services.sncf_service import SncfService
from app.services.ict_service import ICTService

router = APIRouter(prefix="/ict", tags=["Indice de Confort de Trajet (ICT)"])


class ICTSimulationRequest(BaseModel):
    temperature: float = Field(15.0, description="Température en °C")
    rain_mm: float = Field(0.0, ge=0.0, description="Précipitations en mm/h")
    wind_gusts_kmh: float = Field(15.0, ge=0.0, description="Rafales de vent en km/h")
    avg_bus_delay_min: int = Field(0, ge=0, description="Retard moyen des bus Vitalis en min")
    ter_cancelled: bool = Field(False, description="Simuler une annulation de train TER")


@router.get("/current", response_model=ICTResponse, summary="Calcul en temps réel de l'Indice de Confort de Trajet")
async def get_current_ict():
    weather = await WeatherService.get_current_and_forecast()
    buses = await VitalisService.get_all_commuter_departures()
    trains = await SncfService.get_all_ter_shuttles()
    return ICTService.calculate_ict(weather, buses, trains)


@router.post("/simulate", response_model=ICTResponse, summary="Simuler un scénario de trajet (météo + retards)")
def simulate_ict(req: ICTSimulationRequest):
    # Simulated weather object
    weather_sim = WeatherResponse(
        location_name="Simulation Technopole",
        latitude=46.6698,
        longitude=0.3621,
        current=WeatherCurrent(
            temperature=req.temperature,
            apparent_temperature=req.temperature - 1.0,
            relative_humidity=80 if req.rain_mm > 0 else 55,
            precipitation=req.rain_mm,
            rain=req.rain_mm,
            weather_code=61 if req.rain_mm > 0 else 1,
            weather_description="Pluie simulée" if req.rain_mm > 0 else "Ciel dégagé",
            weather_icon="🌧️" if req.rain_mm > 0 else "🌤️",
            wind_speed=req.wind_gusts_kmh * 0.7,
            wind_gusts=req.wind_gusts_kmh,
            is_day=True,
            comfort_category="Simulation"
        ),
        hourly=[]
    )

    # Simulated departures
    sim_buses = [
        Departure(
            id="SIM-BUS-1",
            line="1",
            network="vitalis",
            transport_type="bus",
            destination="Futuroscope LPI",
            stop_id="VIT_TELEPORT1",
            stop_name="Téléport 1",
            planned_time="08:15",
            estimated_time="08:20",
            minutes_left=5 + req.avg_bus_delay_min,
            delay_minutes=req.avg_bus_delay_min,
            status="DELAYED" if req.avg_bus_delay_min > 2 else "ON_TIME",
        )
    ]

    sim_trains = [
        Departure(
            id="SIM-TER-1",
            line="TER 864102",
            network="sncf_ter",
            transport_type="train",
            destination="Gare du Futuroscope",
            stop_id="TER_GARE_POITIERS",
            stop_name="Gare de Poitiers",
            planned_time="08:25",
            estimated_time="08:25",
            minutes_left=15,
            delay_minutes=0 if not req.ter_cancelled else 0,
            status="CANCELLED" if req.ter_cancelled else "ON_TIME",
        )
    ]

    return ICTService.calculate_ict(weather_sim, sim_buses, sim_trains)
