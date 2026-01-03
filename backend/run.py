#!/usr/bin/env python
import os
import sys
from app.main import create_app
import uvicorn

if __name__ == "__main__":
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "app.main:create_app",
        host=host,
        port=port,
        reload=debug,
        factory=True
    )
