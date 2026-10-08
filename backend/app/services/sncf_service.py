"""
Service for SNCF TER Nouvelle-Aquitaine shuttle (Poitiers <-> Gare du Futuroscope).
Handles rail commuter schedules, delays, and platform tracks.
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import random
from app.core.config import settings
from app.core.cache import cache
from app.models.schemas import Departure, TransitDeparturesResponse

logger = logging.getLogger("futuroscope.sncf")

TER_DESTINATIONS = [
    "Gare du Futuroscope",
    "Poitiers (Gare Centre Toumaï)",
    "Tours Centre",
    "Châtellerault",
]

PLATFORMS = ["Voie 1", "Voie 2", "Voie A", "Voie B"]


class SncfService:
    @staticmethod
    async def get_ter_departures(stop_id: str = "TER_GARE_POITIERS", stop_name: str = "Gare de Poitiers") -> TransitDeparturesResponse:
        cache_key = f"sncf:ter:{stop_id}"
        cached = await cache.get(cache_key)
        if cached:
            return TransitDeparturesResponse(**cached)

        departures = SncfService._generate_ter_departures(stop_id, stop_name)

        resp = TransitDeparturesResponse(
            stop_id=stop_id,
            stop_name=stop_name,
            network="sncf_ter",
            departures=departures,
            last_updated=datetime.now(timezone.utc),
            disruption_alert=None if random.random() > 0.15 else "Info TER : Voie banalisée entre Futuroscope et Chasseneuil."
        )

        await cache.set(cache_key, resp.model_dump(), ttl_seconds=60)
        return resp

    @staticmethod
    async def get_all_ter_shuttles() -> List[Departure]:
        """Returns combined Poitiers -> Futuroscope and Futuroscope -> Poitiers trains."""
        cache_key = "sncf:ter_all"
        cached = await cache.get(cache_key)
        if cached:
            return [Departure(**d) for d in cached]

        dep_poitiers = SncfService._generate_ter_departures("TER_GARE_POITIERS", "Gare de Poitiers")
        dep_futuro = SncfService._generate_ter_departures("TER_GARE_FUTUROSCOPE", "Gare du Futuroscope")

        combined = dep_poitiers[:3] + dep_futuro[:3]
        combined.sort(key=lambda d: d.minutes_left)

        await cache.set(cache_key, [d.model_dump() for d in combined], ttl_seconds=60)
        return combined

    @staticmethod
    def _generate_ter_departures(stop_id: str, stop_name: str) -> List[Departure]:
        now = datetime.now()
        is_rush_hour = (7 <= now.hour <= 9) or (16 <= now.hour <= 19)

        time_block = now.minute // 5
        rng = random.Random(f"{stop_id}_{now.hour}_{time_block}_ter")

        # Typical intervals for TER Nouvelle-Aquitaine Poitiers-Futuroscope
        intervals = [8, 22, 45, 68] if is_rush_hour else [14, 42, 75]

        departures = []
        is_from_poitiers = "POITIERS" in stop_id

        for idx, mins in enumerate(intervals):
            destination = "Gare du Futuroscope (Navette 8 min)" if is_from_poitiers else "Poitiers Centre (Navette 8 min)"
            if idx % 2 == 1:
                destination = "Tours via Futuroscope" if is_from_poitiers else "Angoulême via Poitiers"

            train_number = rng.randint(864100, 864199)
            has_delay = rng.random() < 0.20
            delay = rng.randint(3, 9) if has_delay else 0
            is_cancelled = rng.random() < 0.02

            status = "CANCELLED" if is_cancelled else ("DELAYED" if delay > 0 else "ON_TIME")
            planned_dt = now + timedelta(minutes=mins)
            estimated_dt = planned_dt + timedelta(minutes=delay)

            departures.append(
                Departure(
                    id=f"TER-{train_number}",
                    line=f"TER {train_number}",
                    network="sncf_ter",
                    transport_type="train",
                    destination=destination,
                    stop_id=stop_id,
                    stop_name=f"{stop_name} ({rng.choice(PLATFORMS)})",
                    planned_time=planned_dt.strftime("%H:%M"),
                    estimated_time=estimated_dt.strftime("%H:%M"),
                    minutes_left=mins + delay if not is_cancelled else 0,
                    delay_minutes=delay,
                    status=status,
                    occupancy="FEW_SEATS_AVAILABLE" if is_rush_hour else "MANY_SEATS_AVAILABLE"
                )
            )

        departures.sort(key=lambda d: d.minutes_left)
        return departures
