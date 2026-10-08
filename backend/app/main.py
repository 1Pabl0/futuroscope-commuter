"""
Main FastAPI application for Futuroscope Commuter.
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.cache import cache
from app.seeds.stops_seed import seed_stops
from app.api.router import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("futuroscope.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seeded = seed_stops(db)
        logger.info(f"Database ready. Seeded {seeded} initial stops.")
    finally:
        db.close()

    # Initialize cache connection
    await cache.initialize()
    logger.info("Futuroscope Commuter API is fully operational.")

    yield

    # Shutdown
    logger.info("Shutting down cache and connections...")
    await cache.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
🚌 **Futuroscope Commuter API**

Plateforme open-source pour l'optimisation des trajets quotidiens vers la **Technopole du Futuroscope (Grand Poitiers)**.
- 🕒 **Temps Réel Multi-Modal :** Bus Vitalis (Ligne 1, 1E, 21) & Navette SNCF TER (Poitiers ↔ Gare du Futuroscope en 8 min).
- 🌤️ **Contextualisation Météo :** Open-Meteo pour la Vienne (86) avec alertes de pluie, vent et températures.
- 🧠 **Indice de Confort de Trajet (ICT) :** Algorithme prédictif de fluidité et recommandations multi-modales.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirects to Swagger API docs."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
