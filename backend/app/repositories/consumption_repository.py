"""
Repository for consumption data operations.
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consumption import ConsumptionRecord
from app.schemas.consumption import ConsumptionCreate, ConsumptionUpdate
from .base_repository import BaseRepository


class ConsumptionRepository(BaseRepository[ConsumptionRecord, ConsumptionCreate, ConsumptionUpdate]):
    """
    Repository for consumption records with specialized queries.
    """
    
    def __init__(self):
        super().__init__(ConsumptionRecord)
    
    async def get_by_sede_and_date_range(
        self,
        db: AsyncSession,
        sede: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 1000
    ) -> List[ConsumptionRecord]:
        """
        Get consumption records for a sede within a date range.
        
        Args:
            db: Database session
            sede: Sede name
            start_date: Start datetime
            end_date: End datetime
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of consumption records
        """
        query = select(self.model).where(
            and_(
                self.model.sede == sede,
                self.model.timestamp >= start_date,
                self.model.timestamp <= end_date
            )
        ).order_by(self.model.timestamp.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        limit: int = 168  # Last week by default
    ) -> List[ConsumptionRecord]:
        """
        Get the most recent consumption records for a sede.
        
        Args:
            db: Database session
            sede: Sede name
            limit: Number of records to retrieve
            
        Returns:
            List of consumption records ordered by timestamp desc
        """
        query = select(self.model).where(
            self.model.sede == sede
        ).order_by(self.model.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_statistics(
        self,
        db: AsyncSession,
        sede: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get consumption statistics for a sede or all sedes.
        
        Args:
            db: Database session
            sede: Optional sede filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with statistics
        """
        query = select(
            func.avg(self.model.energia_total_kwh).label('avg_consumption'),
            func.sum(self.model.energia_total_kwh).label('total_consumption'),
            func.max(self.model.energia_total_kwh).label('max_consumption'),
            func.min(self.model.energia_total_kwh).label('min_consumption'),
            func.count(self.model.id).label('record_count')
        )
        
        # Apply filters
        filters = []
        if sede:
            filters.append(self.model.sede == sede)
        if start_date:
            filters.append(self.model.timestamp >= start_date)
        if end_date:
            filters.append(self.model.timestamp <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        row = result.first()
        
        if row:
            return {
                'avg_consumption': float(row.avg_consumption or 0),
                'total_consumption': float(row.total_consumption or 0),
                'max_consumption': float(row.max_consumption or 0),
                'min_consumption': float(row.min_consumption or 0),
                'record_count': int(row.record_count or 0)
            }
        
        return {
            'avg_consumption': 0.0,
            'total_consumption': 0.0,
            'max_consumption': 0.0,
            'min_consumption': 0.0,
            'record_count': 0
        }
    
    async def get_by_sector(
        self,
        db: AsyncSession,
        sede: str,
        sector: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[ConsumptionRecord]:
        """
        Get consumption records filtered by sector.
        
        Args:
            db: Database session
            sede: Sede name
            sector: Sector name (comedor, salones, laboratorios, auditorios, oficinas)
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            List of consumption records
        """
        # Map sector names to columns
        sector_columns = {
            'comedor': self.model.energia_comedor_kwh,
            'salones': self.model.energia_salones_kwh,
            'laboratorios': self.model.energia_laboratorios_kwh,
            'auditorios': self.model.energia_auditorios_kwh,
            'oficinas': self.model.energia_oficinas_kwh
        }
        
        query = select(self.model).where(
            and_(
                self.model.sede == sede,
                self.model.timestamp >= start_date,
                self.model.timestamp <= end_date,
                sector_columns.get(sector, self.model.energia_total_kwh) > 0
            )
        ).order_by(self.model.timestamp.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_hourly_average(
        self,
        db: AsyncSession,
        sede: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get average consumption by hour of day.
        
        Args:
            db: Database session
            sede: Sede name
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of dictionaries with hour and average consumption
        """
        query = select(
            self.model.hora,
            func.avg(self.model.energia_total_kwh).label('avg_consumption')
        ).where(
            self.model.sede == sede
        )
        
        if start_date:
            query = query.where(self.model.timestamp >= start_date)
        if end_date:
            query = query.where(self.model.timestamp <= end_date)
        
        query = query.group_by(self.model.hora).order_by(self.model.hora)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                'hora': row.hora,
                'avg_consumption': float(row.avg_consumption or 0)
            }
            for row in rows
        ]
