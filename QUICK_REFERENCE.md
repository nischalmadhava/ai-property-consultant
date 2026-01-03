# Quick Reference Guide

## 🚀 Quick Start Commands

### Start Everything (Docker)
```bash
cd "AI Property Consultant"
docker-compose up -d
```

### Stop Everything
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f          # All services
docker-compose logs -f backend  # Just backend
docker-compose logs -f frontend # Just frontend
```

### Backend Only (Local Dev)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Only (Local Dev)
```bash
cd frontend
npm install
npm run dev
```

## 📍 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main app |
| Backend API | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Swagger docs |
| API Redoc | http://localhost:8000/redoc | ReDoc docs |
| Health Check | http://localhost:8000/health | Server status |

## 🔌 API Endpoints

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Looking for a 30x40 plot in South Bangalore for 40 lakhs",
  "user_id": "user123",
  "session_id": "session123"
}
```

### Get Locations
```bash
GET /api/locations
```

### Map-Based Search
```bash
POST /api/search-by-location?division=South
```

### WebSocket Chat
```
WS ws://localhost:8000/api/ws/chat/session123
```

## 📁 Key File Locations

| File | Purpose |
|------|---------|
| `backend/app/agents/orchestrator.py` | Main workflow |
| `backend/app/routes/chat.py` | API endpoints |
| `backend/app/models/property.py` | Database models |
| `frontend/src/app/page.tsx` | Main page |
| `frontend/src/components/ChatInterface.tsx` | Chat UI |
| `docker-compose.yml` | Docker setup |

## 🔧 Common Tasks

### Add a New Agent

1. Create `backend/app/agents/new_agent.py`:
```python
from .context import SearchContext, AgentType

class NewAgent:
    async def process(self, context: SearchContext) -> SearchContext:
        try:
            # Your logic here
            context.add_workflow_step(
                AgentType.NEW_TYPE,
                "success",
                {"detail": "data"}
            )
        except Exception as e:
            context.add_workflow_step(
                AgentType.NEW_TYPE,
                "failed",
                {},
                str(e)
            )
        return context
```

2. Update `backend/app/agents/__init__.py`:
```python
from app.agents.new_agent import NewAgent
```

3. Use in `backend/app/agents/orchestrator.py`:
```python
self.new_agent = NewAgent()
# In process_query():
context = await self.new_agent.process(context)
```

### Change Database

Edit `backend/.env`:
```
DATABASE_URL=postgresql://new_user:password@new_host:5432/new_db
```

### Change LLM Model

Edit `backend/.env`:
```
LLM_MODEL=gpt-3.5-turbo  # or claude-3, etc
```

### Modify API Response

Edit `backend/app/agents/orchestrator.py` → `_format_response()` method

### Change Frontend Theme

Edit `frontend/tailwind.config.js`:
```javascript
colors: {
  primary: '#your-color',
  secondary: '#your-color',
}
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL
psql -U user -d ai_property_consultant -c "SELECT 1"

# Reset database
psql -U user
DROP DATABASE ai_property_consultant;
CREATE DATABASE ai_property_consultant;
```

### OpenAI API Error
```bash
# Verify key
echo $OPENAI_API_KEY

# Check account at https://platform.openai.com
```

### Frontend can't connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS in backend/app/config/settings.py
cors_origins: ["http://localhost:3000"]
```

## 📊 Database Queries

```bash
# Connect to DB
psql -U user -d ai_property_consultant

# List tables
\dt

# View properties
SELECT * FROM properties LIMIT 10;

# View search history
SELECT * FROM search_history;

# Count properties by division
SELECT division, COUNT(*) FROM properties GROUP BY division;
```

## 🔍 Debugging Tips

### Backend Logging
Add to agent methods:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

### Frontend Logging
```javascript
console.log("Debug:", variable);
console.error("Error:", error);
```

### View Full Workflow Trace
```bash
curl http://localhost:8000/docs
# Try the /api/chat endpoint, then check response workflow_trace
```

## 📈 Performance Tips

1. **Cache frequently searched areas**
   - Use Redis cache in ScraperAgent

2. **Batch LLM calls**
   - Process multiple queries together

3. **Database indexing**
   - Add indexes on division, location, price

4. **Frontend optimization**
   - Use React.memo for MapView divisions

## 🔐 Security Checklist

- [ ] Change default credentials
- [ ] Add HTTPS in production
- [ ] Use environment variables for secrets
- [ ] Add rate limiting to API
- [ ] Enable CORS for specific domains only
- [ ] Add authentication/authorization
- [ ] Validate user input
- [ ] Use prepared statements (ORM does this)

## 📦 Dependency Updates

```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

## 🧹 Cleanup Commands

```bash
# Stop and remove everything
docker-compose down -v

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Clean Node modules
rm -rf frontend/node_modules frontend/.next
```

## 📞 Getting Help

1. Check README.md for overview
2. Check SETUP.md for installation
3. Check ARCHITECTURE.md for design
4. Check API docs at /docs
5. Check logs: `docker-compose logs -f`

## 🎯 Development Workflow

```
1. Make changes (backend or frontend)
   └─ Backend auto-reloads in dev mode
   └─ Frontend hot-reloads with Next.js

2. Test changes
   └─ Backend: http://localhost:8000/docs
   └─ Frontend: http://localhost:3000

3. Check logs if issues
   └─ docker-compose logs -f

4. Commit changes
   └─ git add .
   └─ git commit -m "Feature: description"

5. Push to repo
   └─ git push origin branch-name
```

## 🎓 Learning Resources

- FastAPI: https://fastapi.tiangolo.com
- LangChain: https://python.langchain.com
- Next.js: https://nextjs.org
- SQLAlchemy: https://docs.sqlalchemy.org
- PostgreSQL: https://www.postgresql.org/docs
- Docker: https://docs.docker.com

## 💡 Tips & Tricks

### Run Single Agent Test
```python
from app.agents import ParserAgent
from app.agents.context import SearchContext

context = SearchContext(original_query="looking for 30x40 plot")
agent = ParserAgent()
result = await agent.parse(context)
print(result.to_dict())
```

### Test API Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I want a plot in Kanakapura", "user_id":"test"}'
```

### Access Database
```bash
docker-compose exec postgres psql -U user -d ai_property_consultant
```

### View Container Logs
```bash
docker logs -f ai_property_backend
```

---

**Last Updated**: January 3, 2026
**Version**: 0.1.0

