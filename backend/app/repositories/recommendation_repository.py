"""
Repository for recommendation operations.
"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate
from .base_repository import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation, RecommendationCreate, RecommendationUpdate]):
    """
    Repository for recommendation records.
    """
    
    def __init__(self):
        super().__init__(Recommendation)
    
    async def get_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recommendation]:
        """
        Get recommendations for a specific sede.
        
        Args:
            db: Database session
            sede: Sede name
            priority: Optional priority filter
            status: Optional status filter
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of recommendations
        """
        filters = [self.model.sede == sede]
        
        if priority:
            filters.append(self.model.priority == priority)
        if status:
            filters.append(self.model.status == status)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_priority(
        self,
        db: AsyncSession,
        priority: str,
        sede: Optional[str] = None
    ) -> List[Recommendation]:
        """
        Get recommendations by priority level.
        
        Args:
            db: Database session
            priority: Priority level (high, medium, low)
            sede: Optional sede filter
            
        Returns:
            List of recommendations
        """
        filters = [self.model.priority == priority]
        
        if sede:
            filters.append(self.model.sede == sede)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_pending(
        self,
        db: AsyncSession,
        sede: Optional[str] = None
    ) -> List[Recommendation]:
        """
        Get pending recommendations.
        
        Args:
            db: Database session
            sede: Optional sede filter
            
        Returns:
            List of pending recommendations
        """
        filters = [self.model.status == 'pending']
        
        if sede:
            filters.append(self.model.sede == sede)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.priority.desc(), self.model.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_anomaly_id(
        self,
        db: AsyncSession,
        anomaly_id: int
    ) -> List[Recommendation]:
        """
        Get recommendations associated with a specific anomaly.
        
        Args:
            db: Database session
            anomaly_id: Anomaly ID
            
        Returns:
            List of recommendations
        """
        query = select(self.model).where(
            self.model.anomaly_id == anomaly_id
        ).order_by(self.model.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
