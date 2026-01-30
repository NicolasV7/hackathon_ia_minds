"""Pydantic schemas for API request/response validation"""
from app.schemas.consumption import (
    ConsumptionBase,
    ConsumptionCreate,
    ConsumptionResponse,
    ConsumptionList,
)
from app.schemas.prediction import (
    PredictionBase,
    PredictionRequest,
    PredictionResponse,
    PredictionList,
)
from app.schemas.anomaly import (
    AnomalyBase,
    AnomalyResponse,
    AnomalySummaryResponse,
)
from app.schemas.recommendation import (
    RecommendationBase,
    RecommendationResponse,
    RecommendationList,
)

__all__ = [
    "ConsumptionBase",
    "ConsumptionCreate",
    "ConsumptionResponse",
    "ConsumptionList",
    "PredictionBase",
    "PredictionRequest",
    "PredictionResponse",
    "PredictionList",
    "AnomalyBase",
    "AnomalyResponse",
    "AnomalySummaryResponse",
    "RecommendationBase",
    "RecommendationResponse",
    "RecommendationList",
]
