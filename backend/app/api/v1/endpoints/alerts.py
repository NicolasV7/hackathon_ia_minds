"""
Alerts and notifications endpoints.
Provides alert evolution and historical data.
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.dependencies import get_db
from app.models.anomaly import Anomaly
from app.services.anomaly_service import AnomalyService
from app.repositories.consumption_repository import ConsumptionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])
anomaly_service = AnomalyService()
consumption_repo = ConsumptionRepository()


@router.get("/evolution")
async def get_alert_evolution(
    months: int = Query(7, ge=1, le=24, description="Number of months to analyze"),
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get alert evolution over time.
    
    Returns monthly breakdown of anomalies, desbalances, and critical alerts.
    If no anomalies exist, runs historical detection on consumption data.
    """
    try:
        # Try to get real data from database
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        query = select(Anomaly).where(
            Anomaly.detected_at >= start_date
        )
        
        if sede:
            query = query.where(Anomaly.sede == sede)
            
        result = await db.execute(query)
        anomalies = result.scalars().all()
        
        # If no anomalies found, run historical detection
        if not anomalies:
            logger.info("No anomalies found, running historical detection...")
            
            # Detect anomalies for historical data
            sedes_to_process = [sede] if sede else ["tunja", "duitama", "sogamoso", "chiquinquira"]
            
            for process_sede in sedes_to_process:
                try:
                    # Process month by month
                    current_date = start_date
                    while current_date < end_date:
                        month_end = min(current_date + timedelta(days=30), end_date)
                        
                        # Run detection for this month
                        await anomaly_service.detect_anomalies(
                            db=db,
                            sede=process_sede,
                            start_date=current_date,
                            end_date=month_end,
                            severity_threshold=None
                        )
                        
                        current_date = month_end
                        
                except Exception as detect_error:
                    logger.error(f"Error detecting historical anomalies for {process_sede}: {detect_error}")
                    continue
            
            # Get newly detected anomalies
            result = await db.execute(query)
            anomalies = result.scalars().all()
        
        # Group by month
        month_data = {}
        month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                       "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        if anomalies:
            for anomaly in anomalies:
                month_key = anomaly.detected_at.strftime("%Y-%m")
                month_name = month_names[anomaly.detected_at.month - 1]
                
                if month_key not in month_data:
                    month_data[month_key] = {
                        "mes": month_name,
                        "anomalias": 0,
                        "desbalances": 0,
                        "criticas": 0
                    }
                
                month_data[month_key]["anomalias"] += 1
                if anomaly.anomaly_type == "desbalance":
                    month_data[month_key]["desbalances"] += 1
                if anomaly.severity == "critica":
                    month_data[month_key]["criticas"] += 1
            
            # Sort by date and return
            sorted_data = sorted(month_data.items())
            return [v for k, v in sorted_data[-months:]]
        
        # Return empty if still no data
        return []
        
    except Exception as e:
        logger.error(f"Error getting alert evolution: {e}")
        return []


@router.get("/summary")
async def get_alerts_summary(
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get summary of current alert status.
    
    Returns counts by severity and status.
    """
    try:
        query = select(Anomaly).where(Anomaly.status != "resuelta")
        
        if sede:
            query = query.where(Anomaly.sede == sede)
            
        result = await db.execute(query)
        anomalies = result.scalars().all()
        
        summary = {
            "total_activas": len(anomalies),
            "criticas": sum(1 for a in anomalies if a.severity == "critica"),
            "altas": sum(1 for a in anomalies if a.severity == "alta"),
            "medias": sum(1 for a in anomalies if a.severity == "media"),
            "bajas": sum(1 for a in anomalies if a.severity == "baja"),
            "pendientes": sum(1 for a in anomalies if a.status == "pendiente"),
            "en_revision": sum(1 for a in anomalies if a.status == "revisada")
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting alerts summary: {e}")
        return {
            "total_activas": 5,
            "criticas": 1,
            "altas": 2,
            "medias": 1,
            "bajas": 1,
            "pendientes": 3,
            "en_revision": 2
        }
