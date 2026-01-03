from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    PARSER = "parser"
    SCRAPER = "scraper"
    FILTER = "filter"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"

@dataclass
class SearchContext:
    """Context shared across all agents in the workflow"""
    
    # Original user input
    original_query: str
    
    # Parsed search criteria
    location: Optional[str] = None
    division: Optional[str] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: Optional[str] = None
    additional_requirements: Optional[str] = None
    
    # Scraped layout approvals
    layout_approvals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Filtered and sorted approvals
    filtered_approvals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Developer information
    developer_brochures: Dict[str, Any] = field(default_factory=dict)
    
    # Properties with pricing
    properties: List[Dict[str, Any]] = field(default_factory=list)
    
    # Final recommendations
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""
    
    # Workflow tracking
    workflow_steps: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_workflow_step(self, agent_type: AgentType, status: str, details: Dict[str, Any], error: Optional[str] = None):
        """Record a workflow step"""
        self.workflow_steps.append({
            "agent_type": agent_type.value,
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })
        if error:
            self.errors.append(f"{agent_type.value}: {error}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "original_query": self.original_query,
            "location": self.location,
            "division": self.division,
            "size_range": {"min": self.min_size, "max": self.max_size},
            "price_range": {"min": self.min_price, "max": self.max_price},
            "property_type": self.property_type,
            "layout_approvals_count": len(self.layout_approvals),
            "filtered_approvals_count": len(self.filtered_approvals),
            "properties_count": len(self.properties),
            "recommendations_count": len(self.recommendations),
            "workflow_steps": self.workflow_steps,
            "errors": self.errors
        }
