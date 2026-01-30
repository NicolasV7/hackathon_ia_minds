"""Anomaly detection records model"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base


class Anomaly(Base):
    """
    Detected energy consumption anomalies.
    Records inefficient patterns and potential savings.
    """
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # When was anomaly detected
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # When did anomaly occur
    anomaly_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Location
    sede = Column(String(50), nullable=False, index=True)
    sector = Column(String(50), nullable=False)  # comedor, salones, etc.
    
    # Anomaly classification
    anomaly_type = Column(String(50), nullable=False, index=True)  # off_hours_usage, consumption_spike, etc.
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    # Consumption data
    observed_value_kwh = Column(Float, nullable=False)
    expected_value_kwh = Column(Float, nullable=False)
    deviation_kwh = Column(Float, nullable=False)
    deviation_percentage = Column(Float, nullable=False)
    
    # Scoring
    anomaly_score = Column(Float)  # From model (e.g., Isolation Forest score)
    z_score = Column(Float)  # Statistical z-score
    
    # Impact assessment
    potential_savings_kwh = Column(Float)
    potential_savings_cop = Column(Float)
    co2_impact_kg = Column(Float)
    
    # Description and recommendations
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    
    # Detection method
    detection_method = Column(String(50))  # isolation_forest, z_score, business_rule
    detector_version = Column(String(20), default="1.0.0")
    
    # Additional context
    context_data = Column(JSONB)  # Store relevant context (temperature, occupancy, etc.)
    
    # Status tracking
    status = Column(String(20), default="open")  # open, acknowledged, resolved, false_positive
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_anomaly_sede_severity', 'sede', 'severity'),
        Index('ix_anomaly_type_status', 'anomaly_type', 'status'),
        Index('ix_anomaly_timestamp_desc', anomaly_timestamp.desc()),
    )
    
    def __repr__(self):
        return f"<Anomaly(type={self.anomaly_type}, sede={self.sede}, severity={self.severity})>"
