"""
ML Inference Service for loading trained models and making predictions.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from .features import (
    prepare_prediction_features, 
    get_feature_columns,
    add_cyclical_features,
    fix_periodo_academico,
    encode_categorical
)

logger = logging.getLogger(__name__)


class MLService:
    """
    Service for loading and using trained ML models.
    Handles both prediction and anomaly detection.
    """
    
    def __init__(self, models_path: str = "ml_models"):
        """
        Initialize ML service.
        
        Args:
            models_path: Path to directory containing trained models
        """
        self.models_path = Path(models_path)
        self.predictor_model = None
        self.anomaly_model = None
        self.feature_columns: List[str] = []
        self.is_loaded = False
        
    def load_models(self) -> None:
        """Load trained models from disk."""
        try:
            # Load predictor
            predictor_path = self.models_path / "energy_predictor.joblib"
            if predictor_path.exists():
                logger.info(f"Loading predictor from {predictor_path}")
                predictor_data = joblib.load(predictor_path)
                self.predictor_model = predictor_data['model']
                self.feature_columns = predictor_data.get('feature_columns', get_feature_columns())
                logger.info(f"Predictor loaded successfully with {len(self.feature_columns)} features")
            else:
                logger.warning(f"Predictor not found at {predictor_path}")
            
            # Load anomaly detector
            anomaly_path = self.models_path / "anomaly_detector.joblib"
            if anomaly_path.exists():
                logger.info(f"Loading anomaly detector from {anomaly_path}")
                anomaly_data = joblib.load(anomaly_path)
                self.anomaly_model = anomaly_data
                logger.info("Anomaly detector loaded successfully")
            else:
                logger.warning(f"Anomaly detector not found at {anomaly_path}")
            
            self.is_loaded = True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise RuntimeError(f"Failed to load ML models: {str(e)}")
    
    def predict_consumption(
        self,
        timestamp: datetime,
        sede: str,
        temperatura_exterior_c: float = 20.0,
        ocupacion_pct: float = 70.0,
        es_festivo: bool = False,
        es_semana_parciales: bool = False,
        es_semana_finales: bool = False,
        lag_features: Optional[Dict[str, float]] = None,
        rolling_features: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Predict energy consumption for given parameters.
        
        Args:
            timestamp: Timestamp for prediction
            sede: Sede name
            temperatura_exterior_c: Exterior temperature (default: 20.0)
            ocupacion_pct: Occupancy percentage (default: 70.0)
            es_festivo: Is holiday (default: False)
            es_semana_parciales: Is midterm week (default: False)
            es_semana_finales: Is finals week (default: False)
            lag_features: Optional dictionary with lag feature values
            rolling_features: Optional dictionary with rolling feature values
            
        Returns:
            Predicted consumption in kWh
        """
        if not self.is_loaded or self.predictor_model is None:
            raise RuntimeError("Predictor model not loaded. Call load_models() first.")
        
        # Prepare features
        features_df = prepare_prediction_features(
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
        
        # Ensure all required features are present
        missing_cols = set(self.feature_columns) - set(features_df.columns)
        for col in missing_cols:
            features_df[col] = 0
        
        # Select only the features used by the model
        X = features_df[self.feature_columns].fillna(0).values
        
        # Make prediction
        prediction = self.predictor_model.predict(X)[0]
        
        # Ensure non-negative
        prediction = max(0, prediction)
        
        return float(prediction)
    
    def predict_batch(
        self,
        predictions_data: List[Dict]
    ) -> List[float]:
        """
        Make batch predictions.
        
        Args:
            predictions_data: List of dictionaries with prediction parameters
            
        Returns:
            List of predicted consumption values
        """
        if not self.is_loaded or self.predictor_model is None:
            raise RuntimeError("Predictor model not loaded. Call load_models() first.")
        
        predictions = []
        for data in predictions_data:
            try:
                pred = self.predict_consumption(**data)
                predictions.append(pred)
            except Exception as e:
                logger.error(f"Error predicting for data {data}: {str(e)}")
                predictions.append(0.0)
        
        return predictions
    
    def predict_horizon(
        self,
        sede: str,
        start_timestamp: datetime,
        horizon_hours: int = 24,
        temperatura_exterior_c: float = 20.0,
        ocupacion_pct: float = 70.0
    ) -> List[Dict]:
        """
        Predict consumption for multiple hours ahead.
        
        Args:
            sede: Sede name
            start_timestamp: Starting timestamp
            horizon_hours: Number of hours to predict (default: 24)
            temperatura_exterior_c: Exterior temperature
            ocupacion_pct: Occupancy percentage
            
        Returns:
            List of dictionaries with timestamp and predicted consumption
        """
        if not self.is_loaded or self.predictor_model is None:
            raise RuntimeError("Predictor model not loaded. Call load_models() first.")
        
        predictions = []
        previous_values = []
        
        for h in range(horizon_hours):
            current_timestamp = start_timestamp + timedelta(hours=h)
            
            # Calculate lag features from previous predictions
            lag_features = {}
            if len(previous_values) >= 1:
                lag_features['energia_total_kwh_lag_1h'] = previous_values[-1]
            if len(previous_values) >= 24:
                lag_features['energia_total_kwh_lag_24h'] = previous_values[-24]
            if len(previous_values) >= 168:
                lag_features['energia_total_kwh_lag_168h'] = previous_values[-168]
            
            # Calculate rolling features
            rolling_features = {}
            if len(previous_values) >= 24:
                rolling_features['energia_total_kwh_rolling_mean_24h'] = np.mean(previous_values[-24:])
                rolling_features['energia_total_kwh_rolling_std_24h'] = np.std(previous_values[-24:])
                rolling_features['energia_total_kwh_rolling_max_24h'] = np.max(previous_values[-24:])
            if len(previous_values) >= 168:
                rolling_features['energia_total_kwh_rolling_mean_168h'] = np.mean(previous_values[-168:])
                rolling_features['energia_total_kwh_rolling_std_168h'] = np.std(previous_values[-168:])
                rolling_features['energia_total_kwh_rolling_max_168h'] = np.max(previous_values[-168:])
            
            # Make prediction
            pred = self.predict_consumption(
                timestamp=current_timestamp,
                sede=sede,
                temperatura_exterior_c=temperatura_exterior_c,
                ocupacion_pct=ocupacion_pct,
                lag_features=lag_features if lag_features else None,
                rolling_features=rolling_features if rolling_features else None
            )
            
            predictions.append({
                'timestamp': current_timestamp,
                'predicted_kwh': pred,
                'horizon_hours': h + 1
            })
            
            previous_values.append(pred)
        
        return predictions
    
    def detect_anomalies(
        self,
        consumption_data: pd.DataFrame,
        severity_threshold: Optional[str] = None
    ) -> List[Dict]:
        """
        Detect anomalies in consumption data.
        
        Args:
            consumption_data: DataFrame with consumption records
            severity_threshold: Optional severity filter ('low', 'medium', 'high', 'critical')
            
        Returns:
            List of detected anomalies
        """
        if not self.is_loaded or self.anomaly_model is None:
            raise RuntimeError("Anomaly model not loaded. Call load_models() first.")
        
        # This is a simplified version. Full implementation would use the loaded detector
        anomalies = []
        
        try:
            # Use Isolation Forest from loaded model
            isolation_forest = self.anomaly_model.get('isolation_forest')
            baselines = self.anomaly_model.get('baselines', {})
            z_threshold = self.anomaly_model.get('z_threshold', 3.0)
            
            if isolation_forest is None:
                logger.warning("Isolation Forest not found in anomaly model")
                return anomalies
            
            # Prepare features for anomaly detection
            features = ['energia_total_kwh', 'hora', 'dia_semana']
            available_features = [f for f in features if f in consumption_data.columns]
            
            if not available_features:
                logger.warning("No valid features for anomaly detection")
                return anomalies
            
            # Predict anomalies (-1 for anomaly, 1 for normal)
            X = consumption_data[available_features].fillna(0).values
            predictions = isolation_forest.predict(X)
            
            # Filter anomalies
            anomaly_indices = np.where(predictions == -1)[0]
            
            for idx in anomaly_indices:
                row = consumption_data.iloc[idx]
                
                # Calculate deviation from baseline if available
                sede = row.get('sede', 'unknown')
                hora = int(row.get('hora', 0))
                es_fin_semana = row.get('es_fin_semana', False)
                day_type = 'weekend' if es_fin_semana else 'weekday'
                
                expected_value = row['energia_total_kwh']
                deviation_pct = 0.0
                
                if sede in baselines:
                    key = f'{day_type}_hour_{hora}'
                    if key in baselines[sede]:
                        baseline = baselines[sede][key]
                        expected_value = baseline.get('mean', row['energia_total_kwh'])
                        if expected_value > 0:
                            deviation_pct = ((row['energia_total_kwh'] - expected_value) / expected_value) * 100
                
                # Determine severity
                severity = 'low'
                if abs(deviation_pct) > 100:
                    severity = 'critical'
                elif abs(deviation_pct) > 50:
                    severity = 'high'
                elif abs(deviation_pct) > 30:
                    severity = 'medium'
                
                # Apply severity filter
                if severity_threshold and severity != severity_threshold:
                    if severity_threshold == 'high' and severity not in ['high', 'critical']:
                        continue
                    elif severity_threshold == 'critical' and severity != 'critical':
                        continue
                
                anomalies.append({
                    'timestamp': row.get('timestamp', datetime.now()),
                    'sede': sede,
                    'sector': 'total',
                    'anomaly_type': 'statistical_outlier',
                    'severity': severity,
                    'actual_value': float(row['energia_total_kwh']),
                    'expected_value': float(expected_value),
                    'deviation_pct': float(deviation_pct),
                    'description': f"Consumo {'elevado' if deviation_pct > 0 else 'bajo'} detectado",
                    'recommendation': "Verificar equipos y condiciones de operacion"
                })
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
        
        return anomalies
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model information
        """
        return {
            'predictor_loaded': self.predictor_model is not None,
            'anomaly_detector_loaded': self.anomaly_model is not None,
            'feature_count': len(self.feature_columns),
            'feature_columns': self.feature_columns,
            'models_path': str(self.models_path)
        }


# Global ML service instance
ml_service = MLService()
