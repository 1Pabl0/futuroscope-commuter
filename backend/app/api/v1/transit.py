"""
Transit API endpoints: Stops, Vitalis Buses, and SNCF TER Trains.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.stop import Stop
from app.models.schemas import StopResponse, TransitDeparturesResponse, Departure
from app.services.vitalis_service import VitalisService
from app.services.sncf_service import SncfService

router = APIRouter(prefix="/transit", tags=["Transit & Transports"])


@router.get("/stops", response_model=List[StopResponse], summary="Liste des arrêts de transport")
def get_stops(
    network: Optional[str] = Query(None, description="Filtrer par réseau: 'vitalis' ou 'sncf_ter'"),
    zone: Optional[str] = Query(None, description="Filtrer par zone: e.g. 'Technopole Futuroscope'"),
    db: Session = Depends(get_db)
):
    query = db.query(Stop)
    if network:
        query = query.filter(Stop.network == network)
    if zone:
        query = query.filter(Stop.zone == zone)
    return [s.to_dict() for s in query.all()]


@router.get("/stops/{stop_id}", response_model=StopResponse, summary="Détail d'un arrêt spécifique")
def get_stop_detail(stop_id: str, db: Session = Depends(get_db)):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail=f"Arrêt {stop_id} introuvable.")
    return stop.to_dict()


@router.get("/vitalis/departures", response_model=TransitDeparturesResponse, summary="Prochains passages Bus Vitalis (Grand Poitiers)")
async def get_vitalis_departures(
    stop_id: str = Query("VIT_TELEPORT1", description="Identifiant de l'arrêt Vitalis"),
    db: Session = Depends(get_db)
):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    stop_name = stop.name if stop else "Arrêt Technopole"
    return await VitalisService.get_departures_for_stop(stop_id, stop_name)


@router.get("/ter/departures", response_model=TransitDeparturesResponse, summary="Prochains passages Navette TER (Poitiers <-> Futuroscope)")
async def get_ter_departures(
    stop_id: str = Query("TER_GARE_POITIERS", description="Gare de départ: TER_GARE_POITIERS ou TER_GARE_FUTUROSCOPE"),
    db: Session = Depends(get_db)
):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    stop_name = stop.name if stop else "Gare TER"
    return await SncfService.get_ter_departures(stop_id, stop_name)
