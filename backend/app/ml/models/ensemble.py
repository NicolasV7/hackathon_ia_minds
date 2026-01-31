"""
Ensemble predictor combining multiple models for robust energy prediction.

Combines:
- Prophet (trend and seasonality)
- XGBoost (feature-based prediction)
- Simple average/weighted ensemble

The ensemble approach provides:
- More robust predictions
- Better uncertainty quantification
- Flexibility to add/remove models
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import pandas as pd
import joblib

# Prophet is optional - uncomment if installed
# from .prophet_model import ProphetPredictor, PROPHET_AVAILABLE
PROPHET_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Ensemble predictor combining Prophet and XGBoost models.
    
    Weighting strategies:
    - equal: Equal weights for all models
    - performance: Weights based on validation performance
    - adaptive: Adjust weights based on prediction context
    """
    
    def __init__(
        self,
        sede: str,
        model_dir: Optional[Path] = None,
        strategy: str = 'performance'
    ):
        """
        Initialize EnsemblePredictor.
        
        Args:
            sede: Sede name
            model_dir: Directory for model files
            strategy: Weighting strategy ('equal', 'performance', 'adaptive')
        """
        self.sede = sede
        self.model_dir = model_dir or Path("ml_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.strategy = strategy
        
        # Model weights (updated during training)
        self.weights = {
            'prophet': 0.5,
            'xgboost': 0.5
        }
        
        # Models
        self.prophet_model: Optional[Any] = None
        self.xgboost_model: Optional[Any] = None
        
        # Validation metrics
        self.val_metrics = {}
        
        # Feature columns for XGBoost
        self.feature_cols = None
        
        self.is_fitted = False
    
    def _load_xgboost_model(self) -> bool:
        """Load existing XGBoost model."""
        model_path = self.model_dir / "energy_predictor.joblib"
        
        if model_path.exists():
            try:
                self.xgboost_model = joblib.load(model_path)
                logger.info(f"XGBoost model loaded from {model_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load XGBoost model: {e}")
        
        return False
    
    def _prepare_xgboost_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for XGBoost prediction."""
        from ..features import prepare_full_feature_set, get_feature_columns
        
        # Apply feature engineering
        featured_df = prepare_full_feature_set(df)
        
        # Get feature columns
        if self.feature_cols is None:
            self.feature_cols = get_feature_columns()
        
        # Select features, filling missing with 0
        X = featured_df.reindex(columns=self.feature_cols, fill_value=0)
        
        return X
    
    def fit(
        self,
        df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None
    ) -> 'EnsemblePredictor':
        """
        Fit the ensemble model.
        
        Args:
            df: Training DataFrame
            val_df: Validation DataFrame for weight calibration
            
        Returns:
            self for chaining
        """
        logger.info(f"Fitting ensemble model for sede {self.sede}")
        
        # Filter for this sede
        train_df = df[df['sede'] == self.sede].copy()
        
        if len(train_df) < 168:
            raise ValueError(f"Not enough data: {len(train_df)} rows")
        
        # 1. Fit Prophet model (disabled - not installed)
        if PROPHET_AVAILABLE:
            logger.info("Prophet not available, skipping Prophet model")
            self.prophet_model = None
        
        # 2. Load/use existing XGBoost model
        self._load_xgboost_model()
        
        # 3. Calibrate weights using validation data
        if val_df is not None and len(val_df) > 0:
            self._calibrate_weights(val_df)
        
        self.is_fitted = True
        logger.info(f"Ensemble fitted with weights: {self.weights}")
        
        return self
    
    def _calibrate_weights(self, val_df: pd.DataFrame):
        """Calibrate model weights based on validation performance."""
        val_sede = val_df[val_df['sede'] == self.sede].copy()
        
        if len(val_sede) < 24:
            logger.warning("Not enough validation data for calibration")
            return
        
        errors = {}
        
        # Evaluate Prophet
        if self.prophet_model and self.prophet_model.is_fitted:
            try:
                prophet_preds = self.prophet_model.predict(
                    val_sede, include_history=True
                )
                prophet_preds = prophet_preds.set_index('timestamp')
                
                val_indexed = val_sede.set_index('timestamp')
                common_idx = prophet_preds.index.intersection(val_indexed.index)
                
                if len(common_idx) > 0:
                    mae = np.mean(np.abs(
                        prophet_preds.loc[common_idx, 'predicted_kwh'].values - 
                        val_indexed.loc[common_idx, 'energia_total_kwh'].values
                    ))
                    errors['prophet'] = mae
            except Exception as e:
                logger.warning(f"Prophet validation failed: {e}")
        
        # Evaluate XGBoost
        if self.xgboost_model is not None:
            try:
                X_val = self._prepare_xgboost_features(val_sede)
                xgb_preds = self.xgboost_model.predict(X_val)
                mae = np.mean(np.abs(xgb_preds - val_sede['energia_total_kwh'].values))
                errors['xgboost'] = mae
            except Exception as e:
                logger.warning(f"XGBoost validation failed: {e}")
        
        # Calculate weights (inverse error weighting)
        if errors:
            total_inv_error = sum(1 / (e + 0.001) for e in errors.values())
            
            for model_name in ['prophet', 'xgboost']:
                if model_name in errors:
                    self.weights[model_name] = (1 / (errors[model_name] + 0.001)) / total_inv_error
                else:
                    self.weights[model_name] = 0
            
            self.val_metrics = errors
            logger.info(f"Calibrated weights: {self.weights}, MAEs: {errors}")
    
    def predict(
        self,
        df: pd.DataFrame = None,
        timestamp: datetime = None,
        periods: int = 24,
        temperatura_exterior_c: float = 14.0,
        ocupacion_pct: float = 70.0
    ) -> pd.DataFrame:
        """
        Generate ensemble predictions.
        
        Args:
            df: DataFrame with features (optional)
            timestamp: Start timestamp for prediction
            periods: Number of hours to predict
            temperatura_exterior_c: Temperature
            ocupacion_pct: Occupancy percentage
            
        Returns:
            DataFrame with ensemble predictions
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        predictions = {}
        
        # Generate timestamps if not provided
        if timestamp is None:
            timestamp = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        future_dates = pd.date_range(start=timestamp, periods=periods, freq='H')
        
        # Prophet predictions
        if self.prophet_model and self.prophet_model.is_fitted and self.weights['prophet'] > 0:
            try:
                prophet_preds = self.prophet_model.predict_horizon(
                    start_timestamp=timestamp,
                    horizon_hours=periods,
                    temperatura_exterior_c=temperatura_exterior_c,
                    ocupacion_pct=ocupacion_pct
                )
                predictions['prophet'] = pd.DataFrame(prophet_preds).set_index('timestamp')['predicted_kwh']
            except Exception as e:
                logger.warning(f"Prophet prediction failed: {e}")
        
        # XGBoost predictions
        if self.xgboost_model is not None and self.weights['xgboost'] > 0:
            try:
                # Create feature dataframe for future
                future_df = self._create_future_features(
                    future_dates, temperatura_exterior_c, ocupacion_pct
                )
                X = self._prepare_xgboost_features(future_df)
                xgb_preds = self.xgboost_model.predict(X)
                predictions['xgboost'] = pd.Series(xgb_preds, index=future_dates)
            except Exception as e:
                logger.warning(f"XGBoost prediction failed: {e}")
        
        # Combine predictions
        if not predictions:
            logger.warning("No model predictions available, using fallback")
            return self._fallback_prediction(future_dates)
        
        # Weighted ensemble
        result_df = pd.DataFrame({'timestamp': future_dates})
        
        ensemble_pred = np.zeros(len(future_dates))
        total_weight = 0
        
        for model_name, preds in predictions.items():
            weight = self.weights.get(model_name, 0)
            if weight > 0:
                # Align predictions with future_dates
                aligned_preds = preds.reindex(future_dates).fillna(method='ffill').fillna(0)
                ensemble_pred += weight * aligned_preds.values
                total_weight += weight
        
        if total_weight > 0:
            ensemble_pred /= total_weight
        
        result_df['predicted_kwh'] = np.clip(ensemble_pred, 0, None)
        result_df['sede'] = self.sede
        
        # Estimate confidence based on model agreement
        if len(predictions) > 1:
            pred_values = np.array([p.reindex(future_dates).fillna(0).values for p in predictions.values()])
            std = np.std(pred_values, axis=0)
            mean = np.mean(pred_values, axis=0)
            cv = std / (mean + 0.001)  # Coefficient of variation
            result_df['confidence_score'] = np.clip(1 - cv, 0, 1)
        else:
            result_df['confidence_score'] = 0.7
        
        # Add bounds (approximate)
        result_df['lower_bound'] = result_df['predicted_kwh'] * 0.85
        result_df['upper_bound'] = result_df['predicted_kwh'] * 1.15
        
        return result_df
    
    def _create_future_features(
        self,
        dates: pd.DatetimeIndex,
        temperatura: float,
        ocupacion: float
    ) -> pd.DataFrame:
        """Create feature DataFrame for future timestamps."""
        df = pd.DataFrame({
            'timestamp': dates,
            'sede': self.sede,
            'hora': dates.hour,
            'dia_semana': dates.weekday,
            'mes': dates.month,
            'año': dates.year,
            'temperatura_exterior_c': temperatura,
            'ocupacion_pct': [
                ocupacion if d.weekday() < 5 and 7 <= d.hour <= 18 else ocupacion * 0.2
                for d in dates
            ],
            'es_fin_semana': dates.weekday >= 5,
            'es_festivo': False,
            'es_semana_parciales': False,
            'es_semana_finales': False,
            'energia_total_kwh': 0,  # Placeholder
            'energia_comedor_kwh': 0,
            'energia_salones_kwh': 0,
            'energia_laboratorios_kwh': 0,
            'energia_auditorios_kwh': 0,
            'energia_oficinas_kwh': 0,
        })
        
        return df
    
    def _fallback_prediction(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate fallback predictions when models fail."""
        # Simple heuristic based on time of day
        predictions = []
        
        for dt in dates:
            hour = dt.hour
            is_weekend = dt.weekday() >= 5
            
            # Base consumption pattern (simplified)
            if is_weekend:
                base = 1.5
            elif 7 <= hour <= 18:
                base = 3.5
            elif 22 <= hour or hour <= 5:
                base = 1.0
            else:
                base = 2.0
            
            predictions.append(base)
        
        return pd.DataFrame({
            'timestamp': dates,
            'predicted_kwh': predictions,
            'confidence_score': 0.5,
            'lower_bound': [p * 0.7 for p in predictions],
            'upper_bound': [p * 1.3 for p in predictions],
            'sede': self.sede
        })
    
    def predict_horizon(
        self,
        start_timestamp: datetime,
        horizon_hours: int = 24,
        temperatura_exterior_c: float = 14.0,
        ocupacion_pct: float = 70.0
    ) -> List[Dict[str, Any]]:
        """
        Predict for a specific horizon (compatible with existing API).
        
        Args:
            start_timestamp: Starting timestamp
            horizon_hours: Hours to predict
            temperatura_exterior_c: Temperature
            ocupacion_pct: Occupancy
            
        Returns:
            List of prediction dictionaries
        """
        result_df = self.predict(
            timestamp=start_timestamp,
            periods=horizon_hours,
            temperatura_exterior_c=temperatura_exterior_c,
            ocupacion_pct=ocupacion_pct
        )
        
        return [
            {
                'timestamp': row['timestamp'],
                'predicted_kwh': row['predicted_kwh'],
                'confidence_score': row['confidence_score'],
                'sede': self.sede
            }
            for _, row in result_df.iterrows()
        ]
    
    def save(self, filename: Optional[str] = None) -> Path:
        """Save the ensemble model."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model.")
        
        filename = filename or f"ensemble_{self.sede.lower()}.joblib"
        filepath = self.model_dir / filename
        
        # Save Prophet model separately
        if self.prophet_model:
            self.prophet_model.save()
        
        # Save ensemble metadata
        joblib.dump({
            'sede': self.sede,
            'weights': self.weights,
            'strategy': self.strategy,
            'val_metrics': self.val_metrics,
            'feature_cols': self.feature_cols
        }, filepath)
        
        logger.info(f"Ensemble saved to {filepath}")
        return filepath
    
    def load(self, filename: Optional[str] = None) -> 'EnsemblePredictor':
        """Load the ensemble model."""
        filename = filename or f"ensemble_{self.sede.lower()}.joblib"
        filepath = self.model_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Ensemble file not found: {filepath}")
        
        data = joblib.load(filepath)
        
        self.sede = data['sede']
        self.weights = data['weights']
        self.strategy = data['strategy']
        self.val_metrics = data.get('val_metrics', {})
        self.feature_cols = data.get('feature_cols')
        
        # Load Prophet model (disabled - not installed)
        if PROPHET_AVAILABLE:
            logger.info("Prophet not available, skipping Prophet model load")
            self.prophet_model = None
        
        # Load XGBoost
        self._load_xgboost_model()
        
        self.is_fitted = True
        logger.info(f"Ensemble loaded from {filepath}")
        
        return self


class MultiSedeEnsemble:
    """
    Wrapper to manage ensemble models for all sedes.
    """
    
    SEDES = ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquira']
    
    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or Path("ml_models")
        self.models: Dict[str, EnsemblePredictor] = {}
    
    def fit_all(self, df: pd.DataFrame, val_df: Optional[pd.DataFrame] = None):
        """Fit models for all sedes."""
        for sede in self.SEDES:
            logger.info(f"Fitting model for {sede}")
            self.models[sede] = EnsemblePredictor(
                sede=sede,
                model_dir=self.model_dir
            )
            try:
                self.models[sede].fit(df, val_df)
            except Exception as e:
                logger.error(f"Failed to fit {sede}: {e}")
    
    def predict(self, sede: str, **kwargs) -> pd.DataFrame:
        """Get predictions for a specific sede."""
        if sede not in self.models:
            raise ValueError(f"No model for sede {sede}")
        return self.models[sede].predict(**kwargs)
    
    def predict_all(self, **kwargs) -> Dict[str, pd.DataFrame]:
        """Get predictions for all sedes."""
        return {
            sede: model.predict(**kwargs)
            for sede, model in self.models.items()
        }
