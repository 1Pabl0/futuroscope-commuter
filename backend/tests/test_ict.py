"""
Unit tests for the Indice de Confort de Trajet (ICT) predictive algorithm.
"""
from datetime import datetime
from app.models.schemas import WeatherResponse, WeatherCurrent, Departure
from app.services.ict_service import ICTService


def make_dummy_weather(temp=18.0, rain=0.0, wind_gusts=15.0):
    return WeatherResponse(
        location_name="Technopole",
        latitude=46.6698,
        longitude=0.3621,
        current=WeatherCurrent(
            temperature=temp,
            apparent_temperature=temp,
            relative_humidity=50,
            precipitation=rain,
            rain=rain,
            weather_code=0,
            weather_description="Ensoleillé",
            weather_icon="☀️",
            wind_speed=wind_gusts * 0.7,
            wind_gusts=wind_gusts,
            is_day=True,
            comfort_category="Agréable"
        ),
        hourly=[]
    )


def make_dummy_bus(delay=0, cancelled=False):
    return Departure(
        id="B1",
        line="1",
        network="vitalis",
        transport_type="bus",
        destination="Futuroscope LPI",
        stop_id="VIT_TELEPORT1",
        stop_name="Téléport 1",
        planned_time="08:00",
        estimated_time="08:00",
        minutes_left=5 + delay,
        delay_minutes=delay,
        status="CANCELLED" if cancelled else ("DELAYED" if delay > 0 else "ON_TIME")
    )


def test_ict_ideal_conditions():
    weather = make_dummy_weather(temp=20.0, rain=0.0, wind_gusts=10.0)
    buses = [make_dummy_bus(delay=0)]
    trains = [make_dummy_bus(delay=0)]

    ict = ICTService.calculate_ict(weather, buses, trains)
    assert ict.score >= 85
    assert ict.level == "EXCELLENT"
    assert "Vélo" in ict.recommended_mode


def test_ict_stormy_weather_recommends_ter():
    weather = make_dummy_weather(temp=9.0, rain=4.5, wind_gusts=55.0)
    buses = [make_dummy_bus(delay=4)]
    trains = [make_dummy_bus(delay=0)]

    ict = ICTService.calculate_ict(weather, buses, trains)
    assert ict.score < 70
    assert "TER" in ict.recommended_mode
    assert any("imperméable" in s.lower() or "parapluie" in s.lower() for s in ict.equipment_suggestions)


def test_ict_severe_delays_and_cancellations():
    weather = make_dummy_weather(temp=15.0, rain=0.0, wind_gusts=10.0)
    buses = [make_dummy_bus(delay=15), make_dummy_bus(cancelled=True)]
    trains = [make_dummy_bus(delay=12)]

    ict = ICTService.calculate_ict(weather, buses, trains)
    assert ict.transit_subscore < 60
    assert ict.score < 75
    assert len(ict.breakdown) > 0
