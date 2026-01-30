"""Recommendations model"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean, Text, Index, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base


class Recommendation(Base):
    """
    Energy efficiency recommendations.
    Generated from anomaly analysis and consumption patterns.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Generation metadata
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Location
    sede = Column(String(50), nullable=False, index=True)
    sector = Column(String(50), nullable=False)
    
    # Classification
    category = Column(String(50), nullable=False)  # behavioral, equipment, scheduling, automation, maintenance
    priority = Column(String(20), nullable=False, index=True)  # low, medium, high, urgent
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)  # Why this recommendation
    
    # Impact estimation
    expected_savings_kwh = Column(Float, nullable=False)
    expected_savings_cop = Column(Float, nullable=False)
    expected_co2_reduction_kg = Column(Float, nullable=False)
    
    # Implementation details
    implementation_difficulty = Column(String(20))  # easy, medium, hard
    estimated_cost_cop = Column(Float)
    payback_period_months = Column(Integer)
    
    # Actions (stored as JSON array)
    actions = Column(JSONB)  # List of specific actions
    
    # Source tracking
    generated_from_anomalies = Column(JSONB)  # Array of anomaly IDs
    generation_method = Column(String(50))  # rule_based, llm_enhanced
    model_version = Column(String(20))
    
    # Status tracking
    status = Column(String(20), default="active")  # active, implemented, dismissed, expired
    implemented_at = Column(DateTime(timezone=True))
    implementation_notes = Column(Text)
    
    # Actual impact (if implemented and measured)
    actual_savings_kwh = Column(Float)
    actual_savings_cop = Column(Float)
    measurement_period_days = Column(Integer)
    
    # User interaction
    views_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True))  # Recommendations can expire
    
    # Indexes
    __table_args__ = (
        Index('ix_recommendation_sede_priority', 'sede', 'priority'),
        Index('ix_recommendation_status', 'status'),
        Index('ix_recommendation_category', 'category'),
    )
    
    def __repr__(self):
        return f"<Recommendation(title={self.title}, sede={self.sede}, priority={self.priority})>"
