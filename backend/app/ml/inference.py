"""
ML Inference Service for CO2 and Energy prediction models.

This module loads and uses the trained models:
- modelo_co2.pkl (LightGBM) - Predicts CO2 emissions
- modelo_energia_B2.pkl (Ridge) - Predicts energy consumption

Preprocessing pipeline:
1. Prepare features in exact order
2. Apply PowerTransformer to specified columns
3. Apply Scaler to specified columns
4. Pass to model for prediction
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

from .features import (
    CO2_FEATURE_ORDER,
    ENERGY_B2_FEATURE_ORDER,
    COLS_TO_TRANSFORM,
    COLS_TO_SCALE,
    prepare_features_for_co2_model,
    prepare_features_for_energy_model,
    features_dict_to_array,
    validate_features_not_null,
    get_missing_features
)

logger = logging.getLogger(__name__)


class MLService:
    """
    Service for loading and using trained ML models.
    Handles CO2 and Energy predictions with proper preprocessing.
    """
    
    def __init__(self, models_path: str = "newmodels"):
        """
        Initialize ML service.
        
        Args:
            models_path: Path to directory containing trained models
        """
        self.models_path = Path(models_path)
        
        # Models
        self.co2_model = None
        self.energy_model = None
        
        # Preprocessors
        self.scaler = None
        self.power_transformer = None
        
        # State
        self.is_loaded = False
        
        # Model metadata
        self.co2_model_info = {
            "type": "LightGBM",
            "target": "co2_kg",
            "features": 33,
            "R2": 0.893,
            "RMSE": 0.327,
            "MAE": 0.153
        }
        
        self.energy_model_info = {
            "type": "Ridge",
            "target": "energia_total_kwh",
            "features": 35,
            "R2": 0.998,
            "RMSE": 0.049,
            "MAE": 0.014
        }
        
    def load_models(self) -> None:
        """Load trained models and preprocessors from disk."""
        try:
            # Load CO2 model
            co2_path = self.models_path / "modelo_co2.pkl"
            if co2_path.exists():
                logger.info(f"Loading CO2 model from {co2_path}")
                self.co2_model = joblib.load(co2_path)
                logger.info("CO2 model (LightGBM) loaded successfully")
            else:
                logger.error(f"CO2 model not found at {co2_path}")
                raise FileNotFoundError(f"CO2 model not found at {co2_path}")
            
            # Load Energy model
            energy_path = self.models_path / "modelo_energia_B2.pkl"
            if energy_path.exists():
                logger.info(f"Loading Energy model from {energy_path}")
                self.energy_model = joblib.load(energy_path)
                logger.info("Energy model (Ridge) loaded successfully")
            else:
                logger.error(f"Energy model not found at {energy_path}")
                raise FileNotFoundError(f"Energy model not found at {energy_path}")
            
            # Load Scaler
            scaler_path = self.models_path / "scaler.pkl"
            if scaler_path.exists():
                logger.info(f"Loading Scaler from {scaler_path}")
                self.scaler = joblib.load(scaler_path)
                logger.info("Scaler loaded successfully")
            else:
                logger.error(f"Scaler not found at {scaler_path}")
                raise FileNotFoundError(f"Scaler not found at {scaler_path}")
            
            # Load PowerTransformer
            pt_path = self.models_path / "power_transformer.pkl"
            if pt_path.exists():
                logger.info(f"Loading PowerTransformer from {pt_path}")
                self.power_transformer = joblib.load(pt_path)
                logger.info("PowerTransformer loaded successfully")
            else:
                logger.error(f"PowerTransformer not found at {pt_path}")
                raise FileNotFoundError(f"PowerTransformer not found at {pt_path}")
            
            self.is_loaded = True
            logger.info("All models and preprocessors loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            self.is_loaded = False
            raise RuntimeError(f"Failed to load ML models: {str(e)}")
    
    def _preprocess_features(
        self, 
        features_df: pd.DataFrame,
        feature_order: List[str]
    ) -> np.ndarray:
        """
        Apply preprocessing pipeline to features.
        
        Pipeline:
        1. Ensure correct column order
        2. Apply PowerTransformer to specified columns
        3. Apply Scaler to specified columns
        
        Args:
            features_df: DataFrame with features
            feature_order: List of feature names in required order
            
        Returns:
            Preprocessed numpy array ready for prediction
        """
        # Ensure we have the right columns in right order
        df = features_df[feature_order].copy()
        
        # Identify which columns to transform (intersection with available)
        cols_to_transform = [c for c in COLS_TO_TRANSFORM if c in df.columns]
        cols_to_scale = [c for c in COLS_TO_SCALE if c in df.columns]
        
        # Apply PowerTransformer to specified columns
        if self.power_transformer is not None and cols_to_transform:
            try:
                # Get indices of columns to transform
                transform_indices = [feature_order.index(c) for c in cols_to_transform if c in feature_order]
                if transform_indices:
                    values_to_transform = df[cols_to_transform].values
                    # Only transform if we have the right number of features
                    if values_to_transform.shape[1] == self.power_transformer.n_features_in_:
                        transformed = self.power_transformer.transform(values_to_transform)
                        for i, col in enumerate(cols_to_transform):
                            df[col] = transformed[:, i]
            except Exception as e:
                logger.warning(f"PowerTransformer warning: {e}. Continuing without transform.")
        
        # Apply Scaler to specified columns
        if self.scaler is not None and cols_to_scale:
            try:
                # Get indices of columns to scale
                values_to_scale = df[cols_to_scale].values
                # Only scale if we have the right number of features
                if values_to_scale.shape[1] == self.scaler.n_features_in_:
                    scaled = self.scaler.transform(values_to_scale)
                    for i, col in enumerate(cols_to_scale):
                        df[col] = scaled[:, i]
            except Exception as e:
                logger.warning(f"Scaler warning: {e}. Continuing without scaling.")
        
        return df.values
    
    def predict_co2(
        self,
        energia_comedor_kwh: float,
        energia_salones_kwh: float,
        energia_laboratorios_kwh: float,
        energia_auditorios_kwh: float,
        energia_oficinas_kwh: float,
        agua_litros: float,
        temperatura_exterior_c: float,
        ocupacion_pct: float,
        sede: str,
        timestamp: datetime,
        es_festivo: bool = False,
        es_semana_parciales: bool = False,
        es_semana_finales: bool = False,
        periodo_academico: Optional[str] = None
    ) -> float:
        """
        Predict CO2 emissions using the LightGBM model.
        
        Args:
            All required features for the model
            
        Returns:
            Predicted CO2 in kg
        """
        if not self.is_loaded or self.co2_model is None:
            raise RuntimeError("CO2 model not loaded. Call load_models() first.")
        
        # Prepare features
        features = prepare_features_for_co2_model(
            energia_comedor_kwh=energia_comedor_kwh,
            energia_salones_kwh=energia_salones_kwh,
            energia_laboratorios_kwh=energia_laboratorios_kwh,
            energia_auditorios_kwh=energia_auditorios_kwh,
            energia_oficinas_kwh=energia_oficinas_kwh,
            agua_litros=agua_litros,
            temperatura_exterior_c=temperatura_exterior_c,
            ocupacion_pct=ocupacion_pct,
            sede=sede,
            timestamp=timestamp,
            es_festivo=es_festivo,
            es_semana_parciales=es_semana_parciales,
            es_semana_finales=es_semana_finales,
            periodo_academico=periodo_academico
        )
        
        # Validate no null values
        if not validate_features_not_null(features):
            missing = get_missing_features(features)
            raise ValueError(f"Null values detected in features: {missing}")
        
        # Convert to DataFrame for preprocessing
        features_df = pd.DataFrame([features])
        
        # Ensure column order matches expected
        features_df = features_df[CO2_FEATURE_ORDER]
        
        # Get values as array (preprocessing is handled by model internally for LightGBM)
        X = features_df.values
        
        # Make prediction
        prediction = self.co2_model.predict(X)[0]
        
        # Ensure non-negative
        prediction = max(0, float(prediction))
        
        logger.debug(f"CO2 prediction: {prediction} kg")
        return prediction
    
    def predict_energy(
        self,
        reading_id: int,
        energia_comedor_kwh: float,
        energia_salones_kwh: float,
        energia_laboratorios_kwh: float,
        energia_auditorios_kwh: float,
        energia_oficinas_kwh: float,
        agua_litros: float,
        temperatura_exterior_c: float,
        ocupacion_pct: float,
        co2_kg: float,
        sede: str,
        timestamp: datetime,
        es_festivo: bool = False,
        es_semana_parciales: bool = False,
        es_semana_finales: bool = False,
        periodo_academico: Optional[str] = None
    ) -> float:
        """
        Predict energy consumption using the Ridge model.
        
        Args:
            All required features for the model (including co2_kg)
            
        Returns:
            Predicted energy consumption in kWh
        """
        if not self.is_loaded or self.energy_model is None:
            raise RuntimeError("Energy model not loaded. Call load_models() first.")
        
        # Prepare features
        features = prepare_features_for_energy_model(
            reading_id=reading_id,
            energia_comedor_kwh=energia_comedor_kwh,
            energia_salones_kwh=energia_salones_kwh,
            energia_laboratorios_kwh=energia_laboratorios_kwh,
            energia_auditorios_kwh=energia_auditorios_kwh,
            energia_oficinas_kwh=energia_oficinas_kwh,
            agua_litros=agua_litros,
            temperatura_exterior_c=temperatura_exterior_c,
            ocupacion_pct=ocupacion_pct,
            co2_kg=co2_kg,
            sede=sede,
            timestamp=timestamp,
            es_festivo=es_festivo,
            es_semana_parciales=es_semana_parciales,
            es_semana_finales=es_semana_finales,
            periodo_academico=periodo_academico
        )
        
        # Validate no null values
        if not validate_features_not_null(features):
            missing = get_missing_features(features)
            raise ValueError(f"Null values detected in features: {missing}")
        
        # Convert to DataFrame for preprocessing
        features_df = pd.DataFrame([features])
        
        # Ensure column order matches expected
        features_df = features_df[ENERGY_B2_FEATURE_ORDER]
        
        # Get values as array
        X = features_df.values
        
        # Make prediction
        prediction = self.energy_model.predict(X)[0]
        
        # Ensure non-negative
        prediction = max(0, float(prediction))
        
        logger.debug(f"Energy prediction: {prediction} kWh")
        return prediction
    
    def predict_combined(
        self,
        energia_comedor_kwh: float,
        energia_salones_kwh: float,
        energia_laboratorios_kwh: float,
        energia_auditorios_kwh: float,
        energia_oficinas_kwh: float,
        agua_litros: float,
        temperatura_exterior_c: float,
        ocupacion_pct: float,
        sede: str,
        timestamp: datetime,
        reading_id: Optional[int] = None,
        es_festivo: bool = False,
        es_semana_parciales: bool = False,
        es_semana_finales: bool = False,
        periodo_academico: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Combined prediction: First predicts CO2, then uses it to predict Energy.
        
        This is the main method for predictions as the Energy model requires
        CO2 as an input feature.
        
        Args:
            All required features (reading_id is auto-generated if not provided)
            
        Returns:
            Dictionary with:
                - predicted_co2_kg: CO2 prediction
                - predicted_energy_kwh: Energy prediction
                - confidence_co2: Model R² for CO2
                - confidence_energy: Model R² for Energy
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        # Generate reading_id if not provided
        if reading_id is None:
            reading_id = int(timestamp.timestamp())
        
        # Step 1: Predict CO2
        predicted_co2 = self.predict_co2(
            energia_comedor_kwh=energia_comedor_kwh,
            energia_salones_kwh=energia_salones_kwh,
            energia_laboratorios_kwh=energia_laboratorios_kwh,
            energia_auditorios_kwh=energia_auditorios_kwh,
            energia_oficinas_kwh=energia_oficinas_kwh,
            agua_litros=agua_litros,
            temperatura_exterior_c=temperatura_exterior_c,
            ocupacion_pct=ocupacion_pct,
            sede=sede,
            timestamp=timestamp,
            es_festivo=es_festivo,
            es_semana_parciales=es_semana_parciales,
            es_semana_finales=es_semana_finales,
            periodo_academico=periodo_academico
        )
        
        # Step 2: Predict Energy using the CO2 prediction
        predicted_energy = self.predict_energy(
            reading_id=reading_id,
            energia_comedor_kwh=energia_comedor_kwh,
            energia_salones_kwh=energia_salones_kwh,
            energia_laboratorios_kwh=energia_laboratorios_kwh,
            energia_auditorios_kwh=energia_auditorios_kwh,
            energia_oficinas_kwh=energia_oficinas_kwh,
            agua_litros=agua_litros,
            temperatura_exterior_c=temperatura_exterior_c,
            ocupacion_pct=ocupacion_pct,
            co2_kg=predicted_co2,
            sede=sede,
            timestamp=timestamp,
            es_festivo=es_festivo,
            es_semana_parciales=es_semana_parciales,
            es_semana_finales=es_semana_finales,
            periodo_academico=periodo_academico
        )
        
        return {
            "predicted_co2_kg": predicted_co2,
            "predicted_energy_kwh": predicted_energy,
            "confidence_co2": self.co2_model_info["R2"],
            "confidence_energy": self.energy_model_info["R2"]
        }
    
    def predict_batch(
        self,
        predictions_data: List[Dict]
    ) -> List[Dict[str, float]]:
        """
        Make batch predictions.
        
        Args:
            predictions_data: List of dictionaries with prediction parameters
            
        Returns:
            List of prediction results
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        results = []
        for data in predictions_data:
            try:
                result = self.predict_combined(**data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error predicting for data {data}: {str(e)}")
                results.append({
                    "predicted_co2_kg": 0.0,
                    "predicted_energy_kwh": 0.0,
                    "confidence_co2": 0.0,
                    "confidence_energy": 0.0,
                    "error": str(e)
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model information
        """
        return {
            "models_loaded": self.is_loaded,
            "models_path": str(self.models_path),
            "co2_model": {
                "loaded": self.co2_model is not None,
                **self.co2_model_info
            },
            "energy_model": {
                "loaded": self.energy_model is not None,
                **self.energy_model_info
            },
            "preprocessors": {
                "scaler_loaded": self.scaler is not None,
                "power_transformer_loaded": self.power_transformer is not None
            }
        }


# Global ML service instance
ml_service = MLService()
