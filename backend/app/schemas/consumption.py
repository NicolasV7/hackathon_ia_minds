"""Consumption data schemas"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ConsumptionBase(BaseModel):
    """Base consumption schema"""
    timestamp: datetime
    sede: str = Field(..., max_length=50)
    sede_id: str = Field(..., max_length=20)
    
    energia_total_kwh: float = Field(..., ge=0)
    potencia_total_kw: Optional[float] = Field(None, ge=0)
    
    energia_comedor_kwh: Optional[float] = Field(None, ge=0)
    energia_salones_kwh: Optional[float] = Field(None, ge=0)
    energia_laboratorios_kwh: Optional[float] = Field(None, ge=0)
    energia_auditorios_kwh: Optional[float] = Field(None, ge=0)
    energia_oficinas_kwh: Optional[float] = Field(None, ge=0)
    
    agua_litros: Optional[float] = Field(None, ge=0)
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = Field(None, ge=0, le=100)
    
    co2_kg: Optional[float] = Field(None, ge=0)


class ConsumptionCreate(ConsumptionBase):
    """Schema for creating consumption records"""
    pass


class ConsumptionUpdate(BaseModel):
    """Schema for updating consumption records"""
    energia_total_kwh: Optional[float] = None
    temperatura_exterior_c: Optional[float] = None
    ocupacion_pct: Optional[float] = None


class ConsumptionResponse(ConsumptionBase):
    """Schema for consumption response"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConsumptionList(BaseModel):
    """Paginated list of consumption records"""
    items: list[ConsumptionResponse]
    total: int
    page: int = 1
    page_size: int = 50
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


class ConsumptionStats(BaseModel):
    """Statistics for consumption data"""
    sede: str
    start_date: datetime
    end_date: datetime
    
    total_kwh: float
    avg_kwh: float
    max_kwh: float
    min_kwh: float
    
    total_co2_kg: float
    
    by_sector: dict[str, float] = Field(default_factory=dict)
