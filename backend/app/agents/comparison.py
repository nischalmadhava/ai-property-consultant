from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import re
from app.config import settings
from .context import SearchContext, AgentType

class ComparisonAgent:
    """
    Compares and analyzes properties based on multiple factors
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3,
            api_key=settings.openai_api_key
        )
    
    async def compare_and_score(self, context: SearchContext) -> SearchContext:
        """
        Compare properties and generate recommendations
        """
        
        try:
            if not context.properties:
                context.add_workflow_step(
                    AgentType.COMPARISON,
                    "info",
                    {"message": "No properties to compare"}
                )
                return context
            
            # Score each property
            scored_properties = self._score_properties(context.properties)
            
            # Sort by score (descending)
            scored_properties.sort(key=lambda x: x.get("total_score", 0), reverse=True)
            
            context.recommendations = scored_properties[:5]  # Top 5
            
            context.add_workflow_step(
                AgentType.COMPARISON,
                "success",
                {
                    "properties_compared": len(context.properties),
                    "recommendations_generated": len(context.recommendations),
                    "scoring_factors": ["price", "location", "amenities", "rera_status"]
                }
            )
            
        except Exception as e:
            context.add_workflow_step(
                AgentType.COMPARISON,
                "failed",
                {"properties_count": len(context.properties)},
                str(e)
            )
        
        return context
    
    def _score_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score properties based on multiple factors
        """
        
        scored = []
        
        # Find min/max for normalization
        prices = [p.get("price", 0) for p in properties if p.get("price")]
        areas = [p.get("area", 0) for p in properties if p.get("area")]
        
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 1
        min_area = min(areas) if areas else 0
        max_area = max(areas) if areas else 1
        
        for prop in properties:
            scores = {}
            
            # Price score (lower is better, 0-30 points)
            price = prop.get("price", max_price)
            price_score = 30 * (1 - (price - min_price) / (max_price - min_price or 1))
            scores["price_score"] = round(price_score, 2)
            
            # Area score (optimal size, 0-25 points)
            area = prop.get("area", 0)
            # Assuming optimal size is around 1200 sqft (30x40)
            optimal_area = 1200
            if area > 0:
                area_diff = abs(area - optimal_area)
                area_score = 25 * (1 - (area_diff / (optimal_area + area_diff)))
            else:
                area_score = 0
            scores["area_score"] = round(area_score, 2)
            
            # RERA score (0-20 points)
            rera_score = 20 if prop.get("rera_registered") else 10
            scores["rera_score"] = rera_score
            
            # Amenities score (0-15 points)
            amenities = prop.get("amenities", [])
            amenities_score = min(15, len(amenities) * 3)
            scores["amenities_score"] = amenities_score
            
            # Developer reputation (0-10 points - placeholder)
            dev_score = 8
            scores["developer_score"] = dev_score
            
            total_score = sum(scores.values())
            
            scored.append({
                **prop,
                "scores": scores,
                "total_score": round(total_score, 2)
            })
        
        return scored
