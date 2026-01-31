"""
Prophet model wrapper for energy consumption prediction.

Prophet is excellent for:
- Capturing multiple seasonalities (daily, weekly, yearly)
- Handling holidays and special events
- Providing uncertainty intervals
- Working with missing data
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

import joblib

logger = logging.getLogger(__name__)


# Colombian holidays for Prophet
COLOMBIAN_HOLIDAYS = pd.DataFrame({
    'holiday': [
        'ano_nuevo', 'reyes_magos', 'san_jose', 'jueves_santo', 'viernes_santo',
        'dia_trabajo', 'ascension', 'corpus_christi', 'sagrado_corazon',
        'san_pedro_pablo', 'independencia', 'batalla_boyaca', 'asuncion',
        'dia_raza', 'todos_santos', 'independencia_cartagena', 
        'inmaculada_concepcion', 'navidad'
    ],
    'ds': pd.to_datetime([
        '2024-01-01', '2024-01-08', '2024-03-25', '2024-03-28', '2024-03-29',
        '2024-05-01', '2024-05-13', '2024-06-03', '2024-06-10',
        '2024-07-01', '2024-07-20', '2024-08-07', '2024-08-19',
        '2024-10-14', '2024-11-04', '2024-11-11',
        '2024-12-08', '2024-12-25'
    ]),
    'lower_window': 0,
    'upper_window': 0,
})


class ProphetPredictor:
    """
    Prophet-based predictor for energy consumption.
    
    Features:
    - Automatic seasonality detection (daily, weekly, yearly)
    - Holiday effects for Colombian calendar
    - External regressors (temperature, occupancy)
    - Uncertainty quantification
    """
    
    def __init__(
        self,
        sede: str,
        model_dir: Optional[Path] = None,
        **prophet_kwargs
    ):
        """
        Initialize ProphetPredictor.
        
        Args:
            sede: Sede name for this model
            model_dir: Directory to save/load models
            **prophet_kwargs: Additional Prophet parameters
        """
        if not PROPHET_AVAILABLE:
            raise ImportError(
                "Prophet not installed. Install with: pip install prophet"
            )
        
        self.sede = sede
        self.model_dir = model_dir or Path("ml_models/prophet")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model: Optional[Prophet] = None
        self.is_fitted = False
        
        # Default Prophet configuration optimized for energy data
        self.prophet_config = {
            'growth': 'linear',
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': True,
            'seasonality_mode': 'multiplicative',  # Better for energy data
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10,
            'holidays_prior_scale': 10,
            'interval_width': 0.95,
            **prophet_kwargs
        }
        
        # Regressors to add
        self.regressors = [
            'temperatura_exterior_c',
            'ocupacion_pct',
            'es_festivo',
            'es_semana_parciales',
            'es_semana_finales'
        ]
    
    def _create_model(self) -> Prophet:
        """Create a new Prophet model with configured parameters."""
        model = Prophet(**self.prophet_config)
        
        # Add Colombian holidays
        model.add_country_holidays(country_name='CO')
        
        # Add custom regressors
        for regressor in self.regressors:
            model.add_regressor(regressor, standardize=True)
        
        # Add custom seasonalities for academic calendar
        model.add_seasonality(
            name='semestre',
            period=182.5,  # ~6 months
            fourier_order=5
        )
        
        return model
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare DataFrame for Prophet.
        
        Args:
            df: Input DataFrame with timestamp and energia_total_kwh
            
        Returns:
            DataFrame with ds, y, and regressor columns
        """
        prophet_df = df.copy()
        
        # Ensure required columns exist
        prophet_df['ds'] = pd.to_datetime(prophet_df['timestamp'])
        prophet_df['y'] = prophet_df['energia_total_kwh']
        
        # Fill missing regressors with defaults
        defaults = {
            'temperatura_exterior_c': 14.0,  # Boyacá average
            'ocupacion_pct': 50.0,
            'es_festivo': False,
            'es_semana_parciales': False,
            'es_semana_finales': False
        }
        
        for reg in self.regressors:
            if reg not in prophet_df.columns:
                prophet_df[reg] = defaults.get(reg, 0)
            else:
                prophet_df[reg] = prophet_df[reg].fillna(defaults.get(reg, 0))
        
        # Convert booleans to int
        for col in ['es_festivo', 'es_semana_parciales', 'es_semana_finales']:
            if col in prophet_df.columns:
                prophet_df[col] = prophet_df[col].astype(int)
        
        # Select only needed columns
        cols = ['ds', 'y'] + self.regressors
        return prophet_df[cols].dropna(subset=['ds', 'y'])
    
    def fit(self, df: pd.DataFrame) -> 'ProphetPredictor':
        """
        Fit the Prophet model.
        
        Args:
            df: Training DataFrame with timestamp and energia_total_kwh
            
        Returns:
            self for chaining
        """
        logger.info(f"Fitting Prophet model for sede {self.sede}")
        
        # Filter for this sede
        sede_df = df[df['sede'] == self.sede].copy()
        
        if len(sede_df) < 168:  # At least 1 week of hourly data
            raise ValueError(f"Not enough data for sede {self.sede}: {len(sede_df)} rows")
        
        # Prepare data
        train_df = self._prepare_dataframe(sede_df)
        
        # Create and fit model
        self.model = self._create_model()
        self.model.fit(train_df)
        
        self.is_fitted = True
        logger.info(f"Prophet model fitted for {self.sede} with {len(train_df)} samples")
        
        return self
    
    def predict(
        self,
        future_df: pd.DataFrame = None,
        periods: int = 24,
        freq: str = 'H',
        include_history: bool = False
    ) -> pd.DataFrame:
        """
        Generate predictions.
        
        Args:
            future_df: DataFrame with future timestamps and regressors
            periods: Number of periods to predict (if future_df not provided)
            freq: Frequency ('H' for hourly)
            include_history: Whether to include historical predictions
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        if future_df is None:
            # Create future dataframe
            future_df = self.model.make_future_dataframe(
                periods=periods,
                freq=freq,
                include_history=include_history
            )
            
            # Add default regressor values for future
            for reg in self.regressors:
                if reg not in future_df.columns:
                    if reg == 'temperatura_exterior_c':
                        future_df[reg] = 14.0
                    elif reg == 'ocupacion_pct':
                        # Estimate occupancy based on hour and day
                        future_df[reg] = future_df['ds'].apply(
                            lambda x: 70 if x.weekday() < 5 and 7 <= x.hour <= 18 else 20
                        )
                    else:
                        future_df[reg] = 0
        else:
            future_df = self._prepare_dataframe(future_df)
        
        # Generate predictions
        forecast = self.model.predict(future_df)
        
        # Rename columns for consistency
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        result.columns = ['timestamp', 'predicted_kwh', 'lower_bound', 'upper_bound']
        
        # Ensure non-negative predictions
        result['predicted_kwh'] = result['predicted_kwh'].clip(lower=0)
        result['lower_bound'] = result['lower_bound'].clip(lower=0)
        
        # Add confidence score based on interval width
        interval_width = result['upper_bound'] - result['lower_bound']
        mean_pred = result['predicted_kwh']
        result['confidence_score'] = 1 - (interval_width / (mean_pred + 1e-6)).clip(0, 1)
        
        return result
    
    def predict_horizon(
        self,
        start_timestamp: datetime,
        horizon_hours: int = 24,
        temperatura_exterior_c: float = 14.0,
        ocupacion_pct: float = 70.0
    ) -> List[Dict[str, Any]]:
        """
        Predict for a specific horizon.
        
        Args:
            start_timestamp: Starting timestamp
            horizon_hours: Hours to predict ahead
            temperatura_exterior_c: Temperature for predictions
            ocupacion_pct: Occupancy for predictions
            
        Returns:
            List of prediction dictionaries
        """
        # Create future timestamps
        future_dates = pd.date_range(
            start=start_timestamp,
            periods=horizon_hours,
            freq='H'
        )
        
        future_df = pd.DataFrame({
            'ds': future_dates,
            'temperatura_exterior_c': temperatura_exterior_c,
            'ocupacion_pct': ocupacion_pct,
            'es_festivo': 0,
            'es_semana_parciales': 0,
            'es_semana_finales': 0
        })
        
        # Adjust occupancy by time of day
        future_df['ocupacion_pct'] = future_df['ds'].apply(
            lambda x: ocupacion_pct if x.weekday() < 5 and 7 <= x.hour <= 18 else ocupacion_pct * 0.2
        )
        
        predictions = self.predict(future_df)
        
        return [
            {
                'timestamp': row['timestamp'],
                'predicted_kwh': row['predicted_kwh'],
                'lower_bound': row['lower_bound'],
                'upper_bound': row['upper_bound'],
                'confidence_score': row['confidence_score'],
                'sede': self.sede
            }
            for _, row in predictions.iterrows()
        ]
    
    def get_components(self) -> pd.DataFrame:
        """
        Get model components (trend, seasonalities).
        
        Returns:
            DataFrame with component decomposition
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
        
        # Make future dataframe covering training period
        future = self.model.make_future_dataframe(periods=0, include_history=True)
        
        for reg in self.regressors:
            if reg not in future.columns:
                future[reg] = 0
        
        forecast = self.model.predict(future)
        
        # Extract components
        components = ['ds', 'trend', 'weekly', 'yearly', 'daily']
        available = [c for c in components if c in forecast.columns]
        
        return forecast[available]
    
    def save(self, filename: Optional[str] = None) -> Path:
        """
        Save the model to disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved model
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model.")
        
        filename = filename or f"prophet_{self.sede.lower()}.joblib"
        filepath = self.model_dir / filename
        
        joblib.dump({
            'model': self.model,
            'sede': self.sede,
            'config': self.prophet_config,
            'regressors': self.regressors
        }, filepath)
        
        logger.info(f"Model saved to {filepath}")
        return filepath
    
    def load(self, filename: Optional[str] = None) -> 'ProphetPredictor':
        """
        Load model from disk.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            self for chaining
        """
        filename = filename or f"prophet_{self.sede.lower()}.joblib"
        filepath = self.model_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        data = joblib.load(filepath)
        
        self.model = data['model']
        self.sede = data['sede']
        self.prophet_config = data['config']
        self.regressors = data['regressors']
        self.is_fitted = True
        
        logger.info(f"Model loaded from {filepath}")
        return self
    
    def cross_validate(
        self,
        df: pd.DataFrame,
        initial: str = '365 days',
        period: str = '30 days',
        horizon: str = '7 days'
    ) -> pd.DataFrame:
        """
        Perform time series cross-validation.
        
        Args:
            df: Full DataFrame
            initial: Initial training period
            period: Period between cutoff dates
            horizon: Forecast horizon
            
        Returns:
            DataFrame with cross-validation results
        """
        from prophet.diagnostics import cross_validation, performance_metrics
        
        if not self.is_fitted:
            self.fit(df)
        
        cv_results = cross_validation(
            self.model,
            initial=initial,
            period=period,
            horizon=horizon
        )
        
        metrics = performance_metrics(cv_results)
        
        return metrics
