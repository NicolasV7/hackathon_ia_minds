"""SQLAlchemy database models"""
from app.models.consumption import ConsumptionRecord
from app.models.prediction import Prediction
from app.models.anomaly import Anomaly
from app.models.recommendation import Recommendation

__all__ = [
    "ConsumptionRecord",
    "Prediction",
    "Anomaly",
    "Recommendation",
]
