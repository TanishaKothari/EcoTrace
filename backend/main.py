from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
import re
from datetime import datetime
import uvicorn
import logging

from services.ollama_service import OllamaService
from services.product_analyzer import ProductAnalyzer
from services.barcode_service import BarcodeService
from models.eco_score import EcoScoreResponse, ProductAnalysis

logger = logging.getLogger(__name__)

app = FastAPI(title="EcoTrace API", description="AI-powered environmental impact analysis")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ollama_service = OllamaService()
product_analyzer = ProductAnalyzer(ollama_service)
barcode_service = BarcodeService()

class ProductRequest(BaseModel):
    query: str  # Can be product name or URL
    query_type: str = "name"  # "name" or "url"

class BarcodeRequest(BaseModel):
    barcode: str

@app.get("/")
async def root():
    return {"message": "EcoTrace API is running"}

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
async def analyze_product(request: ProductRequest):
    """Analyze a product by name or URL"""
    try:
        if request.query_type == "url":
            analysis = await product_analyzer.analyze_from_url(request.query)
        else:
            analysis = await product_analyzer.analyze_from_name(request.query)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/barcode", response_model=EcoScoreResponse)
async def analyze_barcode(request: BarcodeRequest):
    """Analyze a product by barcode"""
    try:
        # First get product info from barcode
        product_info = await barcode_service.get_product_info(request.barcode)
        
        if not product_info:
            raise HTTPException(status_code=404, detail="Product not found for this barcode")
        
        # Then analyze the product
        analysis = await product_analyzer.analyze_from_product_info(product_info)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode analysis failed: {str(e)}")

@app.post("/analyze/image")
async def analyze_barcode_image(file: UploadFile = File(...)):
    """Analyze a barcode from an uploaded image"""
    try:
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
        return analysis
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
