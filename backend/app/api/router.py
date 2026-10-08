"""
API v1 Router aggregator.
"""
from fastapi import APIRouter
from app.api.v1.transit import router as transit_router
from app.api.v1.weather import router as weather_router
from app.api.v1.ict import router as ict_router
from app.api.v1.overview import router as overview_router
from app.api.v1.health import router as health_router

api_router = APIRouter()

api_router.include_router(overview_router)
api_router.include_router(ict_router)
api_router.include_router(transit_router)
api_router.include_router(weather_router)
api_router.include_router(health_router)
