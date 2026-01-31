"""
STL (Seasonal-Trend decomposition using LOESS) based anomaly detector.

STL decomposes time series into:
- Trend component
- Seasonal component(s)
- Residual component

Anomalies are detected in the residual component.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.seasonal import STL
    STL_AVAILABLE = True
except ImportError:
    STL_AVAILABLE = False
    STL = None

logger = logging.getLogger(__name__)


class STLAnomalyDetector:
    """
    Anomaly detector using STL decomposition.
    
    Detects anomalies by analyzing residuals after removing
    trend and seasonal components.
    """
    
    def __init__(
        self,
        seasonal_period: int = 24,  # Hourly data, daily seasonality
        robust: bool = True,
        seasonal_deg: int = 1,
        trend_deg: int = 1,
        low_pass_deg: int = 1,
        residual_threshold: float = 3.0  # Standard deviations
    ):
        """
        Initialize STL detector.
        
        Args:
            seasonal_period: Period of seasonal component (24 for hourly data)
            robust: Use robust fitting (less sensitive to outliers)
            seasonal_deg: Degree of seasonal smoothing
            trend_deg: Degree of trend smoothing
            low_pass_deg: Degree of low-pass filter
            residual_threshold: Number of std devs for anomaly threshold
        """
        if not STL_AVAILABLE:
            raise ImportError(
                "statsmodels not installed. Install with: pip install statsmodels"
            )
        
        self.seasonal_period = seasonal_period
        self.robust = robust
        self.seasonal_deg = seasonal_deg
        self.trend_deg = trend_deg
        self.low_pass_deg = low_pass_deg
        self.residual_threshold = residual_threshold
        
        self.decomposition_cache: Dict[str, Any] = {}
    
    def decompose(
        self,
        series: pd.Series,
        sede: Optional[str] = None
    ) -> Dict[str, pd.Series]:
        """
        Decompose time series into components.
        
        Args:
            series: Time series to decompose
            sede: Optional sede identifier for caching
            
        Returns:
            Dictionary with trend, seasonal, and residual components
        """
        # Need at least 2 full periods
        if len(series) < self.seasonal_period * 2:
            logger.warning(f"Series too short for STL: {len(series)} < {self.seasonal_period * 2}")
            return {
                'trend': series,
                'seasonal': pd.Series(0, index=series.index),
                'residual': pd.Series(0, index=series.index)
            }
        
        # Handle missing values
        series_clean = series.interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
        
        try:
            stl = STL(
                series_clean,
                period=self.seasonal_period,
                robust=self.robust,
                seasonal_deg=self.seasonal_deg,
                trend_deg=self.trend_deg,
                low_pass_deg=self.low_pass_deg
            )
            result = stl.fit()
            
            components = {
                'trend': result.trend,
                'seasonal': result.seasonal,
                'residual': result.resid,
                'weights': result.weights if hasattr(result, 'weights') else None
            }
            
            if sede:
                self.decomposition_cache[sede] = components
            
            return components
            
        except Exception as e:
            logger.error(f"STL decomposition failed: {e}")
            return {
                'trend': series,
                'seasonal': pd.Series(0, index=series.index),
                'residual': pd.Series(0, index=series.index)
            }
    
    def detect_anomalies(
        self,
        df: pd.DataFrame,
        target_col: str = 'energia_total_kwh',
        severity_threshold: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using STL decomposition.
        
        Args:
            df: DataFrame with timestamp, sede, and target column
            target_col: Column to analyze
            severity_threshold: Minimum severity to report
            
        Returns:
            List of anomaly dictionaries
        """
        anomalies = []
        severity_order = ['low', 'medium', 'high', 'critical']
        min_severity_idx = severity_order.index(severity_threshold) if severity_threshold else 0
        
        for sede in df['sede'].unique():
            sede_df = df[df['sede'] == sede].sort_values('timestamp').copy()
            
            if len(sede_df) < self.seasonal_period * 2:
                logger.warning(f"Not enough data for {sede}")
                continue
            
            # Create time series
            series = sede_df.set_index('timestamp')[target_col]
            
            # Decompose
            components = self.decompose(series, sede)
            residuals = components['residual']
            
            # Calculate residual statistics
            residual_mean = residuals.mean()
            residual_std = residuals.std()
            
            if residual_std == 0:
                continue
            
            # Z-scores of residuals
            z_scores = (residuals - residual_mean) / residual_std
            
            # Find anomalies
            for idx, z in z_scores.items():
                abs_z = abs(z)
                
                if abs_z >= self.residual_threshold:
                    # Determine severity
                    if abs_z >= 5.0:
                        severity = 'critical'
                    elif abs_z >= 4.0:
                        severity = 'high'
                    elif abs_z >= 3.5:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    # Filter by severity threshold
                    if severity_order.index(severity) < min_severity_idx:
                        continue
                    
                    # Get actual and expected values
                    actual = series.loc[idx]
                    expected = components['trend'].loc[idx] + components['seasonal'].loc[idx]
                    deviation_pct = ((actual - expected) / expected) * 100 if expected != 0 else 0
                    
                    # Determine anomaly type based on direction
                    if z > 0:
                        anomaly_type = 'consumption_spike'
                        description = (
                            f"Consumo anormalmente alto de {actual:.2f} kWh "
                            f"(esperado: {expected:.2f} kWh basado en tendencia y estacionalidad)"
                        )
                        recommendation = (
                            "Investigar causa del incremento. "
                            "Verificar si hubo evento especial o falla de equipo."
                        )
                    else:
                        anomaly_type = 'consumption_drop'
                        description = (
                            f"Consumo anormalmente bajo de {actual:.2f} kWh "
                            f"(esperado: {expected:.2f} kWh)"
                        )
                        recommendation = (
                            "Verificar si hubo cierre no programado o falla en medición."
                        )
                    
                    anomalies.append({
                        'timestamp': idx,
                        'sede': sede,
                        'sector': 'total',
                        'anomaly_type': anomaly_type,
                        'severity': severity,
                        'actual_value': float(actual),
                        'expected_value': float(expected),
                        'deviation_pct': float(deviation_pct),
                        'description': description,
                        'recommendation': recommendation,
                        'potential_savings_kwh': float(max(0, actual - expected)),
                        'z_score': float(z),
                        'detection_method': 'stl_decomposition',
                        'trend_value': float(components['trend'].loc[idx]),
                        'seasonal_value': float(components['seasonal'].loc[idx]),
                        'residual_value': float(residuals.loc[idx])
                    })
        
        logger.info(f"STL detector found {len(anomalies)} anomalies")
        return anomalies
    
    def detect_trend_changes(
        self,
        df: pd.DataFrame,
        target_col: str = 'energia_total_kwh',
        window: int = 168  # 1 week
    ) -> List[Dict[str, Any]]:
        """
        Detect significant changes in trend.
        
        Args:
            df: DataFrame with time series data
            target_col: Column to analyze
            window: Window for trend change detection
            
        Returns:
            List of trend change events
        """
        changes = []
        
        for sede in df['sede'].unique():
            sede_df = df[df['sede'] == sede].sort_values('timestamp').copy()
            
            if len(sede_df) < window * 2:
                continue
            
            series = sede_df.set_index('timestamp')[target_col]
            components = self.decompose(series, sede)
            trend = components['trend']
            
            # Calculate trend slope changes
            trend_diff = trend.diff()
            trend_diff_diff = trend_diff.diff()  # Acceleration
            
            # Find significant acceleration changes
            accel_std = trend_diff_diff.std()
            
            if accel_std == 0:
                continue
            
            accel_z = trend_diff_diff / accel_std
            
            for idx, z in accel_z.items():
                if abs(z) >= 3.0:
                    direction = 'increasing' if z > 0 else 'decreasing'
                    
                    changes.append({
                        'timestamp': idx,
                        'sede': sede,
                        'change_type': 'trend_acceleration',
                        'direction': direction,
                        'z_score': float(z),
                        'description': f"Cambio significativo en tendencia de consumo ({direction})",
                        'recommendation': "Investigar cambios recientes en operación o infraestructura."
                    })
        
        return changes
    
    def get_seasonal_pattern(
        self,
        df: pd.DataFrame,
        sede: str,
        target_col: str = 'energia_total_kwh'
    ) -> Dict[str, Any]:
        """
        Extract typical seasonal pattern for a sede.
        
        Args:
            df: DataFrame with historical data
            sede: Sede to analyze
            target_col: Column to analyze
            
        Returns:
            Dictionary with seasonal pattern information
        """
        sede_df = df[df['sede'] == sede].sort_values('timestamp')
        
        if len(sede_df) < self.seasonal_period * 2:
            return {}
        
        series = sede_df.set_index('timestamp')[target_col]
        components = self.decompose(series, sede)
        
        # Extract hourly pattern (average over all days)
        seasonal = components['seasonal']
        hourly_pattern = seasonal.groupby(seasonal.index.hour).mean()
        
        # Find peak and trough hours
        peak_hour = hourly_pattern.idxmax()
        trough_hour = hourly_pattern.idxmin()
        
        return {
            'sede': sede,
            'hourly_pattern': hourly_pattern.to_dict(),
            'peak_hour': int(peak_hour),
            'peak_value': float(hourly_pattern[peak_hour]),
            'trough_hour': int(trough_hour),
            'trough_value': float(hourly_pattern[trough_hour]),
            'amplitude': float(hourly_pattern[peak_hour] - hourly_pattern[trough_hour]),
            'mean_trend': float(components['trend'].mean())
        }
