"""
Prediction endpoints.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.prediction_service import PredictionService
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionBatchRequest
)

router = APIRouter(prefix="/predictions", tags=["predictions"])
prediction_service = PredictionService()


@router.post("/", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a single energy consumption prediction.
    
    Args:
        request: Prediction request with timestamp, sede, and context
        db: Database session
        
    Returns:
        PredictionResponse with predicted consumption
    """
    try:
        prediction = await prediction_service.create_prediction(
            db=db,
            timestamp=request.timestamp,
            sede=request.sede,
            temperatura_exterior_c=request.temperatura_exterior_c,
            ocupacion_pct=request.ocupacion_pct,
            es_festivo=request.es_festivo,
            es_semana_parciales=request.es_semana_parciales,
            es_semana_finales=request.es_semana_finales
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=List[PredictionResponse], status_code=201)
async def create_batch_predictions(
    request: PredictionBatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create batch predictions for multiple hours ahead.
    
    Args:
        request: Batch prediction request with horizon hours
        db: Database session
        
    Returns:
        List of PredictionResponse objects
    """
    try:
        predictions = await prediction_service.create_batch_predictions(
            db=db,
            sede=request.sede,
            start_timestamp=request.start_timestamp,
            horizon_hours=request.horizon_hours,
            temperatura_exterior_c=request.temperatura_exterior_c,
            ocupacion_pct=request.ocupacion_pct
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}", response_model=List[PredictionResponse])
async def get_predictions_by_sede(
    sede: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get predictions for a specific sede.
    
    Args:
        sede: Sede name (Tunja, Duitama, Sogamoso, Chiquinquira)
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of PredictionResponse objects
    """
    try:
        predictions = await prediction_service.get_predictions_by_sede(
            db=db,
            sede=sede,
            skip=skip,
            limit=limit
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}/latest", response_model=List[PredictionResponse])
async def get_latest_predictions(
    sede: str,
    limit: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent predictions for a sede.
    
    Args:
        sede: Sede name
        limit: Number of predictions to retrieve (default: 24)
        db: Database session
        
    Returns:
        List of PredictionResponse objects
    """
    try:
        predictions = await prediction_service.get_latest_predictions(
            db=db,
            sede=sede,
            limit=limit
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/range", response_model=List[PredictionResponse])
async def get_predictions_by_date_range(
    start_date: datetime = Query(..., description="Start datetime"),
    end_date: datetime = Query(..., description="End datetime"),
    sede: Optional[str] = Query(None, description="Optional sede filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get predictions within a date range.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        sede: Optional sede filter
        db: Database session
        
    Returns:
        List of PredictionResponse objects
    """
    try:
        predictions = await prediction_service.get_predictions_by_date_range(
            db=db,
            sede=sede,
            start_date=start_date,
            end_date=end_date
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
