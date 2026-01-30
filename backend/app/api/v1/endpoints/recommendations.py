"""
Recommendation endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import (
    RecommendationGenerationRequest,
    RecommendationResponse,
    RecommendationStatusUpdate
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
recommendation_service = RecommendationService()


@router.post("/generate", response_model=List[RecommendationResponse], status_code=201)
async def generate_recommendations(
    request: RecommendationGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate recommendations based on recent anomalies.
    
    Args:
        request: Generation request with sede and lookback period
        db: Database session
        
    Returns:
        List of generated RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.generate_recommendations_from_anomalies(
            db=db,
            sede=request.sede,
            days=request.days
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}", response_model=List[RecommendationResponse])
async def get_recommendations_by_sede(
    sede: str,
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high, urgent)"),
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, implemented, rejected)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations for a specific sede.
    
    Args:
        sede: Sede name
        priority: Optional priority filter
        status: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.get_recommendations_by_sede(
            db=db,
            sede=sede,
            priority=priority,
            status=status,
            skip=skip,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending", response_model=List[RecommendationResponse])
async def get_pending_recommendations(
    sede: Optional[str] = Query(None, description="Optional sede filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending recommendations.
    
    Args:
        sede: Optional sede filter
        db: Database session
        
    Returns:
        List of pending RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.get_pending_recommendations(
            db=db,
            sede=sede
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{recommendation_id}/status", response_model=RecommendationResponse)
async def update_recommendation_status(
    recommendation_id: int,
    status_update: RecommendationStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the status of a recommendation.
    
    Args:
        recommendation_id: Recommendation ID
        status_update: Status update with new status and optional notes
        db: Database session
        
    Returns:
        Updated RecommendationResponse
    """
    try:
        recommendation = await recommendation_service.update_recommendation_status(
            db=db,
            recommendation_id=recommendation_id,
            status=status_update.status,
            implementation_notes=status_update.implementation_notes
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
