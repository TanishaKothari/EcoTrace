import httpx
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3"
        
    async def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def analyze_environmental_impact(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental impact using Ollama"""

        system_prompt = """You are an expert environmental analyst with deep knowledge of lifecycle assessment (LCA), carbon footprint analysis, and sustainability metrics. Your expertise covers:

- Product lifecycle assessment from cradle to grave
- Carbon footprint calculation and GHG emissions
- Resource efficiency and circular economy principles
- Supply chain sustainability analysis
- Environmental certification standards (ISO 14001, EPEAT, Energy Star, etc.)
- Material science and sustainable alternatives

CRITICAL: You must respond with ONLY a valid JSON object. No additional text before or after.

Required JSON structure:
{
  "eco_score": integer (1-100, where 1=worst environmental impact, 100=most sustainable),
  "impact_factors": [
    {
      "name": "Carbon Footprint",
      "score": integer (1-100),
      "description": "detailed explanation",
      "weight": float (0-1, sum of all weights should equal 1.0)
    },
    // Include 4-6 relevant impact factors
  ],
  "confidence_level": float (0-1),
  "analysis_summary": "comprehensive explanation of the overall score",
  "recommendations": ["specific actionable suggestions"]
}

Scoring Guidelines:
- 90-100: Exceptional sustainability (renewable materials, carbon negative, circular design)
- 80-89: Very good (certified sustainable, low carbon, recyclable)
- 70-79: Good (some sustainable features, moderate impact)
- 60-69: Fair (average impact, some concerns)
- 50-59: Poor (high impact, limited sustainability)
- 40-49: Very poor (significant environmental damage)
- 1-39: Extremely poor (severe environmental impact)

Consider these impact factors (select 4-6 most relevant) - USE EXACT NAMES:
1. Carbon Footprint
2. Resource Usage
3. Manufacturing Process
4. Transportation & Supply Chain
5. Packaging & Waste Generation
6. End-of-Life Management
7. Biodiversity Impact
8. Chemical Usage & Toxicity
9. Social & Ethical Considerations
10. Durability & Longevity

IMPORTANT: Use the exact factor names listed above. Do not add words like "Impact" to the end."""

        prompt = f"""Analyze the environmental impact of this product and provide an EcoScore.

Product Information:
{json.dumps(product_data, indent=2)}

Provide a comprehensive environmental analysis considering:
1. Material composition and sourcing
2. Manufacturing processes and energy use
3. Transportation and distribution
4. Product use phase and durability
5. End-of-life disposal and recyclability
6. Supply chain sustainability
7. Available certifications or standards

Base your analysis on scientific evidence and established LCA methodologies. Be specific about environmental impacts and provide actionable recommendations."""
        
        try:
            response = await self.generate_response(prompt, system_prompt)
            logger.info(f"Ollama response received: {response[:200]}...")

            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                try:
                    parsed_result = json.loads(json_str)
                    logger.info("Successfully parsed JSON from Ollama response")

                    # Validate the required fields
                    required_fields = ['eco_score', 'impact_factors', 'confidence_level', 'analysis_summary', 'recommendations']
                    if all(field in parsed_result for field in required_fields):
                        # Normalize impact factor names
                        parsed_result = self._normalize_impact_factors(parsed_result)
                        return parsed_result
                    else:
                        logger.warning(f"Missing required fields in response: {[f for f in required_fields if f not in parsed_result]}")
                        try:
                            return self._create_fallback_analysis(product_data)
                        except ValueError as ve:
                            logger.error(f"Fallback analysis failed: {ve}")
                            raise ve

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse extracted JSON: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")
                    try:
                        return self._create_fallback_analysis(product_data)
                    except ValueError as ve:
                        logger.error(f"Fallback analysis failed: {ve}")
                        raise ve
            else:
                logger.warning("No valid JSON structure found in response")
                logger.warning(f"Response content: {response[:500]}...")
                try:
                    return self._create_fallback_analysis(product_data)
                except ValueError as ve:
                    logger.error(f"Fallback analysis failed: {ve}")
                    raise ve

        except ValueError:
            # Re-raise validation errors from fallback analysis
            raise
        except Exception as e:
            logger.error(f"Error in environmental analysis: {e}")
            try:
                return self._create_fallback_analysis(product_data)
            except ValueError as ve:
                logger.error(f"Fallback analysis failed: {ve}")
                raise ve

    def _normalize_impact_factors(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize impact factor names to avoid duplicates"""
        if 'impact_factors' not in analysis_result:
            return analysis_result

        # Mapping of variations to standard names
        name_mappings = {
            'carbon footprint & ghg emissions': 'Carbon Footprint',
            'carbon footprint': 'Carbon Footprint',
            'ghg emissions': 'Carbon Footprint',
            'greenhouse gas emissions': 'Carbon Footprint',

            'resource usage (water, energy, raw materials)': 'Resource Usage',
            'resource usage': 'Resource Usage',
            'water usage': 'Resource Usage',
            'energy usage': 'Resource Usage',

            'manufacturing process impact': 'Manufacturing Process',
            'manufacturing impact': 'Manufacturing Process',
            'manufacturing process': 'Manufacturing Process',
            'manufacturing': 'Manufacturing Process',
            'production process': 'Manufacturing Process',
            'production impact': 'Manufacturing Process',

            'transportation & supply chain': 'Transportation & Supply Chain',
            'transportation': 'Transportation & Supply Chain',
            'supply chain': 'Transportation & Supply Chain',
            'logistics': 'Transportation & Supply Chain',

            'packaging & waste generation': 'Packaging & Waste Generation',
            'packaging': 'Packaging & Waste Generation',
            'waste generation': 'Packaging & Waste Generation',

            'end-of-life management': 'End-of-Life Management',
            'end of life': 'End-of-Life Management',
            'disposal': 'End-of-Life Management',
            'recyclability': 'End-of-Life Management',
        }

        normalized_factors = []
        seen_factors = set()

        for factor in analysis_result['impact_factors']:
            original_name = factor['name']
            normalized_name = name_mappings.get(original_name.lower(), original_name)

            # Avoid duplicates
            if normalized_name not in seen_factors:
                factor['name'] = normalized_name
                normalized_factors.append(factor)
                seen_factors.add(normalized_name)
            else:
                # If we have a duplicate, merge the scores (take the average)
                existing_factor = next(f for f in normalized_factors if f['name'] == normalized_name)
                existing_factor['score'] = int((existing_factor['score'] + factor['score']) / 2)
                # Keep the longer description
                if len(factor['description']) > len(existing_factor['description']):
                    existing_factor['description'] = factor['description']

        analysis_result['impact_factors'] = normalized_factors
        return analysis_result

    def _parse_fallback_response(self, response: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        # This is a simplified fallback - in production, you'd want more sophisticated parsing
        return self._create_fallback_analysis(product_data)
    
    def _create_fallback_analysis(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback analysis only for valid products with sufficient data"""
        product_name = (product_data.get('name') or '').strip()
        category = (product_data.get('category') or '').strip()
        brand = (product_data.get('brand') or '').strip()
        materials = product_data.get('materials') or []

        # Check if we have sufficient product data to create a meaningful analysis
        if not product_name or product_name.lower() in ['unknown product', 'unknown', 'generic product']:
            raise ValueError("Insufficient product information for analysis")

        # Check if this looks like a real product (has brand or category or meaningful name)
        has_brand = bool(brand and brand.lower() not in ['unknown', 'generic', ''])
        has_category = bool(category and category.lower() not in ['unknown', 'generic', ''])
        has_meaningful_name = len(product_name.split()) >= 2  # At least 2 words

        if not (has_brand or has_category or has_meaningful_name):
            raise ValueError(f"Could not find reliable product information for '{product_name}'")

        # Only create fallback for products with sufficient data
        product_name_lower = product_name.lower()
        category_lower = category.lower()

        # Category-based scoring (only for recognized categories)
        category_scores = {
            'electronics': 35,  # Generally high impact
            'clothing': 45,     # Varies widely
            'food': 60,         # Can be sustainable
            'personal care': 50, # Mixed impact
            'automotive': 25,   # High impact
            'furniture': 40,    # Depends on materials
            'toys': 45,         # Often plastic
            'books': 70,        # Generally lower impact
            'home': 50,         # Varies
        }

        base_score = 50  # Neutral starting point

        # Apply category-based adjustment
        for cat, score in category_scores.items():
            if cat in category_lower or cat in product_name_lower:
                base_score = score
                break

        # Positive indicators
        positive_keywords = {
            'organic': 15, 'eco': 12, 'sustainable': 15, 'recycled': 12,
            'renewable': 10, 'biodegradable': 15, 'bamboo': 8, 'hemp': 8,
            'solar': 20, 'energy efficient': 15, 'fair trade': 10,
            'carbon neutral': 20, 'zero waste': 18, 'compostable': 15
        }

        # Negative indicators
        negative_keywords = {
            'plastic': -10, 'synthetic': -8, 'petroleum': -15,
            'disposable': -20, 'single use': -25, 'fast fashion': -15,
            'non-recyclable': -18, 'toxic': -20, 'chemical': -8
        }

        # Apply keyword adjustments
        text_to_analyze = f"{product_name} {category} {brand}".lower()

        for keyword, adjustment in positive_keywords.items():
            if keyword in text_to_analyze:
                base_score += adjustment

        for keyword, adjustment in negative_keywords.items():
            if keyword in text_to_analyze:
                base_score += adjustment  # adjustment is negative

        # Material-based adjustments
        if materials:
            for material in materials:
                material_lower = material.lower()
                if any(word in material_lower for word in ['organic', 'recycled', 'sustainable']):
                    base_score += 8
                elif any(word in material_lower for word in ['plastic', 'synthetic', 'petroleum']):
                    base_score -= 6

        # Brand reputation (simplified)
        sustainable_brands = ['patagonia', 'tesla', 'seventh generation', 'method', 'whole foods']
        if any(brand_name in brand for brand_name in sustainable_brands):
            base_score += 10

        eco_score = max(1, min(100, base_score))

        # Generate varied impact factor scores
        carbon_score = max(1, min(100, eco_score + (-5 if 'electronics' in category else 0)))
        resource_score = max(1, min(100, eco_score + (-8 if 'automotive' in category else 3)))
        manufacturing_score = max(1, min(100, eco_score + (-3 if 'fast fashion' in text_to_analyze else 2)))
        eol_score = max(1, min(100, eco_score + (10 if 'recyclable' in text_to_analyze else -5)))

        return {
            "eco_score": eco_score,
            "impact_factors": [
                {
                    "name": "Carbon Footprint",
                    "score": carbon_score,
                    "description": f"Estimated carbon emissions based on product category and materials",
                    "weight": 0.3
                },
                {
                    "name": "Resource Usage",
                    "score": resource_score,
                    "description": "Water, energy, and raw material consumption assessment",
                    "weight": 0.25
                },
                {
                    "name": "Manufacturing Process",
                    "score": manufacturing_score,
                    "description": "Environmental impact of production processes",
                    "weight": 0.25
                },
                {
                    "name": "End-of-Life Management",
                    "score": eol_score,
                    "description": "Disposal, recycling, and waste management considerations",
                    "weight": 0.2
                }
            ],
            "confidence_level": 0.4,
            "analysis_summary": f"Heuristic analysis for {product_data.get('name', 'Unknown Product')}. Score based on product category, materials, and sustainability indicators. Limited data available for comprehensive LCA assessment.",
            "recommendations": self._generate_recommendations(eco_score, category, text_to_analyze)
        }

    def _generate_recommendations(self, score: int, category: str, product_text: str) -> list:
        """Generate contextual recommendations based on score and product type"""
        recommendations = []

        if score < 40:
            recommendations.extend([
                "Consider switching to a more sustainable alternative",
                "Look for products with environmental certifications",
                "Research the manufacturer's sustainability practices"
            ])
        elif score < 60:
            recommendations.extend([
                "Look for improved versions with better sustainability features",
                "Consider the product's durability and longevity",
                "Check for recycling programs in your area"
            ])
        else:
            recommendations.extend([
                "This appears to be a relatively sustainable choice",
                "Ensure proper disposal or recycling at end of life",
                "Consider supporting brands with strong environmental commitments"
            ])

        # Category-specific recommendations
        if 'electronics' in category:
            recommendations.append("Look for EPEAT or Energy Star certifications")
            recommendations.append("Consider refurbished or repairable options")
        elif 'clothing' in category:
            recommendations.append("Choose quality items that will last longer")
            recommendations.append("Look for organic or recycled materials")
        elif 'food' in category:
            recommendations.append("Consider local and seasonal options")
            recommendations.append("Look for organic or sustainably sourced products")

        return recommendations[:4]  # Limit to 4 recommendations
