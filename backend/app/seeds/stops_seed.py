"""
Seed script and dataset for Vitalis Bus and SNCF TER stops around Futuroscope & Poitiers.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.stop import Stop

FUTUROSCOPE_STOPS: List[Dict[str, Any]] = [
    {
        "id": "VIT_TELEPORT1",
        "name": "Téléport 1",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6668,
        "longitude": 0.3602,
        "lines": ["1", "1E", "21"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_TELEPORT2",
        "name": "Téléport 2",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6695,
        "longitude": 0.3640,
        "lines": ["1", "1E"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_TELEPORT4",
        "name": "Téléport 4 (ISAE-ENSMA)",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6612,
        "longitude": 0.3625,
        "lines": ["1", "21"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_LPI",
        "name": "Futuroscope LPI",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6644,
        "longitude": 0.3678,
        "lines": ["1", "1E"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_GARE_FUTUROSCOPE",
        "name": "Gare du Futuroscope (Passerelle)",
        "transport_type": "multimodal",
        "network": "vitalis",
        "latitude": 46.6601,
        "longitude": 0.3542,
        "lines": ["1", "E", "TER"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "TER_GARE_FUTUROSCOPE",
        "name": "Gare du Futuroscope (TER)",
        "transport_type": "train",
        "network": "sncf_ter",
        "latitude": 46.6600,
        "longitude": 0.3538,
        "lines": ["TER Poitiers-Tours", "Navette Technopole"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "TER_GARE_POITIERS",
        "name": "Gare de Poitiers Toumaï (TER/TGV)",
        "transport_type": "train",
        "network": "sncf_ter",
        "latitude": 46.5828,
        "longitude": 0.3340,
        "lines": ["TER Poitiers-Tours", "TER Angoulême", "Navette Technopole"],
        "zone": "Poitiers Centre",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_POITIERS_GARE",
        "name": "Gare de Poitiers (Pôle Toumaï)",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.5831,
        "longitude": 0.3345,
        "lines": ["1", "1E", "2A", "2B", "3", "11"],
        "zone": "Poitiers Centre",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_BONCENNE",
        "name": "Pôle Boncenne (Poitiers Centre)",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.5815,
        "longitude": 0.3412,
        "lines": ["1", "1E", "2A", "3"],
        "zone": "Poitiers Centre",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_ARENA",
        "name": "Arena Futuroscope",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6730,
        "longitude": 0.3705,
        "lines": ["1", "21"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": False,
        "has_shelter": True,
    },
    {
        "id": "VIT_CHASSENEUIL",
        "name": "Chasseneuil Mairie",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6502,
        "longitude": 0.3718,
        "lines": ["1", "21"],
        "zone": "Chasseneuil-du-Poitou",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    },
    {
        "id": "VIT_PARC_FUTUROSCOPE",
        "name": "Parc du Futuroscope Entrée",
        "transport_type": "bus",
        "network": "vitalis",
        "latitude": 46.6702,
        "longitude": 0.3690,
        "lines": ["1", "1E", "21"],
        "zone": "Technopole Futuroscope",
        "wheelchair_accessible": True,
        "has_bike_station": True,
        "has_shelter": True,
    }
]


def seed_stops(db: Session):
    """Inserts initial stops into database if not already present."""
    count = 0
    for stop_data in FUTUROSCOPE_STOPS:
        existing = db.query(Stop).filter(Stop.id == stop_data["id"]).first()
        if not existing:
            stop_obj = Stop(**stop_data)
            db.add(stop_obj)
            count += 1
    if count > 0:
        db.commit()
    return count
