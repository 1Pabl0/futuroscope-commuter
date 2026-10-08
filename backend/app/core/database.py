"""
Database configuration with SQLAlchemy.
Works with PostgreSQL/PostGIS in Docker/production, and SQLite locally.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Adapt connection string for SQLite if running locally
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite+aiosqlite:///"):
    # sync engine for synchronous seed & queries
    db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
