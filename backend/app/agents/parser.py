import re
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings
from .context import SearchContext, AgentType

class ParserAgent:
    """
    Parses user's natural language input to extract structured search criteria
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0,
            api_key=settings.openai_api_key
        )
    
    async def parse(self, context: SearchContext) -> SearchContext:
        """Parse user's natural language query"""
        
        try:
            prompt = ChatPromptTemplate.from_template("""
            Extract structured property search criteria from the user's query.
            
            User Query: {query}
            
            Extract and provide the following in JSON format:
            {{
                "location": "specific location name if mentioned",
                "division": "North/South/East/West if determinable",
                "min_size": "minimum plot size in sq ft (integer) or null",
                "max_size": "maximum plot size in sq ft (integer) or null",
                "min_price": "minimum price in rupees (float) or null",
                "max_price": "maximum price in rupees (float) or null",
                "property_type": "plot/apartment/villa/commercial or null",
                "additional_requirements": "any other requirements mentioned as string"
            }}
            
            Only return valid JSON, no other text.
            """)
            
            chain = prompt | self.llm
            response = await chain.ainvoke({"query": context.original_query})
            
            # Parse the LLM response
            import json
            json_str = response.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                criteria = json.loads(json_match.group())
                
                # Update context with parsed values
                context.location = criteria.get("location")
                context.division = criteria.get("division")
                context.min_size = criteria.get("min_size")
                context.max_size = criteria.get("max_size")
                context.min_price = criteria.get("min_price")
                context.max_price = criteria.get("max_price")
                context.property_type = criteria.get("property_type")
                context.additional_requirements = criteria.get("additional_requirements")
                
                context.add_workflow_step(
                    AgentType.PARSER,
                    "success",
                    {
                        "parsed_criteria": criteria,
                        "fields_extracted": sum(1 for v in criteria.values() if v)
                    }
                )
            else:
                raise ValueError("Could not extract JSON from LLM response")
                
        except Exception as e:
            context.add_workflow_step(
                AgentType.PARSER,
                "failed",
                {"query": context.original_query},
                str(e)
            )
        
        return context

class LocationMatcher:
    """Helper to match user locations to divisions"""
    
    # Map of locations to divisions
    LOCATION_MAP = {
        # South Bangalore
        "kanakapura": "South",
        "anjanapura": "South",
        "hsr": "South",
        "koramangala": "South",
        "indira nagar": "South",
        "indiranagar": "South",
        "bannerghatta": "South",
        "jayanagar": "South",
        "south": "South",
        
        # North Bangalore
        "yeshwanthpur": "North",
        "whitefield": "North",
        "hebbal": "North",
        "yelahanka": "North",
        "ramamurthy nagar": "North",
        "north": "North",
        
        # East Bangalore
        "marathahalli": "East",
        "ejipura": "East",
        "sarjapur": "East",
        "varthur": "East",
        "east": "East",
        
        # West Bangalore
        "tumkur": "West",
        "nelamangala": "West",
        "chikballapur": "West",
        "west": "West",
    }
    
    @classmethod
    def get_division(cls, location: str) -> Optional[str]:
        """Get division from location name"""
        if not location:
            return None
        location_lower = location.lower().strip()
        return cls.LOCATION_MAP.get(location_lower)
