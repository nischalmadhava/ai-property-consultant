from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import re
from app.config import settings
from .context import SearchContext, AgentType

class RecommendationAgent:
    """
    Generates final recommendations with detailed reasoning
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.5,
            api_key=settings.openai_api_key
        )
    
    async def generate_recommendations(self, context: SearchContext) -> SearchContext:
        """
        Generate final recommendations with reasoning
        """
        
        try:
            if not context.recommendations:
                context.reasoning = "No properties found matching your criteria."
                context.add_workflow_step(
                    AgentType.RECOMMENDATION,
                    "info",
                    {"message": "No recommendations available"}
                )
                return context
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(context)
            context.reasoning = reasoning
            
            context.add_workflow_step(
                AgentType.RECOMMENDATION,
                "success",
                {
                    "recommendations_count": len(context.recommendations),
                    "top_recommendation": context.recommendations[0].get("name") if context.recommendations else None
                }
            )
            
        except Exception as e:
            context.add_workflow_step(
                AgentType.RECOMMENDATION,
                "failed",
                {"recommendations_count": len(context.recommendations)},
                str(e)
            )
        
        return context
    
    async def _generate_reasoning(self, context: SearchContext) -> str:
        """
        Generate LLM-based reasoning for recommendations
        """
        
        try:
            # Format recommendations for LLM
            recommendations_text = "\n".join([
                f"- {r.get('name')}: ₹{r.get('price'):,.0f}, {r.get('area')} sqft, "
                f"Developer: {r.get('developer')}, Score: {r.get('total_score')}"
                for r in context.recommendations[:5]
            ])
            
            prompt = ChatPromptTemplate.from_template("""
            Based on the following property recommendations, provide a concise recommendation summary.
            
            User Criteria:
            - Location: {location}
            - Size: {min_size} - {max_size} sqft
            - Budget: ₹{min_price:,.0f} - ₹{max_price:,.0f}
            - Requirements: {additional_requirements}
            
            Top Recommendations:
            {recommendations}
            
            Provide a brief (2-3 sentences) recommendation summary explaining why these properties are suitable.
            """)
            
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "location": context.location or "Not specified",
                "min_size": context.min_size or 0,
                "max_size": context.max_size or "No limit",
                "min_price": context.min_price or 0,
                "max_price": context.max_price or float('inf'),
                "additional_requirements": context.additional_requirements or "None",
                "recommendations": recommendations_text
            })
            
            return response.content
            
        except Exception as e:
            return f"Based on your criteria, we found {len(context.recommendations)} matching properties. Please review the details above for more information."
