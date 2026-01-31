"""
UPTC EcoEnergy - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.database import init_db, close_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Runs on startup and shutdown.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    
    # Initialize database
    if settings.DEBUG:
        await init_db()
        logger.info("Database initialized")
    
    # Load ML models (CO2 and Energy models from newmodels/)
    try:
        from pathlib import Path
        from app.ml.inference import ml_service
        from app.core.config import get_settings
        
        ml_settings = get_settings()
        ml_service.models_path = Path(ml_settings.ML_MODELS_PATH)
        
        logger.info(f"Loading ML models from: {ml_service.models_path}")
        ml_service.load_models()
        
        # Log model info
        model_info = ml_service.get_model_info()
        logger.info(f"CO2 Model: {model_info['co2_model']}")
        logger.info(f"Energy Model: {model_info['energy_model']}")
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        logger.warning("Application will continue but predictions will not work")
        # Continue anyway for development
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered energy efficiency system for UPTC",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse({
        "status": "healthy",
        "version": settings.VERSION,
        "app": settings.APP_NAME
    })


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": f"/docs",
        "api": settings.API_V1_STR
    }


# Include API routers (will be added next)
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
