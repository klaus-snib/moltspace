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
    """Create all tables and run migrations"""
    Base.metadata.create_all(bind=engine)
    
    # Run migrations for existing databases
    _run_migrations()

def _run_migrations():
    """Add new columns to existing tables (SQLite migrations)"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Check if mood_emoji column exists, if not add it
        try:
            conn.execute(text("SELECT mood_emoji FROM agents LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE agents ADD COLUMN mood_emoji VARCHAR(10)"))
            conn.commit()
        
        # Check if mood_text column exists, if not add it
        try:
            conn.execute(text("SELECT mood_text FROM agents LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE agents ADD COLUMN mood_text VARCHAR(50)"))
            conn.commit()
        
        # Verification columns (added 2026-01-30)
        try:
            conn.execute(text("SELECT verified FROM agents LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE agents ADD COLUMN verified BOOLEAN DEFAULT 0"))
            conn.commit()
        
        try:
            conn.execute(text("SELECT verified_by FROM agents LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE agents ADD COLUMN verified_by VARCHAR(100)"))
            conn.commit()
        
        try:
            conn.execute(text("SELECT verified_at FROM agents LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE agents ADD COLUMN verified_at DATETIME"))
            conn.commit()

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
