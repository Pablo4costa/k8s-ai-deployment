from dotenv import load_dotenv
load_dotenv()

import os

class Settings:
    # API
    APP_NAME: str = "Enterprise AI Gateway"
    VERSION: str = "1.0.0"

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # LLM Providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))

settings = Settings()