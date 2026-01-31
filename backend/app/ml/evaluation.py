"""
Model evaluation utilities for energy consumption prediction.

Provides:
- Standard regression metrics (MAE, RMSE, MAPE, R2)
- Time series specific metrics
- Visualization helpers
- Cross-validation utilities
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# Target metrics by sede (these are goals to achieve)
TARGET_METRICS = {
    'Tunja': {'MAE': 0.15, 'RMSE': 0.25, 'MAPE': 8.0, 'R2': 0.85},
    'Duitama': {'MAE': 0.20, 'RMSE': 0.30, 'MAPE': 10.0, 'R2': 0.82},
    'Sogamoso': {'MAE': 0.18, 'RMSE': 0.28, 'MAPE': 9.0, 'R2': 0.83},
    'Chiquinquira': {'MAE': 0.12, 'RMSE': 0.20, 'MAPE': 7.0, 'R2': 0.87},
}


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAE value
    """
    return np.mean(np.abs(y_true - y_pred))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        RMSE value
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def mean_absolute_percentage_error(
    y_true: np.ndarray, 
    y_pred: np.ndarray,
    epsilon: float = 1e-10
) -> float:
    """
    Calculate Mean Absolute Percentage Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        epsilon: Small value to avoid division by zero
        
    Returns:
        MAPE value (percentage)
    """
    return np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100


def symmetric_mean_absolute_percentage_error(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> float:
    """
    Calculate Symmetric MAPE (more robust than MAPE).
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        SMAPE value (percentage)
    """
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    return np.mean(np.abs(y_true - y_pred) / (denominator + 1e-10)) * 100


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R-squared (coefficient of determination).
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        R2 value
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    
    if ss_tot == 0:
        return 0.0
    
    return 1 - (ss_res / ss_tot)


def mean_bias_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Bias Error (indicates systematic over/under prediction).
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MBE value (positive = over-prediction)
    """
    return np.mean(y_pred - y_true)


def calculate_all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Calculate all regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary with all metrics
    """
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    # Remove any NaN values
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    
    if len(y_true) == 0:
        return {
            'MAE': np.nan, 'RMSE': np.nan, 'MAPE': np.nan,
            'SMAPE': np.nan, 'R2': np.nan, 'MBE': np.nan,
            'n_samples': 0
        }
    
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': root_mean_squared_error(y_true, y_pred),
        'MAPE': mean_absolute_percentage_error(y_true, y_pred),
        'SMAPE': symmetric_mean_absolute_percentage_error(y_true, y_pred),
        'R2': r2_score(y_true, y_pred),
        'MBE': mean_bias_error(y_true, y_pred),
        'n_samples': len(y_true)
    }


def evaluate_by_period(
    df: pd.DataFrame,
    y_true_col: str = 'energia_total_kwh',
    y_pred_col: str = 'predicted_kwh'
) -> Dict[str, Dict[str, float]]:
    """
    Calculate metrics by different time periods.
    
    Args:
        df: DataFrame with timestamp, true values, and predictions
        y_true_col: Column name for true values
        y_pred_col: Column name for predictions
        
    Returns:
        Dictionary with metrics by period
    """
    results = {}
    
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    # Overall metrics
    results['overall'] = calculate_all_metrics(
        df[y_true_col].values,
        df[y_pred_col].values
    )
    
    # By time of day
    for period_name, hour_range in [
        ('night', (22, 6)),
        ('morning', (6, 12)),
        ('afternoon', (12, 18)),
        ('evening', (18, 22))
    ]:
        if hour_range[0] > hour_range[1]:  # Spans midnight
            mask = (df['hour'] >= hour_range[0]) | (df['hour'] < hour_range[1])
        else:
            mask = (df['hour'] >= hour_range[0]) & (df['hour'] < hour_range[1])
        
        period_df = df[mask]
        if len(period_df) > 0:
            results[f'period_{period_name}'] = calculate_all_metrics(
                period_df[y_true_col].values,
                period_df[y_pred_col].values
            )
    
    # Weekday vs Weekend
    results['weekday'] = calculate_all_metrics(
        df[df['dayofweek'] < 5][y_true_col].values,
        df[df['dayofweek'] < 5][y_pred_col].values
    )
    results['weekend'] = calculate_all_metrics(
        df[df['dayofweek'] >= 5][y_true_col].values,
        df[df['dayofweek'] >= 5][y_pred_col].values
    )
    
    return results


def evaluate_by_sede(
    df: pd.DataFrame,
    y_true_col: str = 'energia_total_kwh',
    y_pred_col: str = 'predicted_kwh'
) -> Dict[str, Dict[str, float]]:
    """
    Calculate metrics by sede.
    
    Args:
        df: DataFrame with sede, true values, and predictions
        y_true_col: Column name for true values
        y_pred_col: Column name for predictions
        
    Returns:
        Dictionary with metrics by sede
    """
    results = {}
    
    for sede in df['sede'].unique():
        sede_df = df[df['sede'] == sede]
        metrics = calculate_all_metrics(
            sede_df[y_true_col].values,
            sede_df[y_pred_col].values
        )
        
        # Add comparison with targets
        if sede in TARGET_METRICS:
            targets = TARGET_METRICS[sede]
            metrics['target_MAE'] = targets['MAE']
            metrics['target_RMSE'] = targets['RMSE']
            metrics['target_MAPE'] = targets['MAPE']
            metrics['meets_MAE_target'] = metrics['MAE'] <= targets['MAE']
            metrics['meets_RMSE_target'] = metrics['RMSE'] <= targets['RMSE']
            metrics['meets_MAPE_target'] = metrics['MAPE'] <= targets['MAPE']
        
        results[sede] = metrics
    
    return results


def forecast_accuracy(
    df: pd.DataFrame,
    y_true_col: str = 'energia_total_kwh',
    y_pred_col: str = 'predicted_kwh',
    threshold_pct: float = 10.0
) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics.
    
    Args:
        df: DataFrame with true values and predictions
        y_true_col: Column name for true values
        y_pred_col: Column name for predictions
        threshold_pct: Percentage threshold for "accurate" prediction
        
    Returns:
        Dictionary with accuracy metrics
    """
    y_true = df[y_true_col].values
    y_pred = df[y_pred_col].values
    
    # Percentage error for each prediction
    pct_error = np.abs(y_true - y_pred) / (y_true + 1e-10) * 100
    
    return {
        'accuracy_10pct': np.mean(pct_error <= 10) * 100,
        'accuracy_20pct': np.mean(pct_error <= 20) * 100,
        'accuracy_custom': np.mean(pct_error <= threshold_pct) * 100,
        'median_pct_error': np.median(pct_error),
        'p95_pct_error': np.percentile(pct_error, 95)
    }


def prediction_intervals_coverage(
    y_true: np.ndarray,
    lower_bound: np.ndarray,
    upper_bound: np.ndarray,
    confidence_level: float = 0.95
) -> Dict[str, float]:
    """
    Evaluate prediction interval coverage.
    
    Args:
        y_true: True values
        lower_bound: Lower bound of prediction interval
        upper_bound: Upper bound of prediction interval
        confidence_level: Expected coverage level
        
    Returns:
        Dictionary with coverage metrics
    """
    within_interval = (y_true >= lower_bound) & (y_true <= upper_bound)
    actual_coverage = np.mean(within_interval)
    
    # Interval width
    interval_width = upper_bound - lower_bound
    mean_width = np.mean(interval_width)
    
    # Relative interval width (normalized by true values)
    relative_width = interval_width / (y_true + 1e-10)
    mean_relative_width = np.mean(relative_width)
    
    return {
        'actual_coverage': actual_coverage,
        'expected_coverage': confidence_level,
        'coverage_gap': actual_coverage - confidence_level,
        'mean_interval_width': mean_width,
        'mean_relative_width': mean_relative_width,
        'is_well_calibrated': abs(actual_coverage - confidence_level) < 0.05
    }


def generate_evaluation_report(
    df: pd.DataFrame,
    y_true_col: str = 'energia_total_kwh',
    y_pred_col: str = 'predicted_kwh',
    lower_col: Optional[str] = 'lower_bound',
    upper_col: Optional[str] = 'upper_bound'
) -> Dict[str, Any]:
    """
    Generate comprehensive evaluation report.
    
    Args:
        df: DataFrame with predictions
        y_true_col: Column for true values
        y_pred_col: Column for predictions
        lower_col: Column for lower bound (optional)
        upper_col: Column for upper bound (optional)
        
    Returns:
        Comprehensive evaluation report
    """
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'n_samples': len(df)
    }
    
    # Overall metrics
    report['overall_metrics'] = calculate_all_metrics(
        df[y_true_col].values,
        df[y_pred_col].values
    )
    
    # By sede
    if 'sede' in df.columns:
        report['by_sede'] = evaluate_by_sede(df, y_true_col, y_pred_col)
    
    # By period
    if 'timestamp' in df.columns:
        report['by_period'] = evaluate_by_period(df, y_true_col, y_pred_col)
    
    # Forecast accuracy
    report['forecast_accuracy'] = forecast_accuracy(df, y_true_col, y_pred_col)
    
    # Prediction intervals
    if lower_col in df.columns and upper_col in df.columns:
        report['prediction_intervals'] = prediction_intervals_coverage(
            df[y_true_col].values,
            df[lower_col].values,
            df[upper_col].values
        )
    
    # Error distribution
    errors = df[y_pred_col].values - df[y_true_col].values
    report['error_distribution'] = {
        'mean': float(np.mean(errors)),
        'std': float(np.std(errors)),
        'min': float(np.min(errors)),
        'max': float(np.max(errors)),
        'p5': float(np.percentile(errors, 5)),
        'p25': float(np.percentile(errors, 25)),
        'p50': float(np.percentile(errors, 50)),
        'p75': float(np.percentile(errors, 75)),
        'p95': float(np.percentile(errors, 95))
    }
    
    return report


def compare_models(
    df: pd.DataFrame,
    y_true_col: str,
    model_predictions: Dict[str, str]
) -> pd.DataFrame:
    """
    Compare multiple models.
    
    Args:
        df: DataFrame with predictions from multiple models
        y_true_col: Column with true values
        model_predictions: Dict mapping model name to prediction column
        
    Returns:
        DataFrame comparing models
    """
    results = []
    
    for model_name, pred_col in model_predictions.items():
        if pred_col in df.columns:
            metrics = calculate_all_metrics(
                df[y_true_col].values,
                df[pred_col].values
            )
            metrics['model'] = model_name
            results.append(metrics)
    
    comparison_df = pd.DataFrame(results)
    
    # Rank models by each metric
    for metric in ['MAE', 'RMSE', 'MAPE']:
        if metric in comparison_df.columns:
            comparison_df[f'{metric}_rank'] = comparison_df[metric].rank()
    
    if 'R2' in comparison_df.columns:
        comparison_df['R2_rank'] = comparison_df['R2'].rank(ascending=False)
    
    return comparison_df
