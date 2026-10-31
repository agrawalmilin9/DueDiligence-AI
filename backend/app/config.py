import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from the backend folder if present
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "DueDiligence AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001",
        ).split(",")
        if origin.strip()
    ]

    # Crustdata API configuration (Service module integration)
    CRUSTDATA_API_KEY: str = os.getenv("CRUSTDATA_API_KEY", "")
    CRUSTDATA_BASE_URL: str = os.getenv("CRUSTDATA_BASE_URL", "https://api.crustdata.com")

    # Research & AI APIs configuration
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
