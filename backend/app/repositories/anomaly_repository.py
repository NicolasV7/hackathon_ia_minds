"""
Repository for anomaly operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import Anomaly
from app.schemas.anomaly import AnomalyCreate, AnomalyUpdate
from .base_repository import BaseRepository


class AnomalyRepository(BaseRepository[Anomaly, AnomalyCreate, AnomalyUpdate]):
    """
    Repository for anomaly records.
    """
    
    def __init__(self):
        super().__init__(Anomaly)
    
    async def get_by_sede_and_severity(
        self,
        db: AsyncSession,
        sede: Optional[str] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Anomaly]:
        """
        Get anomalies filtered by sede and severity.
        
        Args:
            db: Database session
            sede: Optional sede filter
            severity: Optional severity filter
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of anomalies
        """
        filters = []
        if sede:
            filters.append(self.model.sede == sede)
        if severity:
            filters.append(self.model.severity == severity)
        
        query = select(self.model)
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(self.model.detected_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        sede: Optional[str] = None,
        anomaly_type: Optional[str] = None
    ) -> List[Anomaly]:
        """
        Get anomalies within a date range.
        
        Args:
            db: Database session
            start_date: Start datetime
            end_date: End datetime
            sede: Optional sede filter
            anomaly_type: Optional anomaly type filter
            
        Returns:
            List of anomalies
        """
        filters = [
            self.model.anomaly_timestamp >= start_date,
            self.model.anomaly_timestamp <= end_date
        ]
        
        if sede:
            filters.append(self.model.sede == sede)
        if anomaly_type:
            filters.append(self.model.anomaly_type == anomaly_type)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.detected_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_summary_by_sede(
        self,
        db: AsyncSession,
        sede: str
    ) -> dict:
        """
        Get anomaly summary statistics for a sede.
        
        Args:
            db: Database session
            sede: Sede name
            
        Returns:
            Dictionary with anomaly statistics
        """
        # Count by severity
        severity_query = select(
            self.model.severity,
            func.count(self.model.id).label('count')
        ).where(
            self.model.sede == sede
        ).group_by(self.model.severity)
        
        severity_result = await db.execute(severity_query)
        severity_counts = {row.severity: row.count for row in severity_result.all()}
        
        # Count by type
        type_query = select(
            self.model.anomaly_type,
            func.count(self.model.id).label('count')
        ).where(
            self.model.sede == sede
        ).group_by(self.model.anomaly_type)
        
        type_result = await db.execute(type_query)
        type_counts = {row.anomaly_type: row.count for row in type_result.all()}
        
        # Total potential savings
        savings_query = select(
            func.sum(self.model.potential_savings_kwh).label('total_savings')
        ).where(
            self.model.sede == sede
        )
        
        savings_result = await db.execute(savings_query)
        total_savings = savings_result.scalar() or 0.0
        
        return {
            'sede': sede,
            'by_severity': severity_counts,
            'by_type': type_counts,
            'total_potential_savings_kwh': float(total_savings)
        }
    
    async def get_unresolved(
        self,
        db: AsyncSession,
        sede: Optional[str] = None
    ) -> List[Anomaly]:
        """
        Get unresolved anomalies.
        
        Args:
            db: Database session
            sede: Optional sede filter
            
        Returns:
            List of unresolved anomalies
        """
        filters = [self.model.status == 'unresolved']
        
        if sede:
            filters.append(self.model.sede == sede)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.severity.desc(), self.model.detected_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
