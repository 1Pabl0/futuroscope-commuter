"""
Unit tests for Vitalis Bus and SNCF TER Transit Services.
"""
import pytest
from app.services.vitalis_service import VitalisService
from app.services.sncf_service import SncfService
from app.seeds.stops_seed import FUTUROSCOPE_STOPS, seed_stops
from app.core.database import SessionLocal, Base, engine
from app.models.stop import Stop


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_stops(db)
    yield
    db.close()


@pytest.mark.asyncio
async def test_vitalis_departures():
    result = await VitalisService.get_departures_for_stop("VIT_TELEPORT1", "Téléport 1")
    assert result.network == "vitalis"
    assert result.stop_id == "VIT_TELEPORT1"
    assert len(result.departures) > 0
    assert result.departures[0].line in ["1", "1E", "21", "E"]
    assert result.departures[0].minutes_left >= 0


@pytest.mark.asyncio
async def test_vitalis_commuter_all():
    deps = await VitalisService.get_all_commuter_departures()
    assert len(deps) > 0
    # verify sorted by minutes_left
    minutes = [d.minutes_left for d in deps]
    assert minutes == sorted(minutes)


@pytest.mark.asyncio
async def test_sncf_ter_departures():
    result = await SncfService.get_ter_departures("TER_GARE_POITIERS", "Gare de Poitiers")
    assert result.network == "sncf_ter"
    assert len(result.departures) > 0
    assert "TER" in result.departures[0].line
    assert result.departures[0].transport_type == "train"


def test_seed_stops_count():
    db = SessionLocal()
    stops = db.query(Stop).all()
    assert len(stops) >= len(FUTUROSCOPE_STOPS)
    db.close()
