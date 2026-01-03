# AI Property Consultant - Bangalore

An AI-powered agentic workflow for property search in Bangalore. Users can interact with an intelligent chatbot or use an interactive map to find properties matching their criteria.

## 🎯 Features

- **Interactive Map View**: Select from 4 divisions of Bangalore (North, South, East, West)
- **AI Chat Interface**: Describe your property requirements in plain English
- **Intelligent Agent Workflow**:
  1. Parse natural language queries
  2. Scrape planning authority layouts
  3. Filter and sort by criteria
  4. Gather developer information and pricing
  5. Compare and score properties
  6. Generate AI-powered recommendations

## 🏗️ Project Structure

```
AI Property Consultant/
├── backend/                    # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── agents/            # Specialized agents
│   │   │   ├── parser.py      # NLP parser agent
│   │   │   ├── scraper.py     # Data scraper agent
│   │   │   ├── filter.py      # Filter & sort agent
│   │   │   ├── developer_intel.py  # Developer intel agent
│   │   │   ├── comparison.py  # Comparison agent
│   │   │   ├── recommendation.py # Recommendation agent
│   │   │   ├── orchestrator.py # Workflow orchestrator
│   │   │   └── context.py     # Shared context
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routes/            # API routes
│   │   ├── scrapers/          # Web scrapers
│   │   ├── config/            # Configuration
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/                   # Next.js React frontend
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   └── components/        # React components
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml         # Docker orchestration
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API Key

### Setup Environment Variables

1. **Backend** - Create `backend/.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ai_property_consultant
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4-turbo-preview
REDIS_URL=redis://localhost:6379
API_PORT=8000
DEBUG=False
```

2. **Frontend** - Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd "AI Property Consultant"

# Start all services
docker-compose up -d

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL
# Make sure PostgreSQL is running and create database:
# createdb -U user -p 5432 ai_property_consultant

# Run migrations (create tables)
python -c "from app.config import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Start backend
python run.py
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Visit http://localhost:3000
```

## 📡 API Documentation

### Endpoints

- **POST** `/api/chat` - Send message to chat agent
  ```json
  {
    "message": "I'm looking for a plot in South Bangalore...",
    "user_id": "optional_user_id",
    "session_id": "optional_session_id"
  }
  ```

- **WS** `/api/ws/chat/{session_id}` - WebSocket for real-time chat

- **GET** `/api/locations` - Get Bangalore divisions and areas

- **POST** `/api/search-by-location` - Search by map division
  ```json
  {
    "division": "South"
  }
  ```

### Response Format

```json
{
  "response": "Human readable response",
  "search_criteria": {
    "location": "Kanakapura",
    "min_size": 1200,
    "max_size": 1200,
    "min_price": 40000000,
    "max_price": 45000000
  },
  "properties": [
    {
      "id": 1,
      "name": "Property Name",
      "location": "Kanakapura",
      "area": 1200,
      "price": 42000000,
      "price_per_sqft": 35000
    }
  ],
  "reasoning": "These properties are recommended because...",
  "workflow_trace": {...}
}
```

## 🤖 Agent Workflow

### 1. Parser Agent
- Extracts: location, area, price range, property type
- Input: Natural language query
- Output: Structured search criteria

### 2. Scraper Agent
- Fetches approved layouts from planning authorities
- Input: Division/Location
- Output: List of approved projects

### 3. Filter & Sort Agent
- Filters projects by area (>5 acres)
- Sorts by approval date (most recent first)
- Output: Sorted list of top projects

### 4. Developer Intel Agent
- Gathers pricing from developer websites
- Extracts property specifications
- Output: Properties with pricing

### 5. Comparison Agent
- Scores properties based on:
  - Price competitiveness
  - Area optimization
  - RERA registration
  - Amenities
- Output: Top 5 ranked properties

### 6. Recommendation Agent
- Generates AI-powered reasoning
- Creates summary of recommendations
- Output: Final recommendations with explanation

## 💾 Database Schema

### Key Tables

- `properties` - Property listings
- `developers` - Developer information
- `layout_approvals` - Approved layouts from authorities
- `search_history` - User search history
- `agent_interactions` - Log of agent operations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `LLM_MODEL` | LLM model to use | gpt-4-turbo-preview |
| `REDIS_URL` | Redis connection string | redis://localhost:6379 |
| `API_PORT` | Backend API port | 8000 |
| `DEBUG` | Debug mode | False |

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Cloud Deployment (AWS/Azure)

Recommended setup:
- Backend: ECS Fargate / Container Apps
- Frontend: S3 + CloudFront / Static Web Apps
- Database: RDS PostgreSQL / Azure Database for PostgreSQL
- Cache: ElastiCache / Azure Cache for Redis

## 🔐 Security Considerations

1. Secure API endpoints with authentication
2. Rate limiting on chat endpoints
3. Input validation on all queries
4. HTTPS only in production
5. Secure credential management using env vars
6. SQL injection prevention via ORM
7. CORS properly configured

## 🚧 Future Enhancements

- [ ] User authentication & authorization
- [ ] Save favorite properties
- [ ] Price prediction models
- [ ] Historical data tracking
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Advanced filtering UI
- [ ] Property comparison tool
- [ ] RERA verification
- [ ] Legal document analysis

## 📝 Development Notes

### Adding New Agents

1. Create agent class in `backend/app/agents/`
2. Implement `async` methods following pattern
3. Update `AgentOrchestrator` in `orchestrator.py`
4. Add agent to workflow pipeline

### Adding New Data Sources

1. Create scraper in `backend/app/scrapers/`
2. Implement data fetching logic
3. Integrate with `ScraperAgent`
4. Add mappings to database models

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## 📄 License

MIT License

## 📞 Support

For issues and questions:
- Open GitHub issue
- Contact: support@aipropertyconsultant.com

## 👥 Team

- AI Architecture & Agents
- Full-stack Development
- DevOps & Deployment

---

**Last Updated**: January 3, 2026
**Version**: 0.1.0
