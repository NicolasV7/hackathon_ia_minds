"""Pydantic schemas for API request/response validation"""
from app.schemas.consumption import (
    ConsumptionBase,
    ConsumptionCreate,
    ConsumptionResponse,
    ConsumptionList,
)
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionList,
    PredictionCreate,
    PredictionUpdate,
    CO2PredictionRequest,
    CO2PredictionResponse,
    EnergyPredictionRequest,
    EnergyPredictionResponse,
    PredictionBatchRequest,
    PredictionBatchResponse,
    ModelInfoResponse,
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
    "PredictionRequest",
    "PredictionResponse",
    "PredictionList",
    "PredictionCreate",
    "PredictionUpdate",
    "CO2PredictionRequest",
    "CO2PredictionResponse",
    "EnergyPredictionRequest",
    "EnergyPredictionResponse",
    "PredictionBatchRequest",
    "PredictionBatchResponse",
    "ModelInfoResponse",
    "AnomalyBase",
    "AnomalyResponse",
    "AnomalySummaryResponse",
    "RecommendationBase",
    "RecommendationResponse",
    "RecommendationList",
]
