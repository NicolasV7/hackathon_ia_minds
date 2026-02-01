"""
Prediction schemas for CO2 and Energy models.
Updated to support new ML models from newmodels/ folder.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SedeEnum(str, Enum):
    """Valid sede values"""
    TUNJA = "Tunja"
    DUITAMA = "Duitama"
    SOGAMOSO = "Sogamoso"


class PeriodoAcademicoEnum(str, Enum):
    """Valid periodo academico values"""
    SEMESTRE_1 = "semestre_1"
    SEMESTRE_2 = "semestre_2"
    VACACIONES = "vacaciones"
    VACACIONES_FIN = "vacaciones_fin"
    VACACIONES_MITAD = "vacaciones_mitad"


class PredictionRequest(BaseModel):
    """
    Request schema for creating predictions.
    Contains all necessary inputs for CO2 and Energy models.
    """
    # Timestamp for prediction (optional, defaults to now)
    timestamp: Optional[datetime] = None
    
    # Energy consumption by area (required)
    energia_comedor_kwh: float = Field(..., ge=0, description="Energy consumption in dining area (kWh)")
    energia_salones_kwh: float = Field(..., ge=0, description="Energy consumption in classrooms (kWh)")
    energia_laboratorios_kwh: float = Field(..., ge=0, description="Energy consumption in labs (kWh)")
    energia_auditorios_kwh: float = Field(..., ge=0, description="Energy consumption in auditoriums (kWh)")
    energia_oficinas_kwh: float = Field(..., ge=0, description="Energy consumption in offices (kWh)")
    
    # Other variables
    agua_litros: float = Field(..., ge=0, description="Water consumption in liters")
    temperatura_exterior_c: float = Field(..., description="Exterior temperature in Celsius")
    ocupacion_pct: float = Field(..., ge=0, le=100, description="Occupancy percentage (0-100)")
    
    # Location
    sede: SedeEnum = Field(..., description="Campus location")
    
    # Academic flags (optional, can be auto-calculated)
    es_festivo: bool = Field(False, description="Is holiday")
    es_semana_parciales: bool = Field(False, description="Is midterm week")
    es_semana_finales: bool = Field(False, description="Is finals week")
    
    # Optional: override periodo academico (otherwise auto-calculated from timestamp)
    periodo_academico: Optional[PeriodoAcademicoEnum] = None
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def set_default_timestamp(cls, v):
        return v or datetime.now()


class PredictionResponse(BaseModel):
    """Response schema for combined CO2 and Energy predictions"""
    id: Optional[int] = None
    
    # Input context
    sede: str
    prediction_timestamp: Optional[datetime] = None
    timestamp: Optional[datetime] = None  # Alias for API response
    
    # Predictions
    predicted_co2_kg: Optional[float] = Field(None, description="Predicted CO2 emissions in kg")
    predicted_energy_kwh: Optional[float] = Field(None, description="Predicted total energy consumption in kWh")
    
    # Confidence scores based on model R² metrics
    confidence_co2: Optional[float] = Field(0.893, description="Model confidence for CO2 (R² = 0.893)")
    confidence_energy: Optional[float] = Field(0.998, description="Model confidence for Energy (R² = 0.998)")
    
    # Model metrics (for reference)
    metrics: Optional[dict] = Field(
        default={
            "co2": {"R2": 0.893, "MAE": 0.153},
            "energy": {"R2": 0.998, "MAE": 0.014}
        },
        description="Model performance metrics"
    )
    
    # Original inputs (for verification)
    energia_comedor_kwh: Optional[float] = None
    energia_salones_kwh: Optional[float] = None
    energia_laboratorios_kwh: Optional[float] = None
    energia_auditorios_kwh: Optional[float] = None
    energia_oficinas_kwh: Optional[float] = None
    agua_litros: Optional[float] = None
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = None
    
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    @model_validator(mode='after')
    def set_timestamp_from_prediction_timestamp(self):
        if self.timestamp is None and self.prediction_timestamp is not None:
            self.timestamp = self.prediction_timestamp
        return self


class CO2PredictionRequest(BaseModel):
    """Request schema specifically for CO2 prediction only"""
    timestamp: Optional[datetime] = None
    
    energia_comedor_kwh: float = Field(..., ge=0)
    energia_salones_kwh: float = Field(..., ge=0)
    energia_laboratorios_kwh: float = Field(..., ge=0)
    energia_auditorios_kwh: float = Field(..., ge=0)
    energia_oficinas_kwh: float = Field(..., ge=0)
    agua_litros: float = Field(..., ge=0)
    temperatura_exterior_c: float
    ocupacion_pct: float = Field(..., ge=0, le=100)
    sede: SedeEnum
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False
    periodo_academico: Optional[PeriodoAcademicoEnum] = None
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def set_default_timestamp(cls, v):
        return v or datetime.now()


class CO2PredictionResponse(BaseModel):
    """Response schema for CO2 prediction only"""
    predicted_co2_kg: float
    confidence: float = 0.893
    timestamp: datetime
    sede: str
    info: dict = Field(
        default={"type": "LightGBM", "R2": 0.893, "MAE": 0.153}
    )
    
    model_config = ConfigDict(from_attributes=True)


class EnergyPredictionRequest(BaseModel):
    """
    Request schema for Energy B2 prediction.
    Note: Requires co2_kg which can be predicted first using CO2 model.
    """
    timestamp: Optional[datetime] = None
    reading_id: int = Field(..., description="Unique reading identifier")
    
    energia_comedor_kwh: float = Field(..., ge=0)
    energia_salones_kwh: float = Field(..., ge=0)
    energia_laboratorios_kwh: float = Field(..., ge=0)
    energia_auditorios_kwh: float = Field(..., ge=0)
    energia_oficinas_kwh: float = Field(..., ge=0)
    agua_litros: float = Field(..., ge=0)
    temperatura_exterior_c: float
    ocupacion_pct: float = Field(..., ge=0, le=100)
    co2_kg: float = Field(..., ge=0, description="CO2 emissions in kg (can be predicted first)")
    sede: SedeEnum
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False
    periodo_academico: Optional[PeriodoAcademicoEnum] = None
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def set_default_timestamp(cls, v):
        return v or datetime.now()


class EnergyPredictionResponse(BaseModel):
    """Response schema for Energy prediction only"""
    predicted_energy_kwh: float
    confidence: float = 0.998
    timestamp: datetime
    sede: str
    co2_kg_used: float
    info: dict = Field(
        default={"type": "Ridge", "R2": 0.998, "MAE": 0.014}
    )
    
    model_config = ConfigDict(from_attributes=True)


class PredictionBatchRequest(BaseModel):
    """Request for batch predictions"""
    predictions: List[PredictionRequest]


class PredictionBatchResponse(BaseModel):
    """Response for batch predictions"""
    predictions: List[PredictionResponse]
    total: int
    successful: int
    failed: int


class PredictionCreate(BaseModel):
    """Schema for creating predictions in DB"""
    sede: str
    prediction_timestamp: datetime
    predicted_co2_kg: float
    predicted_energy_kwh: float
    predicted_kwh: Optional[float] = None  # Legacy field for backwards compatibility
    confidence_co2: float = 0.893
    confidence_energy: float = 0.998
    
    # Input values stored for reference
    energia_comedor_kwh: Optional[float] = None
    energia_salones_kwh: Optional[float] = None
    energia_laboratorios_kwh: Optional[float] = None
    energia_auditorios_kwh: Optional[float] = None
    energia_oficinas_kwh: Optional[float] = None
    agua_litros: Optional[float] = None
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = None
    es_festivo: bool = False
    es_semana_parciales: bool = False
    es_semana_finales: bool = False


class PredictionUpdate(BaseModel):
    """Schema for updating predictions"""
    predicted_co2_kg: Optional[float] = None
    predicted_energy_kwh: Optional[float] = None


class PredictionList(BaseModel):
    """List of predictions"""
    predictions: List[PredictionResponse]
    total: int
    
    # Aggregated metrics
    total_predicted_co2_kg: Optional[float] = None
    total_predicted_energy_kwh: Optional[float] = None
    avg_predicted_co2_kg: Optional[float] = None
    avg_predicted_energy_kwh: Optional[float] = None


class PredictionMetrics(BaseModel):
    """Metrics for prediction accuracy"""
    total_predictions: int
    predictions_with_actuals: int
    
    # CO2 model metrics
    co2_mean_absolute_error: Optional[float] = None
    co2_r2_score: Optional[float] = None
    
    # Energy model metrics
    energy_mean_absolute_error: Optional[float] = None
    energy_r2_score: Optional[float] = None
    
    by_sede: dict[str, dict[str, float]] = Field(default_factory=dict)


class ModelInfoResponse(BaseModel):
    """Response with model information"""
    models_loaded: bool
    co2_model: dict = Field(
        default={
            "name": "modelo_co2.pkl",
            "type": "LightGBM",
            "target": "co2_kg",
            "features": 33,
            "R2": 0.893,
            "MAE": 0.153
        }
    )
    energy_model: dict = Field(
        default={
            "name": "modelo_energia_B2.pkl", 
            "type": "Ridge",
            "target": "energia_total_kwh",
            "features": 35,
            "R2": 0.998,
            "MAE": 0.014
        }
    )
    preprocessing: dict = Field(
        default={
            "scaler": "scaler.pkl",
            "power_transformer": "power_transformer.pkl"
        }
    )
