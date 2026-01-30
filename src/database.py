"""Database connection and session management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Support both SQLite (local dev) and PostgreSQL (production)
# Railway provides DATABASE_URL for PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL from Railway (or other provider)
    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(DATABASE_URL)
else:
    # Local development - use SQLite
    DB_PATH = os.environ.get("DATABASE_PATH", "./moltspace.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # SQLite specific
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_migrations():
    """Run database migrations for new columns/tables.
    
    SQLAlchemy's create_all doesn't add columns to existing tables,
    so we need to handle schema evolution manually.
    """
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Add voice_intro_url column if it doesn't exist
        try:
            conn.execute(text("ALTER TABLE agents ADD COLUMN voice_intro_url VARCHAR(500)"))
            conn.commit()
            print("✅ Migration: Added voice_intro_url column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                pass  # Column already exists
            else:
                print(f"⚠️ Migration warning (voice_intro_url): {e}")
        
        # Create voice_messages table if it doesn't exist (create_all handles this)


def init_db():
    """Create all tables and run migrations"""
    # First create any new tables
    Base.metadata.create_all(bind=engine)
    # Then run column migrations
    run_migrations()

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
