"""
Anomaly detection endpoints.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.anomaly_service import AnomalyService
from app.schemas.anomaly import (
    AnomalyDetectionRequest,
    AnomalyResponse,
    AnomalySummaryResponse,
    AnomalyStatusUpdate
)

router = APIRouter(prefix="/anomalies", tags=["anomalies"])
anomaly_service = AnomalyService()


@router.post("/detect", response_model=List[AnomalyResponse], status_code=201)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect anomalies in consumption data for a given period.
    
    Args:
        request: Detection request with sede and date range
        db: Database session
        
    Returns:
        List of detected AnomalyResponse objects
    """
    try:
        # Default to last 7 days if dates not provided
        end_date = request.end_date or datetime.utcnow()
        start_date = request.start_date or (end_date - timedelta(days=request.days or 7))
        
        anomalies = await anomaly_service.detect_anomalies(
            db=db,
            sede=request.sede,
            start_date=start_date,
            end_date=end_date,
            severity_threshold=request.severity_threshold
        )
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}", response_model=List[AnomalyResponse])
async def get_anomalies_by_sede(
    sede: str,
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get anomalies for a specific sede.
    
    Args:
        sede: Sede name
        severity: Optional severity filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of AnomalyResponse objects
    """
    try:
        anomalies = await anomaly_service.get_anomalies_by_sede(
            db=db,
            sede=sede,
            severity=severity,
            skip=skip,
            limit=limit
        )
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}/summary", response_model=AnomalySummaryResponse)
async def get_anomaly_summary(
    sede: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get anomaly summary statistics for a sede.
    
    Args:
        sede: Sede name
        db: Database session
        
    Returns:
        AnomalySummaryResponse with statistics
    """
    try:
        summary = await anomaly_service.get_anomaly_summary(db=db, sede=sede)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unresolved", response_model=List[AnomalyResponse])
async def get_unresolved_anomalies(
    sede: Optional[str] = Query(None, description="Optional sede filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unresolved anomalies.
    
    Args:
        sede: Optional sede filter
        db: Database session
        
    Returns:
        List of unresolved AnomalyResponse objects
    """
    try:
        anomalies = await anomaly_service.get_unresolved_anomalies(
            db=db,
            sede=sede
        )
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/range", response_model=List[AnomalyResponse])
async def get_anomalies_by_date_range(
    start_date: datetime = Query(..., description="Start datetime"),
    end_date: datetime = Query(..., description="End datetime"),
    sede: Optional[str] = Query(None, description="Optional sede filter"),
    anomaly_type: Optional[str] = Query(None, description="Optional anomaly type filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get anomalies within a date range.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        sede: Optional sede filter
        anomaly_type: Optional anomaly type filter
        db: Database session
        
    Returns:
        List of AnomalyResponse objects
    """
    try:
        anomalies = await anomaly_service.get_anomalies_by_date_range(
            db=db,
            start_date=start_date,
            end_date=end_date,
            sede=sede,
            anomaly_type=anomaly_type
        )
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{anomaly_id}/status", response_model=AnomalyResponse)
async def update_anomaly_status(
    anomaly_id: int,
    status_update: AnomalyStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the status of an anomaly.
    
    Args:
        anomaly_id: Anomaly ID
        status_update: New status
        db: Database session
        
    Returns:
        Updated AnomalyResponse
    """
    try:
        anomaly = await anomaly_service.update_anomaly_status(
            db=db,
            anomaly_id=anomaly_id,
            status=status_update.status
        )
        return anomaly
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
