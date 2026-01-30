"""Anomaly detection schemas"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict


class AnomalyBase(BaseModel):
    """Base anomaly schema"""
    timestamp: datetime
    sede: str = Field(..., max_length=50)
    sector: str = Field(..., max_length=50)
    
    anomaly_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    
    actual_value: float
    expected_value: float
    deviation_pct: float
    
    description: str
    recommendation: str
    potential_savings_kwh: float = 0.0
    status: str = "unresolved"


class AnomalyCreate(AnomalyBase):
    """Schema for creating anomalies"""
    pass


class AnomalyUpdate(BaseModel):
    """Schema for updating anomalies"""
    status: Optional[str] = None
    recommendation: Optional[str] = None


class AnomalyResponse(AnomalyBase):
    """Response schema for anomalies"""
    id: int
    detected_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnomalyList(BaseModel):
    """List of anomalies"""
    anomalies: list[AnomalyResponse]
    total: int
    page: int = 1
    page_size: int = 50


class AnomalySummaryResponse(BaseModel):
    """Summary statistics for anomalies"""
    sede: str
    total_anomalies: int
    by_severity: Dict[str, int] = Field(default_factory=dict)
    by_type: Dict[str, int] = Field(default_factory=dict)
    total_potential_savings_kwh: float = 0.0


class AnomalyDetectionRequest(BaseModel):
    """Request for detecting anomalies"""
    sede: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days: Optional[int] = Field(7, ge=1, le=365)
    severity_threshold: Optional[str] = None


class AnomalyStatusUpdate(BaseModel):
    """Update anomaly status"""
    status: str = Field(..., pattern="^(unresolved|investigating|resolved)$")
