import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://transitflow:transitflow@localhost:5432/transitflow"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TransitFlow"
    
    # Model
    MODEL_PATH: str = "data/crowd_predictor.pkl"
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"


settings = Settings()
