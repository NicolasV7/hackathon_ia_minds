"""
Prediction endpoints for CO2 and Energy models.
Updated to use new ML models from newmodels/ folder.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.prediction_service import PredictionService
from app.ml.inference import ml_service
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionBatchRequest,
    PredictionBatchResponse,
    CO2PredictionRequest,
    CO2PredictionResponse,
    EnergyPredictionRequest,
    EnergyPredictionResponse,
    ModelInfoResponse
)

router = APIRouter(prefix="/predictions", tags=["predictions"])
prediction_service = PredictionService()


@router.post("/", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a combined CO2 and Energy prediction.
    
    This endpoint:
    1. Predicts CO2 emissions using LightGBM model (R² = 0.893)
    2. Uses the CO2 prediction to predict Energy using Ridge model (R² = 0.998)
    3. Saves the prediction to the database
    
    Required inputs:
    - Energy consumption by area (comedor, salones, laboratorios, auditorios, oficinas)
    - Water consumption (agua_litros)
    - Exterior temperature (temperatura_exterior_c)
    - Occupancy percentage (ocupacion_pct)
    - Campus location (sede: Tunja, Duitama, Sogamoso)
    
    Optional inputs:
    - timestamp (defaults to now)
    - Academic flags (es_festivo, es_semana_parciales, es_semana_finales)
    - periodo_academico (auto-calculated from timestamp if not provided)
    
    Returns:
        PredictionResponse with predicted CO2 (kg) and Energy (kWh)
    """
    try:
        prediction = await prediction_service.create_prediction(
            db=db,
            request=request
        )
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/co2", response_model=CO2PredictionResponse, status_code=200)
async def predict_co2_only(
    request: CO2PredictionRequest
):
    """
    Predict only CO2 emissions (does not save to database).
    
    Uses the LightGBM model with R² = 0.893 and MAE = 0.153 kg.
    
    Returns:
        CO2PredictionResponse with predicted CO2 in kg
    """
    try:
        # Convert to PredictionRequest for compatibility
        pred_request = PredictionRequest(
            timestamp=request.timestamp,
            energia_comedor_kwh=request.energia_comedor_kwh,
            energia_salones_kwh=request.energia_salones_kwh,
            energia_laboratorios_kwh=request.energia_laboratorios_kwh,
            energia_auditorios_kwh=request.energia_auditorios_kwh,
            energia_oficinas_kwh=request.energia_oficinas_kwh,
            agua_litros=request.agua_litros,
            temperatura_exterior_c=request.temperatura_exterior_c,
            ocupacion_pct=request.ocupacion_pct,
            sede=request.sede,
            es_festivo=request.es_festivo,
            es_semana_parciales=request.es_semana_parciales,
            es_semana_finales=request.es_semana_finales,
            periodo_academico=request.periodo_academico
        )
        
        result = await prediction_service.predict_co2_only(pred_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/energy", response_model=EnergyPredictionResponse, status_code=200)
async def predict_energy_only(
    request: EnergyPredictionRequest
):
    """
    Predict only Energy consumption (does not save to database).
    
    IMPORTANT: This endpoint requires co2_kg as input. You can:
    1. First call /predictions/co2 to get the CO2 prediction
    2. Or use /predictions/ for combined automatic prediction
    
    Uses the Ridge model with R² = 0.998 and MAE = 0.014 kWh.
    
    Returns:
        EnergyPredictionResponse with predicted energy in kWh
    """
    try:
        # Convert to PredictionRequest for compatibility
        pred_request = PredictionRequest(
            timestamp=request.timestamp,
            energia_comedor_kwh=request.energia_comedor_kwh,
            energia_salones_kwh=request.energia_salones_kwh,
            energia_laboratorios_kwh=request.energia_laboratorios_kwh,
            energia_auditorios_kwh=request.energia_auditorios_kwh,
            energia_oficinas_kwh=request.energia_oficinas_kwh,
            agua_litros=request.agua_litros,
            temperatura_exterior_c=request.temperatura_exterior_c,
            ocupacion_pct=request.ocupacion_pct,
            sede=request.sede,
            es_festivo=request.es_festivo,
            es_semana_parciales=request.es_semana_parciales,
            es_semana_finales=request.es_semana_finales,
            periodo_academico=request.periodo_academico
        )
        
        result = await prediction_service.predict_energy_only(
            reading_id=request.reading_id,
            co2_kg=request.co2_kg,
            request=pred_request
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=PredictionBatchResponse, status_code=201)
async def create_batch_predictions(
    request: PredictionBatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create batch predictions for multiple inputs.
    
    Each prediction will:
    1. Predict CO2 using LightGBM
    2. Predict Energy using Ridge (with CO2 as input)
    3. Save to database
    
    Returns:
        PredictionBatchResponse with all predictions and summary
    """
    try:
        predictions = await prediction_service.create_batch_predictions(
            db=db,
            requests=request.predictions
        )
        
        return PredictionBatchResponse(
            predictions=predictions,
            total=len(request.predictions),
            successful=len(predictions),
            failed=len(request.predictions) - len(predictions)
        )
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
        sede: Campus name (Tunja, Duitama, Sogamoso)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
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
        sede: Campus name
        limit: Number of predictions to retrieve (default: 24)
        
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
        sede: Optional sede filter (Tunja, Duitama, Sogamoso)
        
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


@router.get("/models/info", response_model=ModelInfoResponse)
async def get_models_info():
    """
    Get information about the loaded ML models.
    
    Returns:
        ModelInfoResponse with details about:
        - CO2 model (LightGBM, 33 features, R² = 0.893)
        - Energy model (Ridge, 35 features, R² = 0.998)
        - Preprocessing (scaler, power_transformer)
    """
    try:
        info = ml_service.get_model_info()
        return ModelInfoResponse(
            models_loaded=info.get("models_loaded", False),
            co2_model={
                "name": "modelo_co2.pkl",
                "type": info.get("co2_model", {}).get("type", "LightGBM"),
                "target": "co2_kg",
                "features": info.get("co2_model", {}).get("features", 33),
                "R2": info.get("co2_model", {}).get("R2", 0.893),
                "MAE": info.get("co2_model", {}).get("MAE", 0.153)
            },
            energy_model={
                "name": "modelo_energia_B2.pkl",
                "type": info.get("energy_model", {}).get("type", "Ridge"),
                "target": "energia_total_kwh",
                "features": info.get("energy_model", {}).get("features", 35),
                "R2": info.get("energy_model", {}).get("R2", 0.998),
                "MAE": info.get("energy_model", {}).get("MAE", 0.014)
            },
            preprocessing={
                "scaler": "scaler.pkl",
                "power_transformer": "power_transformer.pkl"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def predictions_health_check():
    """
    Health check for prediction service.
    
    Verifies that all models are loaded and ready.
    """
    try:
        info = ml_service.get_model_info()
        
        if not info.get("models_loaded", False):
            return {
                "status": "unhealthy",
                "message": "Models not loaded",
                "details": info
            }
        
        return {
            "status": "healthy",
            "message": "All models loaded and ready",
            "models": {
                "co2": info.get("co2_model", {}).get("loaded", False),
                "energy": info.get("energy_model", {}).get("loaded", False)
            },
            "preprocessors": info.get("preprocessors", {})
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }
