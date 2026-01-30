"""
Analytics and dashboard endpoints.
"""

from typing import Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()


@router.get("/dashboard/{sede}", response_model=Dict)
async def get_dashboard_kpis(
    sede: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get key performance indicators for the dashboard.
    
    Args:
        sede: Sede name
        days: Number of days to analyze (default: 30)
        db: Database session
        
    Returns:
        Dictionary with dashboard KPI data
    """
    try:
        kpis = await analytics_service.get_dashboard_kpis(
            db=db,
            sede=sede,
            days=days
        )
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumption/trends/{sede}", response_model=Dict)
async def get_consumption_trends(
    sede: str,
    start_date: datetime = Query(..., description="Start datetime"),
    end_date: datetime = Query(..., description="End datetime"),
    granularity: str = Query("hourly", description="Granularity: hourly, daily, weekly"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consumption trends over time.
    
    Args:
        sede: Sede name
        start_date: Start datetime
        end_date: End datetime
        granularity: Data granularity (hourly, daily, weekly)
        db: Database session
        
    Returns:
        Dictionary with trend data
    """
    try:
        if granularity not in ['hourly', 'daily', 'weekly']:
            raise HTTPException(
                status_code=400,
                detail="Invalid granularity. Must be 'hourly', 'daily', or 'weekly'"
            )
        
        trends = await analytics_service.get_consumption_trends(
            db=db,
            sede=sede,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        return trends
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumption/sectors/{sede}", response_model=Dict)
async def get_sector_breakdown(
    sede: str,
    start_date: datetime = Query(..., description="Start datetime"),
    end_date: datetime = Query(..., description="End datetime"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consumption breakdown by sector.
    
    Args:
        sede: Sede name
        start_date: Start datetime
        end_date: End datetime
        db: Database session
        
    Returns:
        Dictionary with sector breakdown data
    """
    try:
        breakdown = await analytics_service.get_sector_breakdown(
            db=db,
            sede=sede,
            start_date=start_date,
            end_date=end_date
        )
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/hourly/{sede}", response_model=Dict)
async def get_hourly_patterns(
    sede: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get hourly consumption patterns.
    
    Args:
        sede: Sede name
        days: Number of days to analyze (default: 30)
        db: Database session
        
    Returns:
        Dictionary with hourly pattern data
    """
    try:
        patterns = await analytics_service.get_hourly_patterns(
            db=db,
            sede=sede,
            days=days
        )
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/efficiency/score/{sede}", response_model=Dict)
async def get_efficiency_score(
    sede: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate efficiency score for a sede.
    
    Args:
        sede: Sede name
        days: Number of days to analyze (default: 30)
        db: Database session
        
    Returns:
        Dictionary with efficiency score and components
    """
    try:
        score = await analytics_service.get_efficiency_score(
            db=db,
            sede=sede,
            days=days
        )
        return score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
