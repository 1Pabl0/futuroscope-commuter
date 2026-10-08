"""
SQLAlchemy models for transport stops and commuter POIs.
"""
from sqlalchemy import Column, String, Float, Boolean, JSON
from app.core.database import Base


class Stop(Base):
    __tablename__ = "stops"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    transport_type = Column(String, nullable=False)  # "bus", "train", "multimodal"
    network = Column(String, nullable=False)         # "vitalis", "sncf_ter"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    lines = Column(JSON, default=list)               # e.g. ["1", "1E"] or ["TER Poitiers-Tours"]
    zone = Column(String, nullable=False)            # "Technopole Futuroscope", "Poitiers Centre", etc.
    wheelchair_accessible = Column(Boolean, default=True)
    has_bike_station = Column(Boolean, default=False)
    has_shelter = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "transport_type": self.transport_type,
            "network": self.network,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "lines": self.lines or [],
            "zone": self.zone,
            "wheelchair_accessible": self.wheelchair_accessible,
            "has_bike_station": self.has_bike_station,
            "has_shelter": self.has_shelter,
        }
