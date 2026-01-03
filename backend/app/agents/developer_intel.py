from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import re
from app.config import settings
from .context import SearchContext, AgentType

class DeveloperIntelligenceAgent:
    """
    Gathers developer information and pricing from developer websites
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0,
            api_key=settings.openai_api_key
        )
    
    async def gather_developer_info(self, context: SearchContext) -> SearchContext:
        """
        For each top project, gather developer information and pricing
        """
        
        try:
            # Get top 5-10 projects
            top_projects = context.filtered_approvals[:10]
            
            context.developer_brochures = {}
            properties_list = []
            
            for project in top_projects:
                dev_info = await self._fetch_developer_brochure(project)
                
                if dev_info:
                    context.developer_brochures[project["project_name"]] = dev_info
                    
                    # Create property records with pricing info
                    properties = self._create_property_records(project, dev_info, context)
                    properties_list.extend(properties)
            
            context.properties = properties_list
            
            context.add_workflow_step(
                AgentType.SCRAPER,
                "success",
                {
                    "top_projects_processed": len(top_projects),
                    "properties_found": len(properties_list),
                    "developers_contacted": len(context.developer_brochures)
                }
            )
            
        except Exception as e:
            context.add_workflow_step(
                AgentType.SCRAPER,
                "failed",
                {"projects_count": len(context.filtered_approvals)},
                str(e)
            )
        
        return context
    
    async def _fetch_developer_brochure(self, project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Fetch developer brochure and pricing information (Mock for now)
        In production, would integrate with actual developer website scrapers
        """
        
        # Mock developer information
        mock_brochures = {
            "Kanakapura Layout - Phase 1": {
                "developer": "Sri Developers",
                "prices_per_plot": [
                    {"size_sqft": 1200, "price": 3600000},  # 30x40
                    {"size_sqft": 1200, "price": 3500000},
                ],
                "amenities": ["Water Supply", "Electricity", "Road Access"],
                "rera_registered": True,
                "rera_number": "REG/BLR/001"
            },
            "Kanakapura Green Acres": {
                "developer": "Green Earth Projects",
                "prices_per_plot": [
                    {"size_sqft": 1200, "price": 3200000},
                    {"size_sqft": 1200, "price": 3100000},
                ],
                "amenities": ["Water Supply", "Electricity", "Green Space", "Security Gate"],
                "rera_registered": True,
                "rera_number": "REG/BLR/002"
            },
            "Kanakpura Residency": {
                "developer": "Kanakpura Builders",
                "prices_per_plot": [
                    {"size_sqft": 1200, "price": 3800000},
                    {"size_sqft": 1200, "price": 3700000},
                ],
                "amenities": ["Water Supply", "Electricity", "Gated Community", "Park"],
                "rera_registered": True,
                "rera_number": "REG/BLR/003"
            }
        }
        
        return mock_brochures.get(project["project_name"])
    
    def _create_property_records(
        self, 
        project: Dict[str, Any], 
        dev_info: Dict[str, Any],
        context: SearchContext
    ) -> List[Dict[str, Any]]:
        """Create property records from project and developer info"""
        
        properties = []
        
        for price_info in dev_info.get("prices_per_plot", []):
            size_sqft = price_info.get("size_sqft", 0)
            price = price_info.get("price", 0)
            
            # Check if matches user criteria
            if context.min_size and size_sqft < context.min_size:
                continue
            if context.max_size and size_sqft > context.max_size:
                continue
            if context.min_price and price < context.min_price:
                continue
            if context.max_price and price > context.max_price:
                continue
            
            property_record = {
                "name": f"{project['project_name']} - {size_sqft} sqft",
                "location": project.get("location"),
                "division": project.get("division"),
                "area": size_sqft,
                "price": price,
                "price_per_sqft": price / size_sqft if size_sqft > 0 else 0,
                "developer": dev_info.get("developer"),
                "project_approval": project.get("approval_number"),
                "amenities": dev_info.get("amenities", []),
                "rera_registered": dev_info.get("rera_registered", False),
                "rera_number": dev_info.get("rera_number"),
                "approval_date": project.get("approval_date")
            }
            properties.append(property_record)
        
        return properties
