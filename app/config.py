import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoCrop-NE Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = "Agricultural Intelligence, SAR Radar Fusion, and Yield Forecasting Engine for Assam (NESFIC-D-12 / ASSAC)"
    
    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"
    ]
    
    # File storage paths
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
