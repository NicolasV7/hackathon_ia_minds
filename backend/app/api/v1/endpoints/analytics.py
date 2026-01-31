"""
Analytics and dashboard endpoints.
"""

import logging
from typing import Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

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
    start_date: str = Query(..., description="Start datetime (ISO format)"),
    end_date: str = Query(..., description="End datetime (ISO format)"),
    granularity: str = Query("hourly", description="Granularity: hourly, daily, weekly"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consumption trends over time.
    
    Args:
        sede: Sede name
        start_date: Start datetime (ISO format)
        end_date: End datetime (ISO format)
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
        
        # Parse dates manually to handle format issues
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        trends = await analytics_service.get_consumption_trends(
            db=db,
            sede=sede,
            start_date=start_dt,
            end_date=end_dt,
            granularity=granularity
        )
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consumption trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumption/sectors/{sede}", response_model=Dict)
async def get_sector_breakdown(
    sede: str,
    start_date: str = Query(..., description="Start datetime (ISO format)"),
    end_date: str = Query(..., description="End datetime (ISO format)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consumption breakdown by sector.
    
    Args:
        sede: Sede name
        start_date: Start datetime (ISO format)
        end_date: End datetime (ISO format)
        db: Database session
        
    Returns:
        Dictionary with sector breakdown data
    """
    try:
        # Parse dates manually to handle format issues
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        breakdown = await analytics_service.get_sector_breakdown(
            db=db,
            sede=sede,
            start_date=start_dt,
            end_date=end_dt
        )
        return breakdown
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sector breakdown: {e}")
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
