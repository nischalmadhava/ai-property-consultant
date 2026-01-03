@echo off
REM AI Property Consultant - Quick Start Script for Windows

setlocal enabledelayedexpansion

echo 🏠 AI Property Consultant - Quick Start
echo ========================================
echo.

REM Check if Docker is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose not found
    echo.
    echo Manual setup required. Follow these steps:
    echo.
    echo 1. Backend Setup:
    echo    cd backend
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo    copy .env.example .env
    echo    (Edit .env and add OPENAI_API_KEY)
    echo    python run.py
    echo.
    echo 2. Frontend Setup (in new terminal):
    echo    cd frontend
    echo    npm install
    echo    npm run dev
    echo.
    echo 3. Open http://localhost:3000 in your browser
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Compose found
echo.
echo Starting services with Docker Compose...
echo.

if not exist ".env" (
    echo ⚠️  .env file not found
    if exist "backend\.env.example" (
        copy backend\.env.example .env
        echo ✅ .env created. Please edit and add your OPENAI_API_KEY
        pause
        exit /b 1
    )
)

echo Starting Docker Compose...
docker-compose up -d

echo.
echo ✅ Services are starting...
echo.
timeout /t 5

echo.
echo 🎉 Ready to go!
echo.
echo Access points:
echo   🌐 Frontend:     http://localhost:3000
echo   📚 API Docs:     http://localhost:8000/docs
echo   🏥 Health:       http://localhost:8000/health
echo.
echo Commands:
echo   View logs:       docker-compose logs -f
echo   Stop services:   docker-compose down
echo.
pause
