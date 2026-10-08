"""
Pydantic schemas for Futuroscope Commuter API requests and responses.
"""
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Transport Stops
# -------------------------------------------------------------
class StopBase(BaseModel):
    id: str
    name: str
    transport_type: str
    network: str
    latitude: float
    longitude: float
    lines: List[str] = []
    zone: str
    wheelchair_accessible: bool = True
    has_bike_station: bool = False
    has_shelter: bool = True


class StopResponse(StopBase):
    pass


# -------------------------------------------------------------
# Transit Real-Time Departures
# -------------------------------------------------------------
class Departure(BaseModel):
    id: str
    line: str
    network: str  # "vitalis" or "sncf_ter"
    transport_type: str  # "bus" or "train"
    destination: str
    stop_id: str
    stop_name: str
    planned_time: str      # "08:14"
    estimated_time: str    # "08:17"
    minutes_left: int      # 3
    delay_minutes: int     # 3
    status: str            # "ON_TIME", "DELAYED", "EARLY", "CANCELLED"
    occupancy: Optional[str] = "MANY_SEATS_AVAILABLE"  # Vitalis / TER crowdedness


class TransitDeparturesResponse(BaseModel):
    stop_id: str
    stop_name: str
    network: str
    departures: List[Departure]
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disruption_alert: Optional[str] = None


# -------------------------------------------------------------
# Weather
# -------------------------------------------------------------
class WeatherCurrent(BaseModel):
    temperature: float
    apparent_temperature: float
    relative_humidity: int
    precipitation: float       # mm
    rain: float                # mm
    weather_code: int
    weather_description: str
    weather_icon: str
    wind_speed: float          # km/h
    wind_gusts: float          # km/h
    is_day: bool
    comfort_category: str      # "Agréable", "Frais", "Pluvieux", "Tempétueux"


class HourlyForecastItem(BaseModel):
    time: str
    temperature: float
    precipitation_probability: int
    precipitation: float
    weather_description: str
    weather_icon: str
    wind_speed: float


class WeatherResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    current: WeatherCurrent
    hourly: List[HourlyForecastItem]
    alerts: List[str] = []
    cached: bool = False


# -------------------------------------------------------------
# Indice de Confort de Trajet (ICT)
# -------------------------------------------------------------
class ICTFactorBreakdown(BaseModel):
    name: str
    score: int          # 0 to 100
    impact: str         # "Positif", "Neutre", "Négatif", "Très négatif"
    description: str


class ICTResponse(BaseModel):
    score: int = Field(ge=0, le=100, description="Score global de fluidité et confort (0-100)")
    level: str  # "EXCELLENT", "BON", "MOYEN", "DIFFICILE", "PERTURBÉ"
    badge_label: str
    color_hex: str
    summary: str
    weather_subscore: int
    transit_subscore: int
    breakdown: List[ICTFactorBreakdown]
    recommended_mode: str
    alternative_mode: str
    commuter_advice: List[str]
    equipment_suggestions: List[str]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# -------------------------------------------------------------
# Global Dashboard Overview
# -------------------------------------------------------------
class DashboardOverview(BaseModel):
    ict: ICTResponse
    weather: WeatherResponse
    next_vitalis_buses: List[Departure]
    next_ter_trains: List[Departure]
    key_stops: List[StopResponse]
    service_status: dict
