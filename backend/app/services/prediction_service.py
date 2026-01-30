"""
Prediction service for energy consumption forecasting.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.ml.inference import ml_service
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.consumption_repository import ConsumptionRepository
from app.schemas.prediction import PredictionCreate, PredictionResponse

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service for handling prediction operations.
    Orchestrates ML inference and database persistence.
    """
    
    def __init__(self):
        self.prediction_repo = PredictionRepository()
        self.consumption_repo = ConsumptionRepository()
    
    async def create_prediction(
        self,
        db: AsyncSession,
        timestamp: datetime,
        sede: str,
        temperatura_exterior_c: float = 20.0,
        ocupacion_pct: float = 70.0,
        es_festivo: bool = False,
        es_semana_parciales: bool = False,
        es_semana_finales: bool = False
    ) -> PredictionResponse:
        """
        Create a single prediction and save to database.
        
        Args:
            db: Database session
            timestamp: Timestamp for prediction
            sede: Sede name
            temperatura_exterior_c: Exterior temperature
            ocupacion_pct: Occupancy percentage
            es_festivo: Is holiday
            es_semana_parciales: Is midterm week
            es_semana_finales: Is finals week
            
        Returns:
            PredictionResponse with prediction data
        """
        try:
            # Get recent consumption for lag features
            recent_data = await self.consumption_repo.get_latest_by_sede(
                db=db,
                sede=sede,
                limit=168  # Last week
            )
            
            # Calculate lag and rolling features from recent data
            lag_features = None
            rolling_features = None
            
            if recent_data:
                # Extract values for lag features
                energia_values = [r.energia_total_kwh for r in recent_data]
                energia_values.reverse()  # Order chronologically
                
                if len(energia_values) >= 1:
                    lag_features = {
                        'energia_total_kwh_lag_1h': energia_values[-1] if len(energia_values) >= 1 else 0,
                        'energia_total_kwh_lag_24h': energia_values[-24] if len(energia_values) >= 24 else energia_values[-1],
                        'energia_total_kwh_lag_168h': energia_values[-168] if len(energia_values) >= 168 else energia_values[-1]
                    }
                    
                    # Calculate rolling features
                    import numpy as np
                    rolling_features = {
                        'energia_total_kwh_rolling_mean_24h': float(np.mean(energia_values[-24:])) if len(energia_values) >= 24 else float(np.mean(energia_values)),
                        'energia_total_kwh_rolling_std_24h': float(np.std(energia_values[-24:])) if len(energia_values) >= 24 else 0.0,
                        'energia_total_kwh_rolling_max_24h': float(np.max(energia_values[-24:])) if len(energia_values) >= 24 else float(np.max(energia_values)),
                        'energia_total_kwh_rolling_mean_168h': float(np.mean(energia_values[-168:])) if len(energia_values) >= 168 else float(np.mean(energia_values)),
                        'energia_total_kwh_rolling_std_168h': float(np.std(energia_values[-168:])) if len(energia_values) >= 168 else 0.0,
                        'energia_total_kwh_rolling_max_168h': float(np.max(energia_values[-168:])) if len(energia_values) >= 168 else float(np.max(energia_values))
                    }
            
            # Make prediction using ML service
            predicted_kwh = ml_service.predict_consumption(
                timestamp=timestamp,
                sede=sede,
                temperatura_exterior_c=temperatura_exterior_c,
                ocupacion_pct=ocupacion_pct,
                es_festivo=es_festivo,
                es_semana_parciales=es_semana_parciales,
                es_semana_finales=es_semana_finales,
                lag_features=lag_features,
                rolling_features=rolling_features
            )
            
            # Calculate confidence score (simplified - can be enhanced)
            confidence_score = 0.85 if lag_features else 0.70
            
            # Save to database
            prediction_data = PredictionCreate(
                sede=sede,
                prediction_timestamp=timestamp,
                predicted_kwh=predicted_kwh,
                confidence_score=confidence_score,
                temperatura_exterior_c=temperatura_exterior_c,
                ocupacion_pct=ocupacion_pct,
                es_festivo=es_festivo,
                es_semana_parciales=es_semana_parciales,
                es_semana_finales=es_semana_finales
            )
            
            db_prediction = await self.prediction_repo.create(db, prediction_data)
            
            return PredictionResponse.model_validate(db_prediction)
            
        except Exception as e:
            logger.error(f"Error creating prediction: {str(e)}")
            raise
    
    async def create_batch_predictions(
        self,
        db: AsyncSession,
        sede: str,
        start_timestamp: datetime,
        horizon_hours: int = 24,
        temperatura_exterior_c: float = 20.0,
        ocupacion_pct: float = 70.0
    ) -> List[PredictionResponse]:
        """
        Create batch predictions for multiple hours ahead.
        
        Args:
            db: Database session
            sede: Sede name
            start_timestamp: Starting timestamp
            horizon_hours: Number of hours to predict
            temperatura_exterior_c: Exterior temperature
            ocupacion_pct: Occupancy percentage
            
        Returns:
            List of PredictionResponse objects
        """
        try:
            # Use ML service's predict_horizon method
            predictions_data = ml_service.predict_horizon(
                sede=sede,
                start_timestamp=start_timestamp,
                horizon_hours=horizon_hours,
                temperatura_exterior_c=temperatura_exterior_c,
                ocupacion_pct=ocupacion_pct
            )
            
            # Save all predictions to database
            predictions_responses = []
            
            for pred_data in predictions_data:
                prediction_create = PredictionCreate(
                    sede=sede,
                    prediction_timestamp=pred_data['timestamp'],
                    predicted_kwh=pred_data['predicted_kwh'],
                    confidence_score=0.80,  # Slightly lower for multi-step
                    temperatura_exterior_c=temperatura_exterior_c,
                    ocupacion_pct=ocupacion_pct,
                    es_festivo=False,
                    es_semana_parciales=False,
                    es_semana_finales=False
                )
                
                db_prediction = await self.prediction_repo.create(db, prediction_create)
                predictions_responses.append(PredictionResponse.model_validate(db_prediction))
            
            return predictions_responses
            
        except Exception as e:
            logger.error(f"Error creating batch predictions: {str(e)}")
            raise
    
    async def get_predictions_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PredictionResponse]:
        """
        Get predictions for a specific sede.
        
        Args:
            db: Database session
            sede: Sede name
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of PredictionResponse objects
        """
        predictions = await self.prediction_repo.get_by_sede(
            db=db,
            sede=sede,
            skip=skip,
            limit=limit
        )
        
        return [PredictionResponse.model_validate(p) for p in predictions]
    
    async def get_predictions_by_date_range(
        self,
        db: AsyncSession,
        sede: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[PredictionResponse]:
        """
        Get predictions within a date range.
        
        Args:
            db: Database session
            sede: Optional sede filter
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            List of PredictionResponse objects
        """
        predictions = await self.prediction_repo.get_by_date_range(
            db=db,
            sede=sede,
            start_date=start_date,
            end_date=end_date
        )
        
        return [PredictionResponse.model_validate(p) for p in predictions]
    
    async def get_latest_predictions(
        self,
        db: AsyncSession,
        sede: str,
        limit: int = 24
    ) -> List[PredictionResponse]:
        """
        Get the most recent predictions for a sede.
        
        Args:
            db: Database session
            sede: Sede name
            limit: Number of predictions to retrieve
            
        Returns:
            List of PredictionResponse objects
        """
        predictions = await self.prediction_repo.get_latest_batch(
            db=db,
            sede=sede,
            limit=limit
        )
        
        return [PredictionResponse.model_validate(p) for p in predictions]
