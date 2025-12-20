from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ImpactFactor(BaseModel):
    """Individual impact factor with score and description"""
    name: str
    score: int = Field(..., ge=1, le=100, description="Score from 1-100")
    description: str
    weight: float = Field(..., ge=0, le=1, description="Weight in overall score calculation")

class ProductInfo(BaseModel):
    """Basic product information"""
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    materials: Optional[List[str]] = None
    origin_country: Optional[str] = None
    manufacturing_process: Optional[str] = None
    packaging: Optional[str] = None
    certifications: Optional[List[str]] = None

class ProductAnalysis(BaseModel):
    """Detailed analysis of a product's environmental impact"""
    product_info: ProductInfo
    impact_factors: List[ImpactFactor]
    eco_score: int = Field(..., ge=1, le=100, description="Overall EcoScore from 1-100")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis")
    analysis_summary: str
    recommendations: List[str]
    data_sources: List[str]

class EcoScoreResponse(BaseModel):
    """API response for EcoScore analysis"""
    success: bool = True
    analysis: ProductAnalysis
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[int] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)
