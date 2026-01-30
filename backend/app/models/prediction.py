"""Prediction records model"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base


class Prediction(Base):
    """
    Energy consumption predictions.
    Stores predictions made by ML models with metadata.
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # When was the prediction made
    prediction_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # What timestamp is being predicted
    target_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Location
    sede = Column(String(50), nullable=False, index=True)
    sector = Column(String(50))  # Optional: specific sector prediction
    
    # Prediction results
    predicted_kwh = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    prediction_error_estimated = Column(Float)  # Expected error based on model metrics
    
    # Model metadata
    model_version = Column(String(50), default="1.0.0")
    model_type = Column(String(50), default="xgboost")
    features_used = Column(JSONB)  # Store feature names and values
    
    # Horizon (hours ahead)
    horizon_hours = Column(Integer)
    
    # Actual value (filled later for evaluation)
    actual_kwh = Column(Float)
    actual_recorded_at = Column(DateTime(timezone=True))
    
    # Evaluation metrics (computed after actual value known)
    prediction_error = Column(Float)  # actual - predicted
    absolute_error = Column(Float)  # abs(actual - predicted)
    percentage_error = Column(Float)  # (actual - predicted) / actual * 100
    is_accurate = Column(Boolean)  # within threshold
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(String(500))
    
    def __repr__(self):
        return f"<Prediction(sede={self.sede}, target={self.target_timestamp}, predicted={self.predicted_kwh})>"
