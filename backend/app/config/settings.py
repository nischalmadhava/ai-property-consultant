from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ai_property_consultant")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Scraping
    scraper_timeout: int = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    scraper_retries: int = int(os.getenv("SCRAPER_RETRIES", "3"))
    scraper_delay: float = float(os.getenv("SCRAPER_DELAY", "2"))
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
