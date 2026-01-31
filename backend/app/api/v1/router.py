"""
Main API v1 router that combines all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    predictions,
    anomalies,
    recommendations,
    analytics,
    db_check,
    models,
    sedes,
    chat,
    optimization,
    alerts,
    explainability
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(predictions.router)
api_router.include_router(anomalies.router)
api_router.include_router(recommendations.router)
api_router.include_router(analytics.router)
api_router.include_router(db_check.router)

# New endpoints for frontend
api_router.include_router(models.router)
api_router.include_router(sedes.router)
api_router.include_router(chat.router)
api_router.include_router(optimization.router)
api_router.include_router(alerts.router)
api_router.include_router(explainability.router)
