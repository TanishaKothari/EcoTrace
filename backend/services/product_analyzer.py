import httpx
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from datetime import datetime

from models.eco_score import ProductAnalysis, ProductInfo, ImpactFactor, EcoScoreResponse
from services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

class ProductAnalyzer:
    """Service for analyzing products and generating EcoScores"""
    
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service
        
    def _validate_product_name(self, product_name: str) -> bool:
        """Validate if the product name seems legitimate"""
        if not product_name:
            return False

        name = product_name.strip().lower()
        original_name = product_name.strip()

        # Check minimum length
        if len(name) < 2:
            return False

        # Check for random/nonsensical patterns (more than 5 repeating chars)

        # Check for excessive repeating characters (6+ same chars)
        if re.search(r'(.)\1{5,}', name):
            return False

        # Check if it's all the same character
        if len(set(name.replace(' ', ''))) <= 1:
            return False

        # Check for obvious keyboard mashing (entire rows)
        keyboard_rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        clean_name = name.replace(' ', '')
        for row in keyboard_rows:
            if len(clean_name) >= 6 and clean_name in row:
                return False

        # Check for random uppercase/lowercase patterns that suggest keyboard mashing
        if len(clean_name) >= 6:
            # Count case changes - random mashing often has many case changes
            case_changes = 0
            for i in range(1, len(original_name)):
                if original_name[i-1].islower() != original_name[i].islower():
                    case_changes += 1
            # If more than 50% of characters involve case changes, likely random
            case_change_ratio = case_changes / len(original_name) if len(original_name) > 0 else 0
            if case_change_ratio > 0.5:
                return False

        # Check for patterns that look like random keyboard mashing
        # Look for sequences that don't form recognizable patterns
        if len(clean_name) >= 8:
            # Check if it contains common letter patterns found in real words
            common_patterns = [
                'ing', 'tion', 'er', 'ed', 'ly', 'est', 'ness', 'ment', 'ful', 'less',
                'th', 'he', 'in', 'er', 'an', 're', 'nd', 'on', 'en', 'at', 'ou', 'it',
                'is', 'or', 'ti', 'as', 'to', 'le', 'sa', 'ar', 'se', 'te', 'al'
            ]
            has_common_pattern = any(pattern in clean_name for pattern in common_patterns)

            # If it's long and has no common patterns, likely random
            if not has_common_pattern and len(clean_name) >= 8:
                return False

        # Check for very long consonant clusters (7+ consecutive consonants)
        if re.search(r'[bcdfghjklmnpqrstvwxyz]{7,}', name):
            return False

        # Check for very short nonsense words
        words = name.split()
        if len(words) == 1 and len(words[0]) < 3 and not any(char.isdigit() for char in words[0]):
            # Allow common short brand/product names
            common_short_names = [
                'tv', 'pc', 'ac', 'mac', 'ipad', 'ps5', 'xbox', 'cpu', 'gpu', 'ssd', 'ram',
                'bmw', 'vw', 'lg', 'hp', 'ge', 'lg', 'jbl', '3m'
            ]
            if words[0] not in common_short_names:
                return False

        # Only flag extreme consonant-to-vowel ratios (more than 6:1)
        consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]', name))
        vowels = len(re.findall(r'[aeiou]', name))
        if vowels > 0 and consonants / vowels > 6:
            return False

        # Additional check for specific nonsense patterns
        # Only reject if it's clearly random keyboard mashing with excessive case changes
        if len(original_name) >= 8:
            # Check for patterns like "dASDSADCSA" - alternating or random case with no clear word structure
            has_mixed_case = any(c.isupper() for c in original_name) and any(c.islower() for c in original_name)
            if has_mixed_case:
                # Only reject if it has excessive case changes AND no spaces (indicating random mashing)
                # Real product names like "Tesla Model Y" have spaces and reasonable case patterns
                if ' ' not in original_name:
                    # Count case changes for single words with mixed case
                    case_changes = 0
                    for i in range(1, len(original_name)):
                        if original_name[i-1].islower() != original_name[i].islower():
                            case_changes += 1
                    # Only reject if more than 70% of characters involve case changes (very random)
                    if case_changes / len(original_name) > 0.7:
                        return False

        return True

    async def analyze_from_name(self, product_name: str) -> EcoScoreResponse:
        """Analyze a product by name"""
        start_time = datetime.now()

        try:
            # Validate product name
            if not self._validate_product_name(product_name):
                raise ValueError("Invalid product name. Please enter a valid product name.")

            # Create basic product info from name
            product_info = ProductInfo(
                name=product_name,
                description=f"Product analysis for: {product_name}"
            )
            
            # Enhance with web search if possible
            enhanced_info = await self._enhance_product_info(product_info)
            
            # Perform AI analysis
            analysis_data = await self.ollama_service.analyze_environmental_impact({
                "name": enhanced_info.name,
                "brand": enhanced_info.brand,
                "category": enhanced_info.category,
                "description": enhanced_info.description,
                "materials": enhanced_info.materials,
                "origin_country": enhanced_info.origin_country,
                "manufacturing_process": enhanced_info.manufacturing_process,
                "packaging": enhanced_info.packaging,
                "certifications": enhanced_info.certifications
            })
            
            # Convert to our models
            analysis = self._create_analysis_from_ai_response(enhanced_info, analysis_data)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return EcoScoreResponse(
                analysis=analysis,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing product by name: {e}")
            raise
    
    async def analyze_from_url(self, url: str) -> EcoScoreResponse:
        """Analyze a product from a URL"""
        start_time = datetime.now()
        
        try:
            # Scrape product information from URL
            product_info = await self._scrape_product_from_url(url)
            
            # Perform AI analysis
            analysis_data = await self.ollama_service.analyze_environmental_impact({
                "name": product_info.name,
                "brand": product_info.brand,
                "category": product_info.category,
                "description": product_info.description,
                "materials": product_info.materials,
                "origin_country": product_info.origin_country,
                "manufacturing_process": product_info.manufacturing_process,
                "packaging": product_info.packaging,
                "certifications": product_info.certifications
            })
            
            # Convert to our models
            analysis = self._create_analysis_from_ai_response(product_info, analysis_data)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return EcoScoreResponse(
                analysis=analysis,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing product from URL: {e}")
            raise
    
    async def analyze_from_product_info(self, product_info: Dict[str, Any]) -> EcoScoreResponse:
        """Analyze a product from existing product information (e.g., from barcode)"""
        start_time = datetime.now()
        
        try:
            # Convert dict to ProductInfo model
            info = ProductInfo(
                name=product_info.get('name', 'Unknown Product'),
                brand=product_info.get('brand'),
                category=product_info.get('category'),
                description=product_info.get('description'),
                materials=product_info.get('materials'),
                origin_country=product_info.get('origin_country'),
                manufacturing_process=product_info.get('manufacturing_process'),
                packaging=product_info.get('packaging'),
                certifications=product_info.get('certifications')
            )
            
            # Perform AI analysis
            analysis_data = await self.ollama_service.analyze_environmental_impact(product_info)
            
            # Convert to our models
            analysis = self._create_analysis_from_ai_response(info, analysis_data)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return EcoScoreResponse(
                analysis=analysis,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing product from info: {e}")
            raise
    
    async def _enhance_product_info(self, product_info: ProductInfo) -> ProductInfo:
        """Enhance product info with additional data from web search"""
        try:
            # Simple enhancement - in production, you might use product databases
            enhanced = product_info.copy()
            
            # Basic category inference from product name
            name_lower = product_info.name.lower()
            if any(word in name_lower for word in ['shirt', 'pants', 'dress', 'clothing']):
                enhanced.category = 'Clothing'
            elif any(word in name_lower for word in ['phone', 'laptop', 'computer', 'electronic']):
                enhanced.category = 'Electronics'
            elif any(word in name_lower for word in ['food', 'snack', 'drink', 'beverage']):
                enhanced.category = 'Food & Beverage'
            elif any(word in name_lower for word in ['shampoo', 'soap', 'cosmetic', 'beauty']):
                enhanced.category = 'Personal Care'
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing product info: {e}")
            return product_info
    
    async def _scrape_product_from_url(self, url: str) -> ProductInfo:
        """Scrape product information from a URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch URL: {response.status_code}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract product information using common selectors
                name = self._extract_product_name(soup)
                brand = self._extract_brand(soup)
                description = self._extract_description(soup)
                
                return ProductInfo(
                    name=name or "Unknown Product",
                    brand=brand,
                    description=description
                )
                
        except Exception as e:
            logger.error(f"Error scraping product from URL: {e}")
            # Return basic info if scraping fails
            return ProductInfo(name=f"Product from {urlparse(url).netloc}")
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product name from HTML"""
        selectors = [
            'h1[data-testid="product-title"]',
            'h1.product-title',
            'h1#product-title',
            '.product-name h1',
            'h1',
            '[data-testid="product-name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand from HTML"""
        selectors = [
            '[data-testid="brand"]',
            '.brand',
            '.product-brand',
            '[itemprop="brand"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from HTML"""
        selectors = [
            '[data-testid="product-description"]',
            '.product-description',
            '.description',
            '[itemprop="description"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:500]  # Limit length
        
        return None
    
    def _create_analysis_from_ai_response(self, product_info: ProductInfo, ai_data: Dict[str, Any]) -> ProductAnalysis:
        """Convert AI response to ProductAnalysis model"""
        try:
            logger.info(f"Processing AI response: {ai_data}")

            # Extract impact factors
            impact_factors = []
            for factor_data in ai_data.get('impact_factors', []):
                impact_factors.append(ImpactFactor(
                    name=factor_data['name'],
                    score=factor_data['score'],
                    description=factor_data['description'],
                    weight=factor_data['weight']
                ))

            logger.info(f"Successfully processed {len(impact_factors)} impact factors")

            return ProductAnalysis(
                product_info=product_info,
                impact_factors=impact_factors,
                eco_score=ai_data.get('eco_score', 50),
                confidence_level=ai_data.get('confidence_level', 0.5),
                analysis_summary=ai_data.get('analysis_summary', 'Environmental impact analysis completed'),
                recommendations=ai_data.get('recommendations', []),
                data_sources=['AI Analysis', 'Product Information']
            )

        except Exception as e:
            logger.error(f"Error creating analysis from AI response: {e}")
            logger.error(f"AI data structure: {ai_data}")
            # Return fallback analysis
            return ProductAnalysis(
                product_info=product_info,
                impact_factors=[
                    ImpactFactor(
                        name="Overall Impact",
                        score=50,
                        description="Basic environmental assessment",
                        weight=1.0
                    )
                ],
                eco_score=50,
                confidence_level=0.3,
                analysis_summary="Basic analysis - limited data available",
                recommendations=["Consider more sustainable alternatives"],
                data_sources=['Basic Analysis']
            )
