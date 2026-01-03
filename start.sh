#!/bin/bash

# AI Property Consultant - Quick Start Script
# This script helps you get started with the project

set -e

echo "🏠 AI Property Consultant - Quick Start"
echo "========================================"
echo ""

# Check if Docker is installed
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose found"
    echo ""
    echo "Starting services with Docker Compose..."
    echo ""
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found"
        echo "Creating .env from template..."
        
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example .env
            echo "✅ .env created. Please edit and add your OPENAI_API_KEY"
            exit 1
        fi
    fi
    
    echo "Starting Docker Compose..."
    docker-compose up -d
    
    echo ""
    echo "✅ Services are starting..."
    echo ""
    echo "Waiting for services to be healthy..."
    sleep 5
    
    echo ""
    echo "🎉 Ready to go!"
    echo ""
    echo "Access points:"
    echo "  🌐 Frontend:     http://localhost:3000"
    echo "  📚 API Docs:     http://localhost:8000/docs"
    echo "  🏥 Health:       http://localhost:8000/health"
    echo ""
    echo "Commands:"
    echo "  View logs:       docker-compose logs -f"
    echo "  Stop services:   docker-compose down"
    echo ""
    
else
    echo "❌ Docker Compose not found"
    echo ""
    echo "Manual setup required. Follow these steps:"
    echo ""
    echo "1. Backend Setup:"
    echo "   cd backend"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
    echo "   pip install -r requirements.txt"
    echo "   cp .env.example .env"
    echo "   # Edit .env and add OPENAI_API_KEY"
    echo "   python run.py"
    echo ""
    echo "2. Frontend Setup (in new terminal):"
    echo "   cd frontend"
    echo "   npm install"
    echo "   npm run dev"
    echo ""
    echo "3. Open http://localhost:3000 in your browser"
    echo ""
fi
