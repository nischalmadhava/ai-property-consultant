from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ai_property_consultant"
    
    # OpenAI
    openai_api_key: str = ""
    llm_model: str = "gpt-4-turbo-preview"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    debug: bool = False
    
    # Scraping
    scraper_timeout: int = 30
    scraper_retries: int = 3
    scraper_delay: float = 2.0
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]

settings = Settings()
