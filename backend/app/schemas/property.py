from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Property Schemas
class PropertyBase(BaseModel):
    name: str
    location: str
    area: float
    price: float
    property_type: str
    division: str
    description: Optional[str] = None
    rera_registered: bool = False
    rera_number: Optional[str] = None
    amenities: Optional[Dict[str, Any]] = None
    url: Optional[str] = None

class PropertyCreate(PropertyBase):
    developer_id: Optional[int] = None
    layout_approval_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    amenities: Optional[Dict[str, Any]] = None

class PropertyResponse(PropertyBase):
    id: int
    price_per_sqft: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime
    last_scraped: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Developer Schemas
class DeveloperBase(BaseModel):
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    established_year: Optional[int] = None
    description: Optional[str] = None

class DeveloperCreate(DeveloperBase):
    pass

class DeveloperResponse(DeveloperBase):
    id: int
    reputation_score: float
    reviews_count: int
    total_projects: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Layout Approval Schemas
class LayoutApprovalBase(BaseModel):
    project_name: str
    approval_number: str
    location: str
    division: str
    approved_area: float
    authority: str
    approval_date: datetime

class LayoutApprovalCreate(LayoutApprovalBase):
    authority_reference: Optional[str] = None
    area_code: Optional[str] = None
    document_url: Optional[str] = None

class LayoutApprovalResponse(LayoutApprovalBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_scraped: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Search Criteria Schemas
class SearchCriteria(BaseModel):
    location: str
    min_size: float = Field(default=0, description="Minimum plot size in sq ft")
    max_size: Optional[float] = None
    min_price: float = Field(default=0, description="Minimum price in rupees")
    max_price: Optional[float] = None
    property_type: Optional[str] = None
    division: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    search_criteria: Optional[SearchCriteria] = None
    properties: Optional[List[PropertyResponse]] = None
    reasoning: Optional[str] = None
    workflow_trace: Optional[Dict[str, Any]] = None

class SearchHistoryResponse(BaseModel):
    id: int
    user_id: str
    search_query: str
    search_criteria: Dict[str, Any]
    results_count: int
    workflow_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Agent Interaction Schemas
class AgentInteractionResponse(BaseModel):
    id: int
    agent_name: str
    agent_type: str
    status: str
    execution_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Map Division Schemas
class MapDivision(BaseModel):
    name: str  # North, South, East, West
    bounds: Dict[str, float]  # {north, south, east, west} coordinates
    description: Optional[str] = None

class LocationResponse(BaseModel):
    divisions: List[MapDivision]
    areas: Optional[List[str]] = None
