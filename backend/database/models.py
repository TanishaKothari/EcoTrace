"""
Database models for EcoTrace application
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for anonymous and authenticated users"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Will be hashed token
    token_hash = Column(String, nullable=False, unique=True)  # Hashed version of token
    is_anonymous = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # For Phase 2 (authenticated accounts)
    email = Column(String, nullable=True, unique=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    history_entries = relationship("HistoryEntry", back_populates="user", cascade="all, delete-orphan")
    comparison_entries = relationship("ComparisonEntry", back_populates="user", cascade="all, delete-orphan")

class HistoryEntry(Base):
    """Individual analysis history entry"""
    __tablename__ = "history_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    analysis_type = Column(String, nullable=False)  # product_search, barcode_scan, etc.
    query = Column(String, nullable=False)
    analysis = Column(JSON, nullable=False)  # Full ProductAnalysis object
    is_comparison_analysis = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="history_entries")

class ComparisonEntry(Base):
    """Product comparison history entry"""
    __tablename__ = "comparison_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    products = Column(JSON, nullable=False)  # List of ProductAnalysis objects
    comparison_notes = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="comparison_entries")
