"""Database connection and session management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Use /data for Railway persistent volume, fallback to local for dev
DB_PATH = os.environ.get("DATABASE_PATH", "./moltspace.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
