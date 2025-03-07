import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Boti API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "changeme_please_this_is_insecure")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days by default
    JWT_ALGORITHM: str = "HS256"
    
    # Supabase
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()