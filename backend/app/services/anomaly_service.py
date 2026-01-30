"""
Anomaly detection service.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import logging

from app.ml.inference import ml_service
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.consumption_repository import ConsumptionRepository
from app.schemas.anomaly import AnomalyCreate, AnomalyResponse, AnomalySummaryResponse

logger = logging.getLogger(__name__)


class AnomalyService:
    """
    Service for anomaly detection operations.
    """
    
    def __init__(self):
        self.anomaly_repo = AnomalyRepository()
        self.consumption_repo = ConsumptionRepository()
    
    async def detect_anomalies(
        self,
        db: AsyncSession,
        sede: str,
        start_date: datetime,
        end_date: datetime,
        severity_threshold: Optional[str] = None
    ) -> List[AnomalyResponse]:
        """
        Detect anomalies in consumption data for a date range.
        
        Args:
            db: Database session
            sede: Sede name
            start_date: Start datetime
            end_date: End datetime
            severity_threshold: Optional severity filter
            
        Returns:
            List of AnomalyResponse objects
        """
        try:
            # Get consumption data
            consumption_records = await self.consumption_repo.get_by_sede_and_date_range(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            if not consumption_records:
                logger.warning(f"No consumption data found for sede {sede}")
                return []
            
            # Convert to DataFrame for ML service
            consumption_data = []
            for record in consumption_records:
                consumption_data.append({
                    'timestamp': record.timestamp,
                    'sede': record.sede,
                    'energia_total_kwh': record.energia_total_kwh,
                    'hora': record.hora,
                    'dia_semana': record.dia_semana,
                    'es_fin_semana': record.es_fin_semana,
                    'energia_comedor_kwh': record.energia_comedor_kwh,
                    'energia_salones_kwh': record.energia_salones_kwh,
                    'energia_laboratorios_kwh': record.energia_laboratorios_kwh,
                    'energia_auditorios_kwh': record.energia_auditorios_kwh,
                    'energia_oficinas_kwh': record.energia_oficinas_kwh
                })
            
            df = pd.DataFrame(consumption_data)
            
            # Detect anomalies using ML service
            detected_anomalies = ml_service.detect_anomalies(
                consumption_data=df,
                severity_threshold=severity_threshold
            )
            
            # Save anomalies to database
            anomaly_responses = []
            
            for anomaly in detected_anomalies:
                anomaly_create = AnomalyCreate(
                    timestamp=anomaly['timestamp'],
                    sede=anomaly['sede'],
                    sector=anomaly['sector'],
                    anomaly_type=anomaly['anomaly_type'],
                    severity=anomaly['severity'],
                    actual_value=anomaly['actual_value'],
                    expected_value=anomaly['expected_value'],
                    deviation_pct=anomaly['deviation_pct'],
                    description=anomaly['description'],
                    recommendation=anomaly['recommendation'],
                    potential_savings_kwh=anomaly.get('potential_savings_kwh', 0.0),
                    status='unresolved'
                )
                
                db_anomaly = await self.anomaly_repo.create(db, anomaly_create)
                anomaly_responses.append(AnomalyResponse.model_validate(db_anomaly))
            
            return anomaly_responses
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    async def get_anomalies_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnomalyResponse]:
        """
        Get anomalies for a specific sede.
        
        Args:
            db: Database session
            sede: Sede name
            severity: Optional severity filter
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of AnomalyResponse objects
        """
        anomalies = await self.anomaly_repo.get_by_sede_and_severity(
            db=db,
            sede=sede,
            severity=severity,
            skip=skip,
            limit=limit
        )
        
        return [AnomalyResponse.model_validate(a) for a in anomalies]
    
    async def get_anomalies_by_date_range(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        sede: Optional[str] = None,
        anomaly_type: Optional[str] = None
    ) -> List[AnomalyResponse]:
        """
        Get anomalies within a date range.
        
        Args:
            db: Database session
            start_date: Start datetime
            end_date: End datetime
            sede: Optional sede filter
            anomaly_type: Optional anomaly type filter
            
        Returns:
            List of AnomalyResponse objects
        """
        anomalies = await self.anomaly_repo.get_by_date_range(
            db=db,
            start_date=start_date,
            end_date=end_date,
            sede=sede,
            anomaly_type=anomaly_type
        )
        
        return [AnomalyResponse.model_validate(a) for a in anomalies]
    
    async def get_anomaly_summary(
        self,
        db: AsyncSession,
        sede: str
    ) -> AnomalySummaryResponse:
        """
        Get anomaly summary statistics for a sede.
        
        Args:
            db: Database session
            sede: Sede name
            
        Returns:
            AnomalySummaryResponse with statistics
        """
        summary = await self.anomaly_repo.get_summary_by_sede(db=db, sede=sede)
        
        return AnomalySummaryResponse(
            sede=sede,
            total_anomalies=sum(summary['by_severity'].values()),
            by_severity=summary['by_severity'],
            by_type=summary['by_type'],
            total_potential_savings_kwh=summary['total_potential_savings_kwh']
        )
    
    async def get_unresolved_anomalies(
        self,
        db: AsyncSession,
        sede: Optional[str] = None
    ) -> List[AnomalyResponse]:
        """
        Get unresolved anomalies.
        
        Args:
            db: Database session
            sede: Optional sede filter
            
        Returns:
            List of unresolved AnomalyResponse objects
        """
        anomalies = await self.anomaly_repo.get_unresolved(db=db, sede=sede)
        
        return [AnomalyResponse.model_validate(a) for a in anomalies]
    
    async def update_anomaly_status(
        self,
        db: AsyncSession,
        anomaly_id: int,
        status: str
    ) -> AnomalyResponse:
        """
        Update the status of an anomaly.
        
        Args:
            db: Database session
            anomaly_id: Anomaly ID
            status: New status (unresolved, investigating, resolved)
            
        Returns:
            Updated AnomalyResponse
        """
        anomaly = await self.anomaly_repo.get(db, anomaly_id)
        
        if not anomaly:
            raise ValueError(f"Anomaly with ID {anomaly_id} not found")
        
        updated_anomaly = await self.anomaly_repo.update(
            db=db,
            db_obj=anomaly,
            obj_in={'status': status}
        )
        
        return AnomalyResponse.model_validate(updated_anomaly)
