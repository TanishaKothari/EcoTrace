import httpx
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class BarcodeService:
    """Service for handling barcode scanning and product lookup"""
    
    def __init__(self):
        # Multiple product databases for comprehensive coverage
        self.openfoodfacts_base = "https://world.openfoodfacts.org/api/v0/product"  # Food products
        self.upcitemdb_base = "https://api.upcitemdb.com/prod/trial/lookup"  # General products
        self.barcodelookup_base = "https://www.barcodelookup.com"  # General products (backup)
        
    async def extract_barcode_from_image(self, image_data: bytes) -> Optional[str]:
        """Extract barcode from image data"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Decode barcodes
            barcodes = pyzbar.decode(cv_image)
            
            if barcodes:
                # Return the first barcode found
                return barcodes[0].data.decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting barcode from image: {e}")
            return None
    
    def _validate_barcode(self, barcode: str) -> bool:
        """Validate if the barcode format is correct"""
        # Remove any whitespace
        barcode = barcode.strip()

        # Check if it contains only digits
        if not barcode.isdigit():
            return False

        # Check common barcode lengths
        valid_lengths = [8, 12, 13, 14]  # UPC-A, EAN-8, EAN-13, ITF-14
        if len(barcode) not in valid_lengths:
            return False

        return True

    async def get_product_info(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product information from barcode"""
        try:
            # Validate barcode format
            if not self._validate_barcode(barcode):
                logger.warning(f"Invalid barcode format: {barcode}")
                return None

            logger.info(f"Looking up barcode: {barcode}")

            # Try multiple databases in order of preference
            # 1. Try UPCItemDB first (general products, free tier)
            product_info = await self._get_from_upcitemdb(barcode)
            if product_info:
                logger.info(f"Found product in UPCItemDB: {product_info.get('name', 'Unknown')}")
                return product_info

            # 2. Try OpenFoodFacts (food products)
            product_info = await self._get_from_openfoodfacts(barcode)
            if product_info:
                logger.info(f"Found product in OpenFoodFacts: {product_info.get('name', 'Unknown')}")
                return product_info

            # No more fallbacks - if not found in real databases, return None

            # If no product found, return None (will trigger generic analysis)
            logger.info(f"No product found for barcode: {barcode}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting product info for barcode {barcode}: {e}")
            return None

    async def _get_from_upcitemdb(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product info from UPCItemDB API (general products)"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.upcitemdb_base}?upc={barcode}")

                if response.status_code == 200:
                    data = response.json()

                    if data.get("code") == "OK" and data.get("items"):
                        item = data["items"][0]  # Get first result

                        return {
                            "name": item.get("title", "Unknown Product"),
                            "brand": item.get("brand", ""),
                            "category": item.get("category", ""),
                            "description": item.get("description", ""),
                            "barcode": barcode,
                            "source": "UPCItemDB"
                        }

        except Exception as e:
            logger.error(f"Error fetching from UPCItemDB: {e}")

        return None

    async def _get_from_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product info from OpenFoodFacts API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.openfoodfacts_base}/{barcode}.json")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == 1 and 'product' in data:
                        product = data['product']
                        
                        # Extract relevant information
                        return {
                            "name": product.get('product_name', f'Product {barcode}'),
                            "brand": product.get('brands'),
                            "category": product.get('categories'),
                            "description": product.get('generic_name') or product.get('product_name'),
                            "ingredients": product.get('ingredients_text'),
                            "materials": self._extract_materials_from_ingredients(product.get('ingredients_text')),
                            "origin_country": product.get('countries'),
                            "packaging": product.get('packaging'),
                            "certifications": self._extract_certifications(product),
                            "nutrition_grade": product.get('nutrition_grade_fr'),
                            "eco_score": product.get('ecoscore_score'),
                            "barcode": barcode,
                            "image_url": product.get('image_url')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching from OpenFoodFacts: {e}")
            return None



    def _extract_materials_from_ingredients(self, ingredients_text: Optional[str]) -> Optional[List[str]]:
        """Extract material information from ingredients"""
        if not ingredients_text:
            return None
        
        # Basic material extraction - could be enhanced
        materials = []
        ingredients_lower = ingredients_text.lower()
        
        # Common materials/ingredients that indicate environmental impact
        material_keywords = {
            'plastic': ['plastic', 'polyethylene', 'polypropylene', 'pet'],
            'organic': ['organic', 'bio'],
            'recycled': ['recycled', 'recyclable'],
            'palm oil': ['palm oil', 'palm kernel'],
            'synthetic': ['artificial', 'synthetic']
        }
        
        for material, keywords in material_keywords.items():
            if any(keyword in ingredients_lower for keyword in keywords):
                materials.append(material)
        
        return materials if materials else None
    
    def _extract_certifications(self, product: Dict[str, Any]) -> Optional[List[str]]:
        """Extract certifications from product data"""
        certifications = []
        
        # Check various certification fields
        cert_fields = ['labels', 'certifications', 'quality_tags']
        
        for field in cert_fields:
            if field in product and product[field]:
                if isinstance(product[field], str):
                    certifications.extend(product[field].split(','))
                elif isinstance(product[field], list):
                    certifications.extend(product[field])
        
        # Clean up certifications
        cleaned_certs = []
        for cert in certifications:
            if isinstance(cert, str):
                cert = cert.strip()
                if cert and len(cert) > 2:  # Filter out very short strings
                    cleaned_certs.append(cert)
        
        return cleaned_certs if cleaned_certs else None
