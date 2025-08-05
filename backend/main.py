from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
import re
from datetime import datetime
import uvicorn
import logging

from database import create_tables
from services.ollama_service import OllamaService
from services.product_analyzer import ProductAnalyzer
from services.barcode_service import BarcodeService
from services.database_history_service import database_history_service
from services.auth_service import auth_service
from utils.security import generate_secure_anonymous_token, validate_token
from models.auth import RegisterRequest, LoginRequest, AuthResponse, UserInfo, TokenValidationResponse
from models.eco_score import EcoScoreResponse, ProductAnalysis
from models.history import (
    HistoryFilter, HistoryResponse, JourneyResponse,
    AnalysisType, HistoryEntry, ComparisonHistoryEntry
)

logger = logging.getLogger(__name__)

app = FastAPI(title="EcoTrace API", description="AI-powered environmental impact analysis")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
create_tables()

# Initialize services
ollama_service = OllamaService()
product_analyzer = ProductAnalyzer(ollama_service)
barcode_service = BarcodeService()

class ProductRequest(BaseModel):
    query: str  # Can be product name or URL
    query_type: str = "name"  # "name" or "url"
    is_comparison_analysis: bool = False  # Flag to mark analyses done for comparisons

class BarcodeRequest(BaseModel):
    barcode: str

def get_user_token(x_user_token: Optional[str] = Header(None)) -> str:
    """Get user token from header or generate new secure anonymous token"""
    if x_user_token and validate_token(x_user_token):
        return x_user_token
    # Generate new secure anonymous token
    return generate_secure_anonymous_token()

@app.get("/")
async def root():
    return {"message": "EcoTrace API is running"}

@app.post("/auth/token")
async def generate_anonymous_token():
    """Generate a secure anonymous user token"""
    try:
        token = generate_secure_anonymous_token()
        return {"success": True, "token": token}
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate token")

@app.post("/auth/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """Register a new user account"""
    try:
        success, message, token = auth_service.register_user(
            email=request.email,
            password=request.password,
            name=request.name
        )

        user_info = None
        if success and token:
            user = auth_service.get_user_by_token(token)
            if user:
                user_info = UserInfo(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_anonymous=user.is_anonymous,
                    created_at=user.created_at.isoformat(),
                    email_verified=user.email_verified
                )

        return AuthResponse(
            success=success,
            message=message,
            token=token,
            user=user_info
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """Login user and return auth token"""
    try:
        success, message, token = auth_service.login_user(
            email=request.email,
            password=request.password
        )

        user_info = None
        if success and token:
            user = auth_service.get_user_by_token(token)
            if user:
                user_info = UserInfo(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_anonymous=user.is_anonymous,
                    created_at=user.created_at.isoformat(),
                    email_verified=user.email_verified
                )

        return AuthResponse(
            success=success,
            message=message,
            token=token,
            user=user_info
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/auth/validate", response_model=TokenValidationResponse)
async def validate_token_endpoint(user_token: str = Header(None, alias="x-user-token")):
    """Validate user token and return user info"""
    try:
        if not user_token:
            return TokenValidationResponse(valid=False)

        user = auth_service.get_user_by_token(user_token)
        if not user:
            return TokenValidationResponse(valid=False)

        user_info = UserInfo(
            id=user.id,
            email=user.email or "",
            name=user.name,
            is_anonymous=user.is_anonymous,
            created_at=user.created_at.isoformat(),
            email_verified=user.email_verified if hasattr(user, 'email_verified') else False
        )

        return TokenValidationResponse(
            valid=True,
            user=user_info,
            is_authenticated=not user.is_anonymous
        )
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return TokenValidationResponse(valid=False)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        ollama_status = await ollama_service.test_connection()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ollama": "connected" if ollama_status else "disconnected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/analyze/product", response_model=EcoScoreResponse)
async def analyze_product(request: ProductRequest, user_token: str = Header(None, alias="x-user-token")):
    """Analyze a product by name or URL"""
    logger.info(f"Starting product analysis for query: {request.query}")
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()

        if request.query_type == "url":
            analysis = await product_analyzer.analyze_from_url(request.query)
            analysis_type = AnalysisType.URL_ANALYSIS
        else:
            analysis = await product_analyzer.analyze_from_name(request.query)
            analysis_type = AnalysisType.PRODUCT_SEARCH

        # Save to history using database service
        try:
            database_history_service.save_analysis(
                user_token=user_token,
                query=request.query,
                analysis=analysis.analysis,
                analysis_type=analysis_type,
                is_comparison_analysis=request.is_comparison_analysis
            )
        except Exception as e:
            logger.error(f"Failed to save analysis to history: {e}")
            # Don't fail the request if history saving fails

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/barcode", response_model=EcoScoreResponse)
async def analyze_barcode(request: BarcodeRequest, user_token: str = Header(None, alias="x-user-token")):
    """Analyze a product by barcode"""
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()
        # First get product info from barcode
        product_info = await barcode_service.get_product_info(request.barcode)

        if not product_info:
            raise HTTPException(status_code=404, detail="Product not found for this barcode")

        # Then analyze the product
        analysis = await product_analyzer.analyze_from_product_info(product_info)

        # Save to history using database service
        database_history_service.save_analysis(
            user_token=user_token,
            query=request.barcode,
            analysis=analysis.analysis,
            analysis_type=AnalysisType.BARCODE_SCAN,
            is_comparison_analysis=False
        )

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode analysis failed: {str(e)}")

@app.post("/analyze/image")
async def analyze_barcode_image(file: UploadFile = File(...), user_token: str = Header(None, alias="x-user-token")):
    """Analyze a barcode from an uploaded image"""
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()
        # Read the uploaded file
        contents = await file.read()
        logger.info(f"Received image file: {file.filename}, size: {len(contents)} bytes")

        # Extract barcode from image
        barcode = await barcode_service.extract_barcode_from_image(contents)
        logger.info(f"Extracted barcode: {barcode}")

        if not barcode:
            raise HTTPException(status_code=400, detail="No barcode found in image")

        # Get product info and analyze
        product_info = await barcode_service.get_product_info(barcode)
        logger.info(f"Product info retrieved: {product_info is not None}")

        if not product_info:
            # Don't create fake analyses for unknown barcodes
            logger.info(f"No product found for barcode {barcode}")
            raise HTTPException(
                status_code=404,
                detail=f"No product found for barcode {barcode}. Please verify the barcode is correct and try again."
            )

        analysis = await product_analyzer.analyze_from_product_info(product_info)

        # Save to history using database service
        database_history_service.save_analysis(
            user_token=user_token,
            query=barcode,
            analysis=analysis.analysis,
            analysis_type=AnalysisType.BARCODE_SCAN,
            is_comparison_analysis=False
        )

        return analysis
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

# History and Journey Endpoints

@app.get("/history", response_model=HistoryResponse)
async def get_analysis_history(
    analysis_type: Optional[str] = None,
    category: Optional[str] = None,
    min_eco_score: Optional[int] = None,
    max_eco_score: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    user_token: str = Header(None, alias="x-user-token")
):
    """Get analysis history with optional filters"""
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()

        # Convert string to enum if provided
        analysis_type_enum = None
        if analysis_type:
            try:
                analysis_type_enum = AnalysisType(analysis_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid analysis_type: {analysis_type}")

        filter_options = HistoryFilter(
            analysis_type=analysis_type_enum,
            category=category,
            min_eco_score=min_eco_score,
            max_eco_score=max_eco_score,
            limit=limit,
            offset=offset
        )

        return database_history_service.get_history(user_token, filter_options)
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/journey", response_model=JourneyResponse)
async def get_eco_journey(user_token: str = Header(None, alias="x-user-token")):
    """Get comprehensive eco journey data and insights"""
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()

        return database_history_service.get_journey(user_token)
    except Exception as e:
        logger.error(f"Error getting eco journey: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get eco journey: {str(e)}")

class ComparisonRequest(BaseModel):
    products: list[ProductAnalysis]
    notes: Optional[str] = None

@app.post("/history/comparison")
async def save_comparison(request: ComparisonRequest, user_token: str = Header(None, alias="x-user-token")):
    """Save a product comparison to history"""
    try:
        # Get or generate user token
        if not user_token or not validate_token(user_token):
            user_token = generate_secure_anonymous_token()

        if len(request.products) < 2:
            raise HTTPException(status_code=400, detail="Comparison must include at least 2 products")

        comparison_id = database_history_service.save_comparison(
            user_token=user_token,
            products=request.products,
            notes=request.notes
        )

        return {"success": True, "comparison_id": comparison_id}
    except Exception as e:
        logger.error(f"Error saving comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save comparison: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
