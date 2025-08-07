import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "CognitiveAmplifier"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    
    # VectorDB
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    VECTOR_COLLECTION: str = "note_vectors"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    MASTER_ENCRYPTION_KEY: bytes = os.getenv("MASTER_ENCRYPTION_KEY", Fernet.generate_key()).encode()
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_BACKEND", "redis://localhost:6379/1")
    
    # AI Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    TITLE_GENERATION_MODEL: str = "gpt2"
    
    # OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    
    # OAuth URLs
    GOOGLE_AUTHORIZE_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    GITHUB_AUTHORIZE_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_USERINFO_URL: str = "https://api.github.com/user"
    
    # Application URLs
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
    FRONTEND_REDIRECT_URI: str = os.getenv("FRONTEND_REDIRECT_URI", "http://localhost:3000")
    
    # Pydantic V2 configuration
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()