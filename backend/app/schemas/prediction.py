"""Prediction schemas"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any


class PredictionBase(BaseModel):
    """Base prediction schema"""
    target_timestamp: datetime
    sede: str = Field(..., max_length=50)
    sector: Optional[str] = Field(None, max_length=50)


class PredictionRequest(BaseModel):
    """Request schema for creating predictions"""
    timestamp: datetime
    sede: str
    temperatura_exterior_c: float = 20.0
    ocupacion_pct: float = 70.0
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False


class PredictionCreate(BaseModel):
    """Schema for creating predictions in DB"""
    sede: str
    prediction_timestamp: datetime
    predicted_kwh: float
    confidence_score: float
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = None
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False


class PredictionUpdate(BaseModel):
    """Schema for updating predictions"""
    predicted_kwh: Optional[float] = None
    confidence_score: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    id: int
    sede: str
    prediction_timestamp: datetime
    predicted_kwh: float
    confidence_score: float
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = None
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PredictionList(BaseModel):
    """List of predictions"""
    predictions: list[PredictionResponse]
    total: int
    
    # Aggregated metrics
    total_predicted_kwh: Optional[float] = None
    avg_predicted_kwh: Optional[float] = None


class PredictionBatchRequest(BaseModel):
    """Request for batch predictions"""
    sede: str
    start_timestamp: datetime
    horizon_hours: int = Field(24, ge=1, le=168)
    temperatura_exterior_c: float = 20.0
    ocupacion_pct: float = 70.0
    
    
class PredictionMetrics(BaseModel):
    """Metrics for prediction accuracy"""
    total_predictions: int
    predictions_with_actuals: int
    
    mean_absolute_error: Optional[float] = None
    root_mean_squared_error: Optional[float] = None
    mean_absolute_percentage_error: Optional[float] = None
    r2_score: Optional[float] = None
    
    by_sede: dict[str, dict[str, float]] = Field(default_factory=dict)
