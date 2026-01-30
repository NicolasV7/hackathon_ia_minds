"""
Repository for prediction operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate
from .base_repository import BaseRepository


class PredictionRepository(BaseRepository[Prediction, PredictionCreate, PredictionUpdate]):
    """
    Repository for prediction records.
    """
    
    def __init__(self):
        super().__init__(Prediction)
    
    async def get_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Prediction]:
        """
        Get predictions for a specific sede.
        
        Args:
            db: Database session
            sede: Sede name
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of predictions
        """
        query = select(self.model).where(
            self.model.sede == sede
        ).order_by(self.model.prediction_timestamp.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        sede: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[Prediction]:
        """
        Get predictions within a date range.
        
        Args:
            db: Database session
            sede: Optional sede filter
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            List of predictions
        """
        filters = [
            self.model.prediction_timestamp >= start_date,
            self.model.prediction_timestamp <= end_date
        ]
        
        if sede:
            filters.append(self.model.sede == sede)
        
        query = select(self.model).where(
            and_(*filters)
        ).order_by(self.model.prediction_timestamp.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_batch(
        self,
        db: AsyncSession,
        sede: str,
        limit: int = 24
    ) -> List[Prediction]:
        """
        Get the most recent prediction batch for a sede.
        
        Args:
            db: Database session
            sede: Sede name
            limit: Number of predictions to retrieve (default: 24)
            
        Returns:
            List of predictions ordered by prediction timestamp
        """
        query = select(self.model).where(
            self.model.sede == sede
        ).order_by(
            self.model.created_at.desc(),
            self.model.prediction_timestamp.asc()
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
