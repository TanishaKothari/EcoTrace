"""
Database package for EcoTrace
"""

from .database import engine, SessionLocal, create_tables, get_db, get_db_session
from .models import Base, User, HistoryEntry, ComparisonEntry

__all__ = [
    "engine",
    "SessionLocal", 
    "create_tables",
    "get_db",
    "get_db_session",
    "Base",
    "User",
    "HistoryEntry", 
    "ComparisonEntry"
]
