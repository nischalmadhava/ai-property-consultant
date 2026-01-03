from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.agents import (
    ParserAgent, ScraperAgent, FilterSortAgent,
    DeveloperIntelligenceAgent, ComparisonAgent, RecommendationAgent,
    SearchContext
)
from app.models.property import SearchHistory, AgentInteraction
from app.schemas import SearchCriteria, ChatResponse
import json

class AgentOrchestrator:
    """
    Orchestrates the entire agentic workflow
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.parser = ParserAgent()
        self.scraper = ScraperAgent()
        self.filter_sort = FilterSortAgent()
        self.developer_intel = DeveloperIntelligenceAgent()
        self.comparison = ComparisonAgent()
        self.recommendation = RecommendationAgent()
    
    async def process_query(
        self,
        user_query: str,
        user_id: str = "anonymous",
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process user query through the entire agent workflow
        """
        
        # Initialize search context
        context = SearchContext(original_query=user_query)
        
        try:
            # Step 1: Parse user input
            context = await self.parser.parse(context)
            
            # Step 2: Scrape planning authority data
            context = await self.scraper.scrape(context)
            
            # Step 3: Filter and sort
            context = await self.filter_sort.filter_and_sort(context)
            
            # Step 4: Gather developer information and pricing
            context = await self.developer_intel.gather_developer_info(context)
            
            # Step 5: Compare and score properties
            context = await self.comparison.compare_and_score(context)
            
            # Step 6: Generate recommendations
            context = await self.recommendation.generate_recommendations(context)
            
        except Exception as e:
            context.add_workflow_step(
                "orchestrator",
                "failed",
                {"query": user_query},
                str(e)
            )
        
        # Save to database if session available
        if self.db:
            await self._save_search_history(context, user_id, session_id)
        
        # Format response
        response = self._format_response(context)
        
        return response
    
    async def _save_search_history(
        self,
        context: SearchContext,
        user_id: str,
        session_id: Optional[str]
    ):
        """Save search history and agent interactions to database"""
        
        try:
            # Create search history record
            search_history = SearchHistory(
                user_id=user_id,
                search_query=context.original_query,
                search_criteria={
                    "location": context.location,
                    "division": context.division,
                    "size_range": {"min": context.min_size, "max": context.max_size},
                    "price_range": {"min": context.min_price, "max": context.max_price},
                    "property_type": context.property_type
                },
                results_count=len(context.recommendations),
                workflow_status="completed" if not context.errors else "completed_with_errors",
                workflow_trace=context.to_dict()
            )
            
            self.db.add(search_history)
            self.db.flush()
            
            # Save agent interactions
            for step in context.workflow_steps:
                agent_interaction = AgentInteraction(
                    search_history_id=search_history.id,
                    agent_name=step.get("agent_type"),
                    agent_type=step.get("agent_type"),
                    input_data={},
                    output_data=step.get("details", {}),
                    status=step.get("status"),
                    error_message=step.get("error")
                )
                self.db.add(agent_interaction)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error saving search history: {e}")
    
    def _format_response(self, context: SearchContext) -> ChatResponse:
        """Format context into chat response"""
        
        # Build response message
        response_parts = []
        
        if context.errors:
            response_parts.append(f"⚠️ Processing completed with {len(context.errors)} issue(s).")
        else:
            response_parts.append("✅ Search completed successfully!")
        
        if context.recommendations:
            response_parts.append(f"\n📍 Found {len(context.recommendations)} matching properties:")
            for i, rec in enumerate(context.recommendations, 1):
                response_parts.append(
                    f"\n{i}. **{rec.get('name')}**\n"
                    f"   Price: ₹{rec.get('price'):,.0f}\n"
                    f"   Area: {rec.get('area')} sqft\n"
                    f"   Developer: {rec.get('developer')}\n"
                    f"   Score: {rec.get('total_score')}/100"
                )
        else:
            response_parts.append("\n❌ No properties found matching your criteria.")
        
        if context.reasoning:
            response_parts.append(f"\n\n💡 **Recommendation:** {context.reasoning}")
        
        response_text = "\n".join(response_parts)
        
        return ChatResponse(
            response=response_text,
            search_criteria=SearchCriteria(
                location=context.location or "",
                min_size=context.min_size or 0,
                max_size=context.max_size,
                min_price=context.min_price or 0,
                max_price=context.max_price,
                property_type=context.property_type,
                division=context.division
            ),
            properties=[
                {
                    "id": i,
                    "name": rec.get("name"),
                    "location": rec.get("location"),
                    "area": rec.get("area"),
                    "price": rec.get("price"),
                    "price_per_sqft": rec.get("price_per_sqft"),
                    "property_type": "plot",
                    "status": "available",
                    "created_at": context.started_at,
                    "updated_at": context.started_at
                }
                for i, rec in enumerate(context.recommendations, 1)
            ],
            reasoning=context.reasoning,
            workflow_trace=context.to_dict()
        )
