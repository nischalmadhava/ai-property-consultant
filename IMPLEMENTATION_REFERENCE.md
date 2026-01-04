# AI Property Consultant - Complete Implementation Reference

**Project:** AI Property Consultant for Bangalore  
**Status:** MVP Complete (56 files, 5000+ lines of code)  
**Date:** January 4, 2026  

---

## Table of Contents

1. [Database Models](#database-models)
2. [Backend Agents](#backend-agents)
3. [API Schemas](#api-schemas)
4. [API Routes & Endpoints](#api-routes--endpoints)
5. [Frontend Components](#frontend-components)
6. [Configuration](#configuration)
7. [Workflow Architecture](#workflow-architecture)
8. [Docker Setup](#docker-setup)

---

## DATABASE MODELS

### 1. **Property** Model
**Table:** `properties` (Primary entity for real estate listings)

**Fields:**
- `id` (Integer): Primary key
- `name` (String[255]): Property name
- `description` (Text): Detailed description
- `location` (String[255]): Location name (e.g., "Whitefield", "Koramangala")
- `area` (Float): Plot area in square feet
- `price` (Float): Price in Indian rupees
- `price_per_sqft` (Float): Calculated price per sq ft
- `property_type` (String[50]): Enum - "plot", "apartment", "villa", "commercial"
- `status` (String[50]): Enum - "approved", "under_approval", "rejected", "sold"
- `developer_id` (Integer): Foreign key to Developer
- `layout_approval_id` (Integer): Foreign key to LayoutApproval
- `latitude` (Float): GPS latitude
- `longitude` (Float): GPS longitude
- `division` (String[100]): "North", "South", "East", or "West" Bangalore
- `amenities` (JSON): Dictionary of nearby amenities (schools, hospitals, parks, etc.)
- `rera_registered` (Boolean): RERA registration status
- `rera_number` (String[100]): RERA registration number
- `url` (String[500]): Source URL for web scraping
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `last_scraped` (DateTime): Last data refresh timestamp

**Relationships:**
- `developer` → Developer (many-to-one)
- `layout_approval` → LayoutApproval (many-to-one)

**Methods:**
- `__repr__()`: Returns formatted property string

---

### 2. **Developer** Model
**Table:** `developers` (Real estate developers/builders)

**Fields:**
- `id` (Integer): Primary key
- `name` (String[255]): Developer name (unique)
- `description` (Text): Company description
- `website` (String[500]): Company website URL
- `phone` (String[20]): Contact phone
- `email` (String[255]): Contact email
- `reputation_score` (Float): 0-5 star rating
- `reviews_count` (Integer): Number of reviews
- `established_year` (Integer): Year company was founded
- `total_projects` (Integer): Number of projects completed
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- `properties` → Property[] (one-to-many)

**Methods:**
- `__repr__()`: Returns formatted developer string

---

### 3. **LayoutApproval** Model
**Table:** `layout_approvals` (BDA/BMRDA project approvals)

**Fields:**
- `id` (Integer): Primary key
- `project_name` (String[255]): Project name
- `approval_number` (String[100]): Unique approval number (unique)
- `approval_date` (DateTime): Date of approval
- `approved_area` (Float): Total approved area in acres
- `location` (String[255]): Project location
- `division` (String[100]): Bangalore division
- `area_code` (String[50]): Area/Zone code
- `authority` (String[100]): Approving authority (BDA, BMRDA, BBMP, etc.)
- `authority_reference` (String[200]): Authority reference number
- `document_url` (String[500]): Online document link
- `document_path` (String[500]): Local document storage path
- `document_hash` (String[100]): Document integrity hash
- `is_active` (Boolean): Active/inactive status
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `last_scraped` (DateTime): Last data refresh timestamp

**Relationships:**
- `properties` → Property[] (one-to-many)

**Methods:**
- `__repr__()`: Returns formatted approval string

---

### 4. **SearchHistory** Model
**Table:** `search_history` (Tracks user searches for analytics)

**Fields:**
- `id` (Integer): Primary key
- `user_id` (String[255]): User identifier (can be "anonymous")
- `search_query` (Text): Original natural language query
- `search_criteria` (JSON): Structured search parameters:
  ```json
  {
    "location": "string",
    "size": {"min": float, "max": float},
    "price": {"min": float, "max": float},
    "property_type": "string",
    "division": "string"
  }
  ```
- `results_count` (Integer): Number of results found
- `results` (JSON): Summary of top results
- `workflow_status` (String[50]): "pending", "processing", "completed", "failed"
- `workflow_trace` (JSON): Complete trace of agent execution steps
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Methods:**
- `__repr__()`: Returns formatted search string

---

### 5. **AgentInteraction** Model
**Table:** `agent_interactions` (Tracks individual agent executions)

**Fields:**
- `id` (Integer): Primary key
- `search_history_id` (Integer): Foreign key to SearchHistory
- `agent_name` (String[100]): Name of the agent (ParserAgent, etc.)
- `input_data` (JSON): Agent input
- `output_data` (JSON): Agent output
- `execution_time` (Float): Execution time in seconds
- `status` (String[50]): "success", "failed", "timeout"
- `error_message` (Text): Error details if failed
- `created_at` (DateTime): Record creation timestamp

---

## BACKEND AGENTS

### 1. **ParserAgent** 
**Purpose:** Extract structured search criteria from natural language input  
**File:** `backend/app/agents/parser.py`

**Key Features:**
- Uses LangChain + OpenAI GPT-4 for NLP
- Extracts JSON-structured criteria from plain English
- Maps location names to Bangalore divisions (North/South/East/West)

**Extracted Criteria:**
```json
{
  "location": "specific location name",
  "division": "North|South|East|West",
  "min_size": "minimum sq ft",
  "max_size": "maximum sq ft",
  "min_price": "minimum price in rupees",
  "max_price": "maximum price in rupees",
  "property_type": "plot|apartment|villa|commercial",
  "additional_requirements": "string"
}
```

**Methods:**
- `async parse(context: SearchContext) → SearchContext`
- `LocationMatcher.match_to_division(location: str) → str`

**Location Mapping:**
- **North:** Yeshwanthpur, Whitefield, Hebbal, Yelahanka, Ramamurthy Nagar
- **South:** Kanakapura, Anjanapura, HSR, Koramangala, Indiranagar, Bannerghatta, Jayanagar
- **East:** Marathahalli, Ejipura, Sarjapur, Varthur
- **West:** Tumkur, Nelamangala

---

### 2. **ScraperAgent**
**Purpose:** Fetch layout approval data from planning authorities  
**File:** `backend/app/agents/scraper.py`

**Key Features:**
- Scrapes BDA/BMRDA layout approval databases
- Currently uses mock data (ready for real scraper integration)
- Filters by division and area criteria

**Data Scraped:**
- Project names
- Approval numbers
- Approved area (acres)
- Authority (BDA, BMRDA, BBMP)
- Location coordinates

**Methods:**
- `async scrape(context: SearchContext) → SearchContext`
- `_fetch_layout_approvals() → List[Dict]`
- `_parse_approval_data(raw_data) → Dict`

---

### 3. **FilterSortAgent**
**Purpose:** Filter and sort properties by user criteria  
**File:** `backend/app/agents/filter.py`

**Filtering Logic:**
- By division (North/South/East/West)
- By area range (min/max sq ft)
- By price range (min/max rupees)
- By property type (plot/apartment/villa/commercial)
- By availability status (approved projects only)

**Sorting Options:**
- Price (low to high / high to low)
- Area size (small to large / large to small)
- Developer reputation score
- Proximity to city center
- Amenity density score

**Methods:**
- `async filter_and_sort(context: SearchContext) → SearchContext`
- `_apply_filters(approvals: List, criteria: Dict) → List`
- `_sort_properties(properties: List, sort_key: str) → List`

---

### 4. **DeveloperIntelligenceAgent**
**Purpose:** Gather developer information and pricing intelligence  
**File:** `backend/app/agents/developer_intel.py`

**Data Gathered:**
- Developer reputation score (0-5 stars)
- Historical project information
- Pricing trends for each developer
- Project delivery timelines
- Customer reviews and complaints ratio

**Features:**
- Cross-references developer database
- Analyzes price per sq ft trends
- Flags red-flag developers
- Estimates project completion timeline

**Methods:**
- `async gather_developer_info(context: SearchContext) → SearchContext`
- `_get_developer_brochure(developer_id: int) → Dict`
- `_analyze_pricing_trends(developer_id: int) → Dict`
- `_calculate_delivery_risk(developer_id: int) → Float`

---

### 5. **ComparisonAgent**
**Purpose:** Score and compare properties using a 100-point system  
**File:** `backend/app/agents/comparison.py`

**Scoring Methodology (100 points):**
- **Location Score (30%):** 30 points
  - Distance to city center
  - Connectivity (highways, metro, bus routes)
  - Neighborhood development level
  
- **Developer Score (25%):** 25 points
  - Reputation score (0-5 stars)
  - Project delivery history
  - Financial stability
  
- **Price Score (20%):** 20 points
  - Price per sq ft vs. market average
  - Price trend analysis
  - Appreciation potential
  
- **Amenities Score (15%):** 15 points
  - Nearby schools, hospitals, parks
  - Shopping centers, restaurants
  - Public transportation access
  
- **Legal & Compliance (10%):** 10 points
  - RERA registration
  - Layout approval status
  - No legal disputes

**Methods:**
- `async compare_and_score(context: SearchContext) → SearchContext`
- `_calculate_location_score(property: Dict) → Float`
- `_calculate_developer_score(developer_id: int) → Float`
- `_calculate_price_score(property: Dict) → Float`
- `_calculate_amenities_score(property: Dict) → Float`
- `_calculate_compliance_score(property: Dict) → Float`

---

### 6. **RecommendationAgent**
**Purpose:** Generate AI-powered recommendations with reasoning  
**File:** `backend/app/agents/recommendation.py`

**Recommendation Logic:**
- Ranks properties by composite score
- Generates personalized reasoning for each recommendation
- Identifies unique selling propositions (USPs)
- Highlights pros and cons

**Output per Recommendation:**
```json
{
  "rank": 1,
  "property_id": "int",
  "name": "string",
  "composite_score": 85.5,
  "reasoning": "This is the best match because...",
  "pros": ["list of advantages"],
  "cons": ["list of considerations"],
  "investment_potential": "high|medium|low",
  "next_steps": ["Contact developer", "Site visit recommended"]
}
```

**Methods:**
- `async generate_recommendations(context: SearchContext) → SearchContext`
- `_rank_by_score(properties: List) → List`
- `_generate_reasoning(property: Dict, scores: Dict) → str`
- `_identify_usps(property: Dict) → List[str]`
- `_assess_investment_potential(property: Dict) → str`

---

### 7. **SearchContext** (Shared State)
**Purpose:** Maintains state across all agents  
**File:** `backend/app/agents/context.py`

**Data Structure:**
```python
@dataclass
class SearchContext:
    # Input
    original_query: str
    
    # Parsed criteria
    location: Optional[str]
    division: Optional[str]
    min_size: Optional[float]
    max_size: Optional[float]
    min_price: Optional[float]
    max_price: Optional[float]
    property_type: Optional[str]
    additional_requirements: Optional[str]
    
    # Agent outputs (pipeline data)
    layout_approvals: List[Dict]
    filtered_approvals: List[Dict]
    developer_brochures: Dict[str, Any]
    properties: List[Dict]
    recommendations: List[Dict]
    reasoning: str
    
    # Tracking
    workflow_steps: List[Dict]
    errors: List[str]
    started_at: datetime
```

**Methods:**
- `add_workflow_step(agent_type: AgentType, status: str, details: Dict, error: str)`
- `to_dict() → Dict`

---

### 8. **AgentOrchestrator**
**Purpose:** Coordinates execution of all agents in sequence  
**File:** `backend/app/agents/orchestrator.py`

**Workflow Pipeline:**
```
ParserAgent (parse input)
    ↓
ScraperAgent (fetch data)
    ↓
FilterSortAgent (filter & sort)
    ↓
DeveloperIntelligenceAgent (gather intel)
    ↓
ComparisonAgent (score & compare)
    ↓
RecommendationAgent (generate recommendations)
    ↓
Database Save & Format Response
```

**Methods:**
- `async process_query(user_query: str, user_id: str, session_id: str) → ChatResponse`
- `async _save_search_history(context: SearchContext, user_id: str, session_id: str)`
- `_format_response(context: SearchContext) → ChatResponse`

---

## API SCHEMAS

### 1. **ChatRequest** (Input Schema)
```python
class ChatRequest(BaseModel):
    message: str           # User's natural language query
    user_id: Optional[str] # Optional user identifier
    session_id: Optional[str] # Session ID for continuity
    context: Optional[Dict] # Optional previous context
```

### 2. **ChatResponse** (Output Schema)
```python
class ChatResponse(BaseModel):
    session_id: str
    message: str
    recommendations: List[PropertyRecommendation]
    search_criteria: SearchCriteria
    workflow_trace: WorkflowTrace
    timestamp: datetime
```

### 3. **PropertyRecommendation** (Individual Recommendation)
```python
class PropertyRecommendation(BaseModel):
    rank: int
    property_id: int
    name: str
    location: str
    area: float
    price: float
    price_per_sqft: float
    composite_score: float
    location_score: float
    developer_score: float
    price_score: float
    amenities_score: float
    compliance_score: float
    reasoning: str
    pros: List[str]
    cons: List[str]
    investment_potential: str
    developer_info: DeveloperInfo
    amenities: Dict[str, List[str]]
    next_steps: List[str]
```

### 4. **SearchCriteria** (Parsed Search Schema)
```python
class SearchCriteria(BaseModel):
    location: Optional[str]
    division: Optional[str]
    area_range: Dict[str, Optional[float]]  # {min, max}
    price_range: Dict[str, Optional[float]]  # {min, max}
    property_type: Optional[str]
    additional_requirements: Optional[str]
```

### 5. **LocationResponse** (Map Data Schema)
```python
class LocationResponse(BaseModel):
    divisions: List[MapDivision]
    center: Dict[str, float]  # {latitude, longitude}
```

### 6. **MapDivision** (Division Schema)
```python
class MapDivision(BaseModel):
    name: str
    bounds: Dict[str, float]  # {north, south, east, west}
    description: str
    area_id: Optional[str]
    amenity_summary: Optional[Dict]
```

### 7. **WorkflowTrace** (Agent Execution Trace)
```python
class WorkflowTrace(BaseModel):
    started_at: datetime
    completed_at: datetime
    total_duration_ms: int
    agent_steps: List[AgentStep]
    errors: List[str]
```

### 8. **AgentStep** (Individual Agent Execution)
```python
class AgentStep(BaseModel):
    agent_name: str
    status: str  # success, failed, skipped
    input_summary: Dict
    output_summary: Dict
    duration_ms: int
    error_message: Optional[str]
```

---

## API ROUTES & ENDPOINTS

### 1. **POST /api/chat**
**Purpose:** Process chat message and return recommendations

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to buy a 2-acre plot in south bangalore for 50 lakhs",
    "user_id": "user123",
    "session_id": "session123"
  }'
```

**Response:**
```json
{
  "session_id": "session123",
  "message": "Found 5 properties matching your criteria",
  "recommendations": [
    {
      "rank": 1,
      "property_id": 101,
      "name": "Prestige Tech Park",
      "location": "Koramangala",
      "area": 20000,
      "price": 5000000,
      "price_per_sqft": 250,
      "composite_score": 88.5,
      "reasoning": "...",
      "pros": [...],
      "cons": [...]
    }
  ],
  "search_criteria": {...},
  "workflow_trace": {...},
  "timestamp": "2026-01-04T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Successful query processing
- `400 Bad Request`: Empty message
- `500 Internal Server Error`: Processing error

---

### 2. **WebSocket /api/ws/chat/{session_id}**
**Purpose:** Real-time bidirectional chat

**Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/chat/session123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: "status", "response", "error"
  // data.message: status message
  // data.data: full response object
};

ws.send(JSON.stringify({
  message: "What properties are available?"
}));
```

**Message Types:**
- `status`: Processing status updates
- `response`: Final recommendation response
- `error`: Error messages

---

### 3. **GET /api/locations**
**Purpose:** Get Bangalore divisions and areas for map

**Response:**
```json
{
  "divisions": [
    {
      "name": "North Bangalore",
      "bounds": {
        "north": 13.2,
        "south": 13.0,
        "east": 77.7,
        "west": 77.5
      },
      "description": "Includes Yeshwanthpur, Whitefield, Hebbal, Yelahanka"
    },
    {
      "name": "South Bangalore",
      "bounds": {...}
    },
    {
      "name": "East Bangalore",
      "bounds": {...}
    },
    {
      "name": "West Bangalore",
      "bounds": {...}
    }
  ],
  "center": {
    "latitude": 12.9716,
    "longitude": 77.5946
  }
}
```

---

### 4. **POST /api/search-by-location**
**Purpose:** Search properties by specific location/division

**Request:**
```json
{
  "division": "South",
  "area_min_sqft": 1000,
  "area_max_sqft": 5000,
  "price_min": 2000000,
  "price_max": 10000000,
  "property_type": "plot"
}
```

**Response:**
```json
{
  "properties": [...],
  "total_count": 45,
  "filters_applied": {...}
}
```

---

### 5. **GET /api/health**
**Purpose:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T10:30:00Z",
  "database": "connected",
  "redis": "connected",
  "llm": "connected"
}
```

---

### 6. **GET /api/docs**
**Purpose:** Interactive Swagger API documentation

**Access:** http://localhost:8000/docs

---

## FRONTEND COMPONENTS

### 1. **Home Page** (`src/app/page.tsx`)
**Purpose:** Main landing page with view toggle

**Features:**
- Toggle between Map View and Chat View
- Responsive header with branding
- Main content area with grid layout
- Footer with additional information

**State Management:**
```typescript
- selectedDivision: string | null
- viewMode: 'map' | 'chat'
```

**UI Elements:**
- Header with title and view toggle buttons
- Main content container
- Side panel for selected area info
- Footer with links and info

---

### 2. **MapView Component** (`src/components/MapView.tsx`)
**Purpose:** Interactive SVG map of Bangalore with 4 divisions

**Features:**
- SVG-based interactive map
- 4 clickable divisions (North/South/East/West)
- Visual feedback on hover
- Division-specific descriptions
- Color-coded regions

**Division Colors:**
- **North:** RGB(66, 133, 244) - Blue
- **South:** RGB(217, 48, 37) - Red
- **East:** RGB(51, 182, 121) - Green
- **West:** RGB(251, 188, 4) - Yellow

**Props:**
```typescript
interface MapViewProps {
  onDivisionSelect: (division: string) => void
}
```

**Interactivity:**
- Hover: Division becomes semi-transparent (opacity 0.7)
- Click: Triggers onDivisionSelect callback
- Tooltip: Shows division name on hover

**Division Coordinates (SVG paths):**
- North: Top-right quadrant
- South: Bottom-right quadrant
- East: Right side with curved boundary
- West: Left side with curved boundary

---

### 3. **ChatInterface Component** (`src/components/ChatInterface.tsx`)
**Purpose:** Real-time chat with property recommendations

**Features:**
- Message input field with send button
- Chat history display
- Property card grid for recommendations
- Loading states
- Error handling
- Real-time streaming (optional WebSocket)

**State:**
```typescript
- messages: Message[]
- inputValue: string
- isLoading: boolean
- recommendations: PropertyRecommendation[]
- selectedProperty: PropertyRecommendation | null
```

**Message Types:**
- User messages (right-aligned)
- Assistant messages (left-aligned)
- System messages (centered, gray)
- Property recommendations (card grid)

**API Integration:**
- REST POST `/api/chat` for initial requests
- WebSocket `/api/ws/chat/{sessionId}` for real-time updates

**Property Card Display:**
```typescript
- Property image
- Name and location
- Area and price
- Composite score (visual gauge)
- Developer info
- Amenities badges
- "View Details" and "Contact" buttons
```

---

### 4. **Button UI Component** (`src/components/ui/Button.tsx`)
**Purpose:** Reusable button with variants

**Variants:**
- Primary (blue background)
- Secondary (gray background)
- Outlined (border-only)
- Ghost (text-only)

**Props:**
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}
```

---

### 5. **Card UI Component** (`src/components/ui/Card.tsx`)
**Purpose:** Reusable card container with shadow

**Features:**
- Fixed background color (white)
- Shadow effect
- Border radius
- Padding

**Props:**
```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}
```

---

## CONFIGURATION

### 1. **Settings** (`backend/app/config/settings.py`)
```python
class Settings(BaseSettings):
    # API Configuration
    api_title: str = "AI Property Consultant"
    api_description: str = "..."
    api_version: str = "1.0.0"
    
    # Database
    database_url: str  # PostgreSQL connection string
    
    # LLM Configuration
    openai_api_key: str
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000
    
    # Redis
    redis_url: str
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

### 2. **Database Configuration** (`backend/app/config/database.py`)
```python
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. **Environment Variables** (`backend/.env.example`)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/property_consultant

# OpenAI
OPENAI_API_KEY=sk-...

# LLM Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.3

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_TITLE=AI Property Consultant
API_VERSION=1.0.0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

---

## WORKFLOW ARCHITECTURE

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────┐
│ User Input (Chat or Map Selection)                      │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js)                                      │
│ - ChatInterface sends message to /api/chat              │
│ - Or MapView triggers location-based search             │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI Backend: POST /api/chat                         │
│ - Instantiate AgentOrchestrator                         │
│ - Call process_query()                                  │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ AGENT PIPELINE EXECUTION                                │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │ Agent Step 1    │
    ├─────────────────┤
    │ ParserAgent     │
    │ Extracts:       │
    │ - location      │
    │ - division      │
    │ - size range    │
    │ - price range   │
    │ - property type │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Agent Step 2    │
    ├─────────────────┤
    │ ScraperAgent    │
    │ Fetches:        │
    │ - Layout Apps   │
    │ - BDA data      │
    │ - BMRDA data    │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Agent Step 3    │
    ├─────────────────┤
    │ FilterSort      │
    │ Filters by:     │
    │ - division      │
    │ - area          │
    │ - price         │
    │ - type          │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Agent Step 4    │
    ├─────────────────┤
    │ DevIntel        │
    │ Gathers:        │
    │ - Developer rep │
    │ - Pricing trend │
    │ - Project hist  │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Agent Step 5    │
    ├─────────────────┤
    │ Comparison      │
    │ Scores:         │
    │ - Location (30%)│
    │ - Developer(25%)│
    │ - Price (20%)   │
    │ - Amenities(15%)│
    │ - Legal (10%)   │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Agent Step 6    │
    ├─────────────────┤
    │ Recommendation  │
    │ Generates:      │
    │ - Rankings      │
    │ - Reasoning     │
    │ - Pros/Cons     │
    └────────┬────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Save to Database                                        │
│ - SearchHistory record                                  │
│ - AgentInteraction records                              │
│ - Complete workflow trace                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Format ChatResponse                                     │
│ - Recommendations list                                  │
│ - Search criteria                                       │
│ - Workflow trace (for debugging)                        │
│ - Timestamp                                             │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Return to Frontend                                      │
│ - JSON response with recommendations                    │
│ - Display in ChatInterface                              │
│ - Show property cards with scores                       │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Through SearchContext

```
SearchContext
├── original_query: "I need 2-acre plot under 50L in south"
│
├── [After ParserAgent]
│   ├── location: "South Bangalore"
│   ├── division: "South"
│   ├── min_size: 87120 (2 acres)
│   ├── max_size: null
│   ├── min_price: null
│   └── max_price: 5000000
│
├── [After ScraperAgent]
│   └── layout_approvals: [
│       { project: "Prestige Tech", approval: "BDA-001", ... },
│       { project: "DLF Cyber", approval: "BDA-002", ... }
│     ]
│
├── [After FilterSortAgent]
│   └── filtered_approvals: [
│       { project: "Prestige Tech", score: 0.92, ... }
│     ]
│
├── [After DeveloperIntelligenceAgent]
│   ├── developer_brochures: {
│   │   "prestige": { reputation: 4.5, reviews: 1200, ... }
│   │ }
│   └── properties: [
│       {
│         name: "Prestige Tech Plot",
│         developer_id: 1,
│         price: 4500000,
│         ...
│       }
│     ]
│
├── [After ComparisonAgent]
│   └── properties: [
│       {
│         name: "Prestige Tech Plot",
│         location_score: 28,
│         developer_score: 24,
│         price_score: 18,
│         amenities_score: 14,
│         compliance_score: 9,
│         composite_score: 93
│       }
│     ]
│
└── [After RecommendationAgent]
    └── recommendations: [
        {
          rank: 1,
          property_id: 101,
          composite_score: 93,
          reasoning: "Best match...",
          pros: [...],
          cons: [...]
        }
      ]
```

---

## DOCKER SETUP

### Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Docker Compose (4 Services)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Frontend        │  │  Backend         │                │
│  │  Next.js:3000    │  │  FastAPI:8000    │                │
│  │  Container       │  │  Container       │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                           │
│           │ HTTP                │ REST/WebSocket           │
│           │                     │                           │
│           └─────────┬───────────┘                           │
│                     │                                       │
│                     ▼                                       │
│           ┌──────────────────┐                             │
│           │  PostgreSQL:5432 │                             │
│           │  Database        │                             │
│           │  Container       │                             │
│           └──────────────────┘                             │
│                     ▲                                       │
│                     │                                       │
│           ┌──────────┴──────────┐                          │
│           │                     │                          │
│           ▼                     ▼                          │
│    ┌──────────────┐      ┌──────────────┐                │
│    │  Redis:6379  │      │  Backend     │                │
│    │  Cache       │      │  LangChain   │                │
│    │  Container   │      │  OpenAI API  │                │
│    └──────────────┘      └──────────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Docker Compose Configuration (`docker-compose.yml`)

**Service 1: Frontend (Next.js)**
- Image: `node:20-alpine`
- Port: 3000
- Volume: `./frontend:/app`
- Environment: `NODE_ENV=development`
- Command: `npm run dev`

**Service 2: Backend (FastAPI)**
- Image: `python:3.11-slim`
- Port: 8000
- Volume: `./backend:/app`
- Depends on: PostgreSQL, Redis
- Environment: Database URL, OpenAI API Key, etc.
- Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

**Service 3: PostgreSQL**
- Image: `postgres:15-alpine`
- Port: 5432
- Volume: `postgres_data:/var/lib/postgresql/data`
- Environment: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Health check: `pg_isready`

**Service 4: Redis**
- Image: `redis:7-alpine`
- Port: 6379
- Volume: `redis_data:/data`
- Health check: `redis-cli ping`

---

## STARTUP & VERIFICATION

### Start Application
```bash
cd "d:\AI Property Consultant"
docker-compose up -d
```

### Verify Services
```bash
docker-compose ps

# Expected output:
# NAME              STATUS      PORTS
# ai-frontend       Up 2m       0.0.0.0:3000->3000/tcp
# ai-backend        Up 2m       0.0.0.0:8000->8000/tcp
# ai-postgres       Up 2m       5432/tcp
# ai-redis          Up 2m       6379/tcp
```

### Access Application
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **WebSocket Test:** ws://localhost:8000/api/ws/chat/test123

### View Logs
```bash
# Backend logs
docker-compose logs -f ai-backend

# Frontend logs
docker-compose logs -f ai-frontend

# All logs
docker-compose logs -f
```

---

## File Structure Summary

```
AI Property Consultant/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── orchestrator.py (6 agents coordination)
│   │   │   ├── parser.py (NLP extraction)
│   │   │   ├── scraper.py (Data fetching)
│   │   │   ├── filter.py (Filtering & sorting)
│   │   │   ├── developer_intel.py (Developer info)
│   │   │   ├── comparison.py (100-point scoring)
│   │   │   ├── recommendation.py (AI recommendations)
│   │   │   └── context.py (Shared state)
│   │   ├── models/
│   │   │   └── property.py (5 SQLAlchemy models)
│   │   ├── schemas/
│   │   │   └── property.py (Pydantic validation)
│   │   ├── routes/
│   │   │   └── chat.py (6 API endpoints)
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   └── database.py
│   │   ├── main.py (FastAPI app)
│   │   └── __init__.py
│   ├── requirements.txt (20 packages)
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx (Home page)
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── MapView.tsx (4-division map)
│   │   │   ├── ChatInterface.tsx (Real-time chat)
│   │   │   └── ui/
│   │   │       ├── Button.tsx
│   │   │       └── Card.tsx
│   │   └── ...
│   ├── package.json (12 packages)
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── docker-compose.yml (4 services)
├── .env.example (Configuration template)
├── README.md
├── ARCHITECTURE.md
├── SETUP.md
├── QUICK_REFERENCE.md
└── ... (7 more documentation files)
```

---

## Key Statistics

- **Total Files:** 56
- **Lines of Code:** 5000+
- **Backend Python Code:** 2500+ lines
- **Frontend TypeScript Code:** 800+ lines
- **Database Models:** 5
- **Agents:** 6 (in parallel pipeline)
- **API Endpoints:** 6
- **Frontend Components:** 5+
- **Documentation Files:** 9
- **Docker Services:** 4
- **Supported Divisions:** 4 (North, South, East, West)
- **Scoring Metrics:** 5 categories (100 points total)

---

This reference provides comprehensive details of all implemented classes, features, data flows, and configurations for analysis and future development.
