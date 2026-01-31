"""Consumption records model for SQLite"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index, Text
from datetime import datetime
from app.core.database import Base


class ConsumptionRecord(Base):
    """
    Energy consumption record for UPTC sedes.
    Optimized for TimescaleDB time-series queries.
    """
    __tablename__ = "consumption_records"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Temporal data (indexed for TimescaleDB)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Location
    sede = Column(String(50), nullable=False, index=True)
    sede_id = Column(String(20), nullable=False)
    
    # Total energy metrics
    energia_total_kwh = Column(Float, nullable=False)
    potencia_total_kw = Column(Float)
    
    # Energy by sector
    energia_comedor_kwh = Column(Float)
    energia_salones_kwh = Column(Float)
    energia_laboratorios_kwh = Column(Float)
    energia_auditorios_kwh = Column(Float)
    energia_oficinas_kwh = Column(Float)
    
    # Water consumption
    agua_litros = Column(Float)
    
    # Environmental context
    temperatura_exterior_c = Column(Float)
    ocupacion_pct = Column(Float)
    
    # Temporal features
    hora = Column(Integer)  # 0-23
    dia_semana = Column(Integer)  # 0-6
    dia_nombre = Column(String(20))
    mes = Column(Integer)  # 1-12
    trimestre = Column(Integer)  # 1-4
    ano = Column(Integer)  # año sin tilde para compatibilidad
    
    # Academic context
    periodo_academico = Column(String(50))
    es_fin_semana = Column(Boolean, default=False)
    es_festivo = Column(Boolean, default=False)
    es_semana_parciales = Column(Boolean, default=False)
    es_semana_finales = Column(Boolean, default=False)
    
    # CO2 emissions
    co2_kg = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    source = Column(String(50), default="import")  # import, api, manual
    
    # Composite indexes for common queries
    __table_args__ = (
        # Most common: filter by sede and time range
        Index('ix_consumption_sede_timestamp', 'sede', 'timestamp'),
        # Descending timestamp for latest records
        Index('ix_consumption_timestamp_desc', timestamp.desc()),
        # By hour for pattern analysis
        Index('ix_consumption_sede_hora', 'sede', 'hora'),
        # Academic period analysis
        Index('ix_consumption_periodo', 'periodo_academico', 'sede'),
    )
    
    def __repr__(self):
        return f"<ConsumptionRecord(sede={self.sede}, timestamp={self.timestamp}, energia={self.energia_total_kwh})>"
