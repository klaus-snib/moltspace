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
    
    This runs BEFORE create_all to ensure columns exist for ORM queries.
    """
    from sqlalchemy import text
    
    # Migration: Add voice_intro_url column to agents table
    # Just try the ALTER - if it fails (column exists, table doesn't exist, etc), ignore
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE agents ADD COLUMN voice_intro_url VARCHAR(500)"))
            conn.commit()
            print("✅ Migration: Added voice_intro_url column")
        except Exception as e:
            # Expected errors: column already exists, table doesn't exist
            # Both are fine - we just move on
            try:
                conn.rollback()
            except:
                pass  # Connection might be in auto-commit mode
            error_str = str(e).lower()
            if "already exists" in error_str or "duplicate" in error_str:
                pass  # Column exists, good
            elif "does not exist" in error_str or "no such table" in error_str:
                pass  # Table doesn't exist, create_all will handle it
            else:
                print(f"ℹ️ Migration note (voice_intro_url): {e}")


def init_db():
    """Create all tables and run migrations"""
    # Run column migrations FIRST (before ORM tries to use new columns)
    # This ensures existing tables get new columns before create_all
    run_migrations()
    # Then create any new tables (this won't modify existing tables)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
