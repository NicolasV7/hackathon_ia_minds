"""Recommendation schemas"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any


class RecommendationBase(BaseModel):
    """Base recommendation schema"""
    sede: str = Field(..., max_length=50)
    sector: str = Field(..., max_length=50)
    
    category: str = Field(..., max_length=50)
    priority: str = Field(..., max_length=20)
    
    title: str = Field(..., max_length=200)
    description: str
    
    expected_savings_kwh: float = Field(..., ge=0)
    expected_savings_cop: float = Field(..., ge=0)
    expected_co2_reduction_kg: float = Field(..., ge=0)
    
    implementation_difficulty: Optional[str] = Field(None, max_length=20)
    actions: Optional[list[str]] = None
    status: str = "pending"


class RecommendationCreate(RecommendationBase):
    """Schema for creating recommendations"""
    anomaly_id: Optional[int] = None


class RecommendationUpdate(BaseModel):
    """Schema for updating recommendations"""
    status: Optional[str] = None
    implemented_at: Optional[datetime] = None


class RecommendationResponse(RecommendationBase):
    """Response schema for recommendations"""
    id: int
    anomaly_id: Optional[int] = None
    implemented_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationList(BaseModel):
    """List of recommendations"""
    recommendations: list[RecommendationResponse]
    total: int
    
    total_potential_savings_kwh: float = 0.0
    total_potential_savings_cop: float = 0.0
    total_co2_reduction_kg: float = 0.0


class RecommendationGenerationRequest(BaseModel):
    """Request for generating recommendations"""
    sede: str
    days: int = Field(7, ge=1, le=90)


class RecommendationStatusUpdate(BaseModel):
    """Update recommendation status"""
    status: str = Field(..., pattern="^(pending|in_progress|implemented|rejected)$")
    implementation_notes: Optional[str] = None
