from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .eco_score import ProductAnalysis, ProductInfo

class AnalysisType(str, Enum):
    """Type of analysis performed"""
    PRODUCT_SEARCH = "product_search"
    BARCODE_SCAN = "barcode_scan"
    URL_ANALYSIS = "url_analysis"
    COMPARISON = "comparison"

class HistoryEntry(BaseModel):
    """Single entry in user's analysis history"""
    id: str = Field(..., description="Unique identifier for this history entry")
    timestamp: datetime = Field(default_factory=datetime.now)
    analysis_type: AnalysisType
    query: str = Field(..., description="Original search query or barcode")
    analysis: ProductAnalysis
    user_session: Optional[str] = None  # For future user tracking
    is_comparison_analysis: bool = False  # Flag to mark analyses done for comparisons
    
class ComparisonHistoryEntry(BaseModel):
    """History entry for product comparisons"""
    id: str = Field(..., description="Unique identifier for this comparison")
    timestamp: datetime = Field(default_factory=datetime.now)
    analysis_type: AnalysisType = AnalysisType.COMPARISON
    products: List[ProductAnalysis] = Field(..., min_items=2, max_items=3)
    comparison_notes: Optional[str] = None
    user_session: Optional[str] = None

class JourneyStats(BaseModel):
    """Statistics about user's eco journey"""
    total_analyses: int = 0
    total_comparisons: int = 0
    average_eco_score: float = 0.0
    best_eco_score: int = 0
    worst_eco_score: int = 100
    favorite_categories: List[str] = []
    improvement_trend: float = 0.0  # Positive = improving, negative = declining
    days_active: int = 0
    first_analysis_date: Optional[datetime] = None
    last_analysis_date: Optional[datetime] = None

class CategoryStats(BaseModel):
    """Statistics for a specific product category"""
    category: str
    count: int
    average_score: float
    best_score: int
    worst_score: int
    trend: float  # Score improvement over time

class TimelineEntry(BaseModel):
    """Entry for timeline visualization"""
    date: datetime
    eco_score: int
    product_name: str
    category: Optional[str] = None
    analysis_type: AnalysisType

class EcoJourney(BaseModel):
    """Complete eco journey data for a user"""
    stats: JourneyStats
    recent_analyses: List[HistoryEntry] = Field(default_factory=list, max_items=10)
    recent_comparisons: List[ComparisonHistoryEntry] = Field(default_factory=list, max_items=5)
    category_breakdown: List[CategoryStats] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)  # Achievement-like milestones

class HistoryFilter(BaseModel):
    """Filter options for history queries"""
    analysis_type: Optional[AnalysisType] = None
    category: Optional[str] = None
    min_eco_score: Optional[int] = Field(None, ge=1, le=100)
    max_eco_score: Optional[int] = Field(None, ge=1, le=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class HistoryResponse(BaseModel):
    """Response for history API calls"""
    success: bool = True
    entries: List[HistoryEntry] = Field(default_factory=list)
    comparisons: List[ComparisonHistoryEntry] = Field(default_factory=list)
    total_count: int = 0
    has_more: bool = False

class JourneyResponse(BaseModel):
    """Response for eco journey API calls"""
    success: bool = True
    journey: EcoJourney
    insights: List[str] = Field(default_factory=list)  # AI-generated insights about progress
