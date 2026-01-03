from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, engine, Base
from app.routes.chat import router as chat_router
from app.models import Property, Developer, LayoutApproval, SearchHistory, AgentInteraction

# Create tables
Base.metadata.create_all(bind=engine)

def create_app():
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AI Property Consultant API",
        description="AI Agentic workflow for property search in Bangalore",
        version="0.1.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "AI Property Consultant",
            "version": "0.1.0"
        }
    
    @app.get("/")
    async def root():
        return {
            "message": "AI Property Consultant API",
            "docs_url": "/docs",
            "version": "0.1.0"
        }
    
    return app

if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
