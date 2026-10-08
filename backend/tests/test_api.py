"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.seeds.stops_seed import seed_stops


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_stops(db)
    db.close()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_stops_endpoint(client):
    response = client.get("/api/v1/transit/stops")
    assert response.status_code == 200
    stops = response.json()
    assert len(stops) > 0
    assert any(s["id"] == "VIT_TELEPORT1" for s in stops)


def test_stop_detail_endpoint(client):
    response = client.get("/api/v1/transit/stops/VIT_TELEPORT1")
    assert response.status_code == 200
    stop = response.json()
    assert stop["name"] == "Téléport 1"
    assert "1" in stop["lines"]


def test_stop_not_found(client):
    response = client.get("/api/v1/transit/stops/NON_EXISTENT")
    assert response.status_code == 404


def test_vitalis_departures(client):
    response = client.get("/api/v1/transit/vitalis/departures?stop_id=VIT_TELEPORT1")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "vitalis"
    assert len(data["departures"]) > 0


def test_ter_departures(client):
    response = client.get("/api/v1/transit/ter/departures?stop_id=TER_GARE_POITIERS")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "sncf_ter"
    assert len(data["departures"]) > 0


def test_weather_endpoints(client):
    response = client.get("/api/v1/weather")
    assert response.status_code == 200
    data = response.json()
    assert "current" in data
    assert "temperature" in data["current"]

    resp_poi = client.get("/api/v1/weather/poitiers")
    assert resp_poi.status_code == 200


def test_ict_current(client):
    response = client.get("/api/v1/ict/current")
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 100
    assert data["level"] in ["EXCELLENT", "BON", "MOYEN", "DIFFICILE", "PERTURBÉ"]


def test_ict_simulate(client):
    payload = {
        "temperature": 12.0,
        "rain_mm": 3.5,
        "wind_gusts_kmh": 45.0,
        "avg_bus_delay_min": 6,
        "ter_cancelled": False
    }
    response = client.post("/api/v1/ict/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 75
    assert len(data["breakdown"]) > 0


def test_overview_endpoint(client):
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "ict" in data
    assert "weather" in data
    assert "next_vitalis_buses" in data
    assert "next_ter_trains" in data
    assert "key_stops" in data
