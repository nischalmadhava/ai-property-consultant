# Setup & Installation Guide

## Quick Start (5 minutes)

### Option A: Docker Compose (Easiest)

```bash
# 1. Set environment variables
export OPENAI_API_KEY="your-key-here"

# 2. Start all services
docker-compose up -d

# 3. Check if running
docker-compose ps

# 4. Open in browser
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

### Option B: Local Development

#### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your editor

# Install & start PostgreSQL
# On macOS with Homebrew:
brew install postgresql
brew services start postgresql

# On Windows, use PostgreSQL installer or Docker:
# docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres

# Create database
createdb -U postgres ai_property_consultant

# Update DATABASE_URL in .env if needed

# Initialize database
python -c "from app.config import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Start backend
python run.py

# Backend should be available at http://localhost:8000
```

#### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev

# Frontend should be available at http://localhost:3000
```

## Verify Installation

### Backend

1. Open http://localhost:8000/docs in browser
2. You should see Swagger API documentation
3. Try the `/health` endpoint

### Frontend

1. Open http://localhost:3000 in browser
2. You should see the AI Property Consultant interface
3. Try switching between Map View and Chat

## Troubleshooting

### PostgreSQL Connection Error

```bash
# Check if PostgreSQL is running
# On macOS:
brew services list | grep postgresql

# Start if not running:
brew services start postgresql

# On Linux:
sudo systemctl status postgresql
sudo systemctl start postgresql

# Check connection string in .env
```

### Redis Connection Error

```bash
# If using Redis (optional for production):
# Start Redis:
redis-server

# Or use Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### OpenAI API Error

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check your OpenAI account has API access
# https://platform.openai.com/account/api-keys
```

### Frontend can't connect to Backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/app/config/settings.py
# Make sure frontend URL is in cors_origins

# If using different port, update:
# frontend/.env.local -> NEXT_PUBLIC_API_URL
```

## Development Workflow

### Making Changes to Backend

```bash
# Changes auto-reload when using `python run.py`
# Backend watches for file changes

# If not auto-reloading:
# 1. Stop the server (Ctrl+C)
# 2. Make your changes
# 3. Run: python run.py
```

### Making Changes to Frontend

```bash
# Changes auto-reload automatically with Next.js
# Just edit files and save

# If you need to restart:
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Database Migrations

If you modify models in `backend/app/models/`, recreate tables:

```bash
# Drop and recreate all tables
python -c "
from app.config import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('Database reset and tables created!')
"
```

## Environment Variables Reference

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_property_consultant

# API
OPENAI_API_KEY=sk-xxxxxx
LLM_MODEL=gpt-4-turbo-preview

# Cache
REDIS_URL=redis://localhost:6379

# Server
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=False  # Set True for development
```

### Frontend (.env.local)

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Using Docker

### Build images locally

```bash
docker-compose build
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access containers

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend bash

# PostgreSQL
docker-compose exec postgres psql -U user -d ai_property_consultant
```

### Stop services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Next Steps

1. ✅ Backend is running
2. ✅ Frontend is running
3. 📖 Read [README.md](README.md) for project overview
4. 🧪 Try the chat interface
5. 🗺️ Try the map interface
6. 📚 Check API docs at /docs

## Need Help?

1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all ports are available (3000, 8000, 5432, 6379)
4. Check OpenAI API key is valid
5. Try restarting services: `docker-compose restart`

---

**Happy coding! 🚀**
