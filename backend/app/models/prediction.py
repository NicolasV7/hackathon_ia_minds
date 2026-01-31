"""Prediction records model - Updated for CO2 and Energy models"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean, Text
from datetime import datetime
from app.core.database import Base


class Prediction(Base):
    """
    Energy consumption and CO2 predictions.
    Stores predictions made by ML models with metadata.
    
    Models used:
    - modelo_co2.pkl (LightGBM) - Predicts CO2 emissions
    - modelo_energia_B2.pkl (Ridge) - Predicts energy consumption
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # When was the prediction made
    prediction_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Target timestamp (legacy field from old model, kept for backward compatibility)
    target_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Location
    sede = Column(String(50), nullable=False, index=True)
    sector = Column(String(50), nullable=True)  # Legacy field
    
    # Prediction results - CO2
    predicted_co2_kg = Column(Float, nullable=True)
    confidence_co2 = Column(Float, default=0.893)  # R² score
    
    # Prediction results - Energy
    predicted_energy_kwh = Column(Float, nullable=True)
    confidence_energy = Column(Float, default=0.998)  # R² score
    
    # Legacy field for backwards compatibility
    predicted_kwh = Column(Float, nullable=True)  # Same as predicted_energy_kwh
    
    # Input values stored for reference
    energia_comedor_kwh = Column(Float)
    energia_salones_kwh = Column(Float)
    energia_laboratorios_kwh = Column(Float)
    energia_auditorios_kwh = Column(Float)
    energia_oficinas_kwh = Column(Float)
    agua_litros = Column(Float)
    temperatura_exterior_c = Column(Float)
    ocupacion_pct = Column(Float)
    
    # Context flags
    es_festivo = Column(Boolean, default=False)
    es_semana_parciales = Column(Boolean, default=False)
    es_semana_finales = Column(Boolean, default=False)
    
    # Model metadata
    model_version = Column(String(50), default="2.0.0")
    model_type_co2 = Column(String(50), default="LightGBM")
    model_type_energy = Column(String(50), default="Ridge")
    
    # Actual values (filled later for evaluation)
    actual_co2_kg = Column(Float)
    actual_energy_kwh = Column(Float)
    actual_recorded_at = Column(DateTime(timezone=True))
    
    # Evaluation metrics for CO2
    co2_prediction_error = Column(Float)
    co2_absolute_error = Column(Float)
    co2_percentage_error = Column(Float)
    
    # Evaluation metrics for Energy
    energy_prediction_error = Column(Float)
    energy_absolute_error = Column(Float)
    energy_percentage_error = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(String(500))
    
    def __repr__(self):
        return f"<Prediction(sede={self.sede}, co2={self.predicted_co2_kg}kg, energy={self.predicted_energy_kwh}kWh)>"
