"""
Prediction service for CO2 and Energy consumption forecasting.
Updated to use new ML models from newmodels/ folder.
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.ml.inference import ml_service
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import (
    PredictionCreate, 
    PredictionResponse,
    PredictionRequest,
    CO2PredictionResponse,
    EnergyPredictionResponse
)

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service for handling prediction operations.
    Orchestrates ML inference and database persistence.
    """
    
    def __init__(self):
        self.prediction_repo = PredictionRepository()
    
    async def create_prediction(
        self,
        db: AsyncSession,
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        Create a combined CO2 and Energy prediction and save to database.
        
        This method:
        1. Predicts CO2 using the LightGBM model
        2. Uses the CO2 prediction to predict Energy using the Ridge model
        3. Saves the prediction to the database
        
        Args:
            db: Database session
            request: PredictionRequest with all required inputs
            
        Returns:
            PredictionResponse with both predictions
        """
        try:
            # Use timestamp from request or current time
            timestamp = request.timestamp or datetime.now()
            sede = request.sede.value if hasattr(request.sede, 'value') else str(request.sede)
            
            # Get periodo_academico value if provided
            periodo = None
            if request.periodo_academico:
                periodo = request.periodo_academico.value if hasattr(request.periodo_academico, 'value') else str(request.periodo_academico)
            
            # Make combined prediction using ML service
            prediction_result = ml_service.predict_combined(
                energia_comedor_kwh=request.energia_comedor_kwh,
                energia_salones_kwh=request.energia_salones_kwh,
                energia_laboratorios_kwh=request.energia_laboratorios_kwh,
                energia_auditorios_kwh=request.energia_auditorios_kwh,
                energia_oficinas_kwh=request.energia_oficinas_kwh,
                agua_litros=request.agua_litros,
                temperatura_exterior_c=request.temperatura_exterior_c,
                ocupacion_pct=request.ocupacion_pct,
                sede=sede,
                timestamp=timestamp,
                es_festivo=request.es_festivo,
                es_semana_parciales=request.es_semana_parciales,
                es_semana_finales=request.es_semana_finales,
                periodo_academico=periodo
            )
            
            # Save to database
            prediction_data = PredictionCreate(
                sede=sede,
                prediction_timestamp=timestamp,
                predicted_co2_kg=prediction_result["predicted_co2_kg"],
                predicted_energy_kwh=prediction_result["predicted_energy_kwh"],
                predicted_kwh=prediction_result["predicted_energy_kwh"],  # Legacy compatibility
                confidence_co2=prediction_result["confidence_co2"],
                confidence_energy=prediction_result["confidence_energy"],
                energia_comedor_kwh=request.energia_comedor_kwh,
                energia_salones_kwh=request.energia_salones_kwh,
                energia_laboratorios_kwh=request.energia_laboratorios_kwh,
                energia_auditorios_kwh=request.energia_auditorios_kwh,
                energia_oficinas_kwh=request.energia_oficinas_kwh,
                agua_litros=request.agua_litros,
                temperatura_exterior_c=request.temperatura_exterior_c,
                ocupacion_pct=request.ocupacion_pct,
                es_festivo=request.es_festivo,
                es_semana_parciales=request.es_semana_parciales,
                es_semana_finales=request.es_semana_finales
            )
            
            db_prediction = await self.prediction_repo.create(db, prediction_data)
            
            # Build response
            return PredictionResponse(
                id=db_prediction.id if hasattr(db_prediction, 'id') else None,
                sede=sede,
                timestamp=timestamp,
                predicted_co2_kg=prediction_result["predicted_co2_kg"],
                predicted_energy_kwh=prediction_result["predicted_energy_kwh"],
                confidence_co2=prediction_result["confidence_co2"],
                confidence_energy=prediction_result["confidence_energy"],
                energia_comedor_kwh=request.energia_comedor_kwh,
                energia_salones_kwh=request.energia_salones_kwh,
                energia_laboratorios_kwh=request.energia_laboratorios_kwh,
                energia_auditorios_kwh=request.energia_auditorios_kwh,
                energia_oficinas_kwh=request.energia_oficinas_kwh,
                agua_litros=request.agua_litros,
                temperatura_exterior_c=request.temperatura_exterior_c,
                ocupacion_pct=request.ocupacion_pct,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating prediction: {str(e)}")
            raise
    
    async def predict_co2_only(
        self,
        request: PredictionRequest
    ) -> CO2PredictionResponse:
        """
        Predict only CO2 emissions (without saving to DB).
        
        Args:
            request: PredictionRequest with required inputs
            
        Returns:
            CO2PredictionResponse with prediction
        """
        try:
            timestamp = request.timestamp or datetime.now()
            sede = request.sede.value if hasattr(request.sede, 'value') else str(request.sede)
            
            periodo = None
            if request.periodo_academico:
                periodo = request.periodo_academico.value if hasattr(request.periodo_academico, 'value') else str(request.periodo_academico)
            
            predicted_co2 = ml_service.predict_co2(
                energia_comedor_kwh=request.energia_comedor_kwh,
                energia_salones_kwh=request.energia_salones_kwh,
                energia_laboratorios_kwh=request.energia_laboratorios_kwh,
                energia_auditorios_kwh=request.energia_auditorios_kwh,
                energia_oficinas_kwh=request.energia_oficinas_kwh,
                agua_litros=request.agua_litros,
                temperatura_exterior_c=request.temperatura_exterior_c,
                ocupacion_pct=request.ocupacion_pct,
                sede=sede,
                timestamp=timestamp,
                es_festivo=request.es_festivo,
                es_semana_parciales=request.es_semana_parciales,
                es_semana_finales=request.es_semana_finales,
                periodo_academico=periodo
            )
            
            return CO2PredictionResponse(
                predicted_co2_kg=predicted_co2,
                confidence=0.893,
                timestamp=timestamp,
                sede=sede
            )
            
        except Exception as e:
            logger.error(f"Error predicting CO2: {str(e)}")
            raise
    
    async def predict_energy_only(
        self,
        reading_id: int,
        co2_kg: float,
        request: PredictionRequest
    ) -> EnergyPredictionResponse:
        """
        Predict only Energy consumption (requires CO2 value).
        
        Args:
            reading_id: Unique reading identifier
            co2_kg: CO2 emissions value (can be from prediction)
            request: PredictionRequest with required inputs
            
        Returns:
            EnergyPredictionResponse with prediction
        """
        try:
            timestamp = request.timestamp or datetime.now()
            sede = request.sede.value if hasattr(request.sede, 'value') else str(request.sede)
            
            periodo = None
            if request.periodo_academico:
                periodo = request.periodo_academico.value if hasattr(request.periodo_academico, 'value') else str(request.periodo_academico)
            
            predicted_energy = ml_service.predict_energy(
                reading_id=reading_id,
                energia_comedor_kwh=request.energia_comedor_kwh,
                energia_salones_kwh=request.energia_salones_kwh,
                energia_laboratorios_kwh=request.energia_laboratorios_kwh,
                energia_auditorios_kwh=request.energia_auditorios_kwh,
                energia_oficinas_kwh=request.energia_oficinas_kwh,
                agua_litros=request.agua_litros,
                temperatura_exterior_c=request.temperatura_exterior_c,
                ocupacion_pct=request.ocupacion_pct,
                co2_kg=co2_kg,
                sede=sede,
                timestamp=timestamp,
                es_festivo=request.es_festivo,
                es_semana_parciales=request.es_semana_parciales,
                es_semana_finales=request.es_semana_finales,
                periodo_academico=periodo
            )
            
            return EnergyPredictionResponse(
                predicted_energy_kwh=predicted_energy,
                confidence=0.998,
                timestamp=timestamp,
                sede=sede,
                co2_kg_used=co2_kg
            )
            
        except Exception as e:
            logger.error(f"Error predicting energy: {str(e)}")
            raise
    
    async def create_batch_predictions(
        self,
        db: AsyncSession,
        requests: List[PredictionRequest]
    ) -> List[PredictionResponse]:
        """
        Create batch predictions for multiple inputs.
        
        Args:
            db: Database session
            requests: List of PredictionRequest objects
            
        Returns:
            List of PredictionResponse objects
        """
        responses = []
        for request in requests:
            try:
                response = await self.create_prediction(db, request)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error in batch prediction: {str(e)}")
                # Continue with other predictions
        
        return responses
    
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
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded models.
        
        Returns:
            Dictionary with model information
        """
        return ml_service.get_model_info()
