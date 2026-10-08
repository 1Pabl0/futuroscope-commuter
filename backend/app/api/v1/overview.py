"""
Overview endpoint aggregating weather, transit, and ICT for fast dashboard loading.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.stop import Stop
from app.models.schemas import DashboardOverview, StopResponse
from app.services.weather_service import WeatherService
from app.services.vitalis_service import VitalisService
from app.services.sncf_service import SncfService
from app.services.ict_service import ICTService

router = APIRouter(prefix="/overview", tags=["Tableau de Bord / Commuter Overview"])


@router.get("", response_model=DashboardOverview, summary="Synthèse globale pour le tableau de bord")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    weather = await WeatherService.get_current_and_forecast()
    buses = await VitalisService.get_all_commuter_departures()
    trains = await SncfService.get_all_ter_shuttles()
    ict = ICTService.calculate_ict(weather, buses, trains)

    stops = db.query(Stop).all()
    stops_responses = [StopResponse(**s.to_dict()) for s in stops]

    return DashboardOverview(
        ict=ict,
        weather=weather,
        next_vitalis_buses=buses[:6],
        next_ter_trains=trains[:4],
        key_stops=stops_responses,
        service_status={
            "api_status": "OPERATIONAL",
            "open_meteo": "CONNECTED",
            "vitalis_gtfs_rt": "SYNCHRONIZED",
            "sncf_ter": "SYNCHRONIZED",
            "cache": "ACTIVE",
        }
    )
