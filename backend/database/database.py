"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from dotenv import load_dotenv
import os
from .models import Base

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """Get database session for direct use"""
    return SessionLocal()
