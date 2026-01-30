"""
Main API v1 router that combines all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import predictions, anomalies, recommendations, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(predictions.router)
api_router.include_router(anomalies.router)
api_router.include_router(recommendations.router)
api_router.include_router(analytics.router)
