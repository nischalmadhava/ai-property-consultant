from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.config.database import Base

class PropertyType(str, enum.Enum):
    PLOT = "plot"
    APARTMENT = "apartment"
    VILLA = "villa"
    COMMERCIAL = "commercial"

class PropertyStatus(str, enum.Enum):
    APPROVED = "approved"
    UNDER_APPROVAL = "under_approval"
    REJECTED = "rejected"
    SOLD = "sold"

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=False)
    area = Column(Float, nullable=False)  # in sq ft
    price = Column(Float, nullable=False)  # in rupees
    price_per_sqft = Column(Float, nullable=True)
    property_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=PropertyStatus.APPROVED.value)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=True)
    layout_approval_id = Column(Integer, ForeignKey("layout_approvals.id"), nullable=True)
    
    # Location details
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    division = Column(String(100), nullable=False)  # North, South, East, West
    
    # Amenities (JSON)
    amenities = Column(JSON, nullable=True)  # {schools: [], hospitals: [], etc}
    
    # Additional details
    rera_registered = Column(Boolean, default=False)
    rera_number = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)  # Source URL
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, nullable=True)
    
    # Relationships
    developer = relationship("Developer", back_populates="properties")
    layout_approval = relationship("LayoutApproval", back_populates="properties")
    
    def __repr__(self):
        return f"<Property {self.name} - {self.location}>"

class Developer(Base):
    __tablename__ = "developers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Reputation
    reputation_score = Column(Float, default=0.0)  # 0-5
    reviews_count = Column(Integer, default=0)
    
    # Additional info
    established_year = Column(Integer, nullable=True)
    total_projects = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = relationship("Property", back_populates="developer")
    
    def __repr__(self):
        return f"<Developer {self.name}>"

class LayoutApproval(Base):
    __tablename__ = "layout_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    approval_number = Column(String(100), nullable=False, unique=True)
    approval_date = Column(DateTime, nullable=False)
    approved_area = Column(Float, nullable=False)  # in acres
    
    # Location details
    location = Column(String(255), nullable=False)
    division = Column(String(100), nullable=False)
    area_code = Column(String(50), nullable=True)
    
    # Authority details
    authority = Column(String(100), nullable=False)  # BDA, BMRDA, BBMP, etc
    authority_reference = Column(String(200), nullable=True)
    
    # Document details
    document_url = Column(String(500), nullable=True)
    document_path = Column(String(500), nullable=True)
    document_hash = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, nullable=True)
    
    # Relationships
    properties = relationship("Property", back_populates="layout_approval")
    
    def __repr__(self):
        return f"<LayoutApproval {self.project_name}>"

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)  # Can be anonymous or authenticated
    
    # Search criteria (JSON)
    search_query = Column(Text, nullable=False)
    search_criteria = Column(JSON, nullable=False)  # {location, size, price_range, etc}
    
    # Results
    results_count = Column(Integer, default=0)
    results = Column(JSON, nullable=True)  # Summary of results
    
    # Agent workflow
    workflow_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    workflow_trace = Column(JSON, nullable=True)  # Trace of agent steps
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SearchHistory {self.id} - {self.user_id}>"

class AgentInteraction(Base):
    __tablename__ = "agent_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    search_history_id = Column(Integer, ForeignKey("search_history.id"))
    
    # Agent details
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)  # parser, scraper, filter, etc
    
    # Input/Output
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    
    # Status and timing
    status = Column(String(50), nullable=False)  # success, failure, partial
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentInteraction {self.agent_name}>"
