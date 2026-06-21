import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GIS Visual ETL Platform"
    API_V1_STR: str = "/api"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "my_jwt_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://etl_user:etl_password@localhost:5432/etl_db"
    )
    DEBUG_AUTH: bool = os.getenv("DEBUG_AUTH", "true").lower() == "true"
    
    INTERMEDIATE_STORAGE_PATH: str = os.getenv(
        "INTERMEDIATE_STORAGE_PATH", "./tmp/etl_cache"
    )

    class Config:
        case_sensitive = True

settings = Settings()
