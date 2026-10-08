"""
Application configuration using Pydantic Settings.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core App
    PROJECT_NAME: str = "Futuroscope Commuter API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Server Host & Ports
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]

    # Geolocation Coordinates (Technopole du Futuroscope & Poitiers)
    FUTUROSCOPE_LAT: float = 46.6698
    FUTUROSCOPE_LON: float = 0.3621
    POITIERS_LAT: float = 46.5802
    POITIERS_LON: float = 0.3404

    # Cache & Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 180  # 3 minutes cache for transit/weather

    # Database
    DATABASE_URL: str = "sqlite:///./futuroscope.db"

    # Weather
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    # Grand Poitiers / Vitalis
    VITALIS_API_KEY: Optional[str] = None
    VITALIS_BASE_URL: str = "https://data.grandpoitiers.fr/api"

    # SNCF
    SNCF_API_KEY: Optional[str] = None
    SNCF_BASE_URL: str = "https://api.sncf.com/v1"


settings = Settings()
