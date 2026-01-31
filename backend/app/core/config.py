"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "UPTC EcoEnergy API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Database - SQLite by default (use absolute path in Docker)
    DATABASE_URL: str = "sqlite+aiosqlite:///app/data/uptc_energy.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # CORS - comma-separated string
    CORS_ORIGINS_STR: str = "http://localhost:3000"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    # ML Models - Nuevos modelos de predicción
    ML_MODELS_PATH: str = "./newmodels"
    
    # Archivos de modelos
    MODEL_CO2_FILE: str = "modelo_co2.pkl"
    MODEL_ENERGIA_B2_FILE: str = "modelo_energia_B2.pkl"
    SCALER_FILE: str = "scaler.pkl"
    POWER_TRANSFORMER_FILE: str = "power_transformer.pkl"
    
    # OpenAI (optional)
    OPENAI_API_KEY: str | None = None
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
