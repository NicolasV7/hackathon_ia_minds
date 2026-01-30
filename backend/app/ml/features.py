"""
Feature engineering utilities for ML models.
Adapted from src/data_processing.py
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime


# Constants
SEDES = ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquira']
SECTORES = ['comedor', 'salones', 'laboratorios', 'auditorios', 'oficinas']

SECTOR_COL_MAP = {
    'comedor': 'energia_comedor_kwh',
    'salones': 'energia_salones_kwh',
    'laboratorios': 'energia_laboratorios_kwh',
    'auditorios': 'energia_auditorios_kwh',
    'oficinas': 'energia_oficinas_kwh'
}


def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add cyclical encoding for temporal features.
    
    Args:
        df: DataFrame with hora, dia_semana, mes columns
        
    Returns:
        DataFrame with cyclical features added
    """
    df = df.copy()
    
    # Hour cyclical encoding (0-23)
    df['hora_sin'] = np.sin(2 * np.pi * df['hora'] / 24)
    df['hora_cos'] = np.cos(2 * np.pi * df['hora'] / 24)
    
    # Day of week cyclical encoding (0-6)
    df['dia_semana_sin'] = np.sin(2 * np.pi * df['dia_semana'] / 7)
    df['dia_semana_cos'] = np.cos(2 * np.pi * df['dia_semana'] / 7)
    
    # Month cyclical encoding (1-12)
    df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
    df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
    
    # Day of year (approximate seasonality)
    df['dia_del_ano'] = df['timestamp'].dt.dayofyear
    df['dia_ano_sin'] = np.sin(2 * np.pi * df['dia_del_ano'] / 365)
    df['dia_ano_cos'] = np.cos(2 * np.pi * df['dia_del_ano'] / 365)
    
    return df


def add_lag_features(
    df: pd.DataFrame, 
    target_col: str = 'energia_total_kwh',
    lags: List[int] = [1, 24, 168]  # 1 hour, 1 day, 1 week
) -> pd.DataFrame:
    """
    Add lag features for time series prediction.
    
    Args:
        df: DataFrame sorted by sede and timestamp
        target_col: Column to create lags for
        lags: List of lag periods (in hours)
        
    Returns:
        DataFrame with lag features
    """
    df = df.copy()
    df = df.sort_values(['sede', 'timestamp']).reset_index(drop=True)
    
    for lag in lags:
        lag_col_name = f'{target_col}_lag_{lag}h'
        df[lag_col_name] = df.groupby('sede')[target_col].shift(lag)
    
    return df


def add_rolling_features(
    df: pd.DataFrame,
    target_col: str = 'energia_total_kwh',
    windows: List[int] = [24, 168]  # 24 hours, 1 week
) -> pd.DataFrame:
    """
    Add rolling statistics features.
    
    Args:
        df: DataFrame sorted by sede and timestamp
        target_col: Column to calculate rolling stats for
        windows: List of window sizes (in hours)
        
    Returns:
        DataFrame with rolling features
    """
    df = df.copy()
    df = df.sort_values(['sede', 'timestamp']).reset_index(drop=True)
    
    for window in windows:
        # Rolling mean
        mean_col = f'{target_col}_rolling_mean_{window}h'
        df[mean_col] = df.groupby('sede')[target_col].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        
        # Rolling std
        std_col = f'{target_col}_rolling_std_{window}h'
        df[std_col] = df.groupby('sede')[target_col].transform(
            lambda x: x.rolling(window=window, min_periods=1).std()
        )
        
        # Rolling max
        max_col = f'{target_col}_rolling_max_{window}h'
        df[max_col] = df.groupby('sede')[target_col].transform(
            lambda x: x.rolling(window=window, min_periods=1).max()
        )
    
    return df


def fix_periodo_academico(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix inconsistencies in periodo_academico based on dates.
    
    Args:
        df: DataFrame with timestamp and mes column
        
    Returns:
        DataFrame with corrected periodo_academico
    """
    df = df.copy()
    
    # Define academic calendar rules (approximate for Colombia)
    def get_periodo(row):
        month = row['mes']
        
        # Vacation periods
        if month in [1] or (month == 12 and row['timestamp'].day > 15):
            return 'vacaciones_fin'
        elif month in [6, 7]:
            return 'vacaciones_mitad'
        
        # Regular semesters
        elif month in [2, 3, 4, 5]:
            return 'semestre_1'
        elif month in [8, 9, 10, 11] or (month == 12 and row['timestamp'].day <= 15):
            return 'semestre_2'
        else:
            return 'transicion'
    
    df['periodo_academico_fixed'] = df.apply(get_periodo, axis=1)
    
    return df


def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical variables for ML models.
    
    Args:
        df: DataFrame with categorical columns
        
    Returns:
        DataFrame with encoded columns
    """
    df = df.copy()
    
    # One-hot encode sede
    sede_dummies = pd.get_dummies(df['sede'], prefix='sede')
    df = pd.concat([df, sede_dummies], axis=1)
    
    # Encode periodo_academico
    if 'periodo_academico_fixed' in df.columns:
        periodo_dummies = pd.get_dummies(
            df['periodo_academico_fixed'], 
            prefix='periodo'
        )
        df = pd.concat([df, periodo_dummies], axis=1)
    
    return df


def prepare_prediction_features(
    timestamp: datetime,
    sede: str,
    temperatura_exterior_c: float,
    ocupacion_pct: float,
    es_festivo: bool,
    es_semana_parciales: bool,
    es_semana_finales: bool,
    lag_features: Optional[Dict[str, float]] = None,
    rolling_features: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Prepare features for a single prediction request.
    
    Args:
        timestamp: Timestamp for prediction
        sede: Sede name
        temperatura_exterior_c: Exterior temperature
        ocupacion_pct: Occupancy percentage
        es_festivo: Is holiday
        es_semana_parciales: Is midterm week
        es_semana_finales: Is finals week
        lag_features: Dictionary with lag feature values
        rolling_features: Dictionary with rolling feature values
        
    Returns:
        DataFrame with single row ready for prediction
    """
    # Extract temporal features
    hora = timestamp.hour
    dia_semana = timestamp.weekday()
    mes = timestamp.month
    dia_del_ano = timestamp.timetuple().tm_yday
    es_fin_semana = dia_semana >= 5
    
    # Create base row
    row = {
        'timestamp': timestamp,
        'sede': sede,
        'hora': hora,
        'dia_semana': dia_semana,
        'mes': mes,
        'dia_del_ano': dia_del_ano,
        'es_fin_semana': es_fin_semana,
        'temperatura_exterior_c': temperatura_exterior_c,
        'ocupacion_pct': ocupacion_pct,
        'es_festivo': es_festivo,
        'es_semana_parciales': es_semana_parciales,
        'es_semana_finales': es_semana_finales,
    }
    
    df = pd.DataFrame([row])
    
    # Add cyclical features
    df = add_cyclical_features(df)
    
    # Add periodo academico
    df = fix_periodo_academico(df)
    
    # Encode categorical
    df = encode_categorical(df)
    
    # Add derived features
    df['temp_x_ocupacion'] = df['temperatura_exterior_c'] * df['ocupacion_pct']
    df['es_horario_laboral'] = ((df['hora'] >= 7) & (df['hora'] <= 18) & (~df['es_fin_semana'])).astype(int)
    df['es_horario_pico'] = ((df['hora'] >= 10) & (df['hora'] <= 14)).astype(int)
    
    # Add lag features if provided
    if lag_features:
        for key, value in lag_features.items():
            df[key] = value
    else:
        # Set default lag features to 0 or median values
        df['energia_total_kwh_lag_1h'] = 0
        df['energia_total_kwh_lag_24h'] = 0
        df['energia_total_kwh_lag_168h'] = 0
    
    # Add rolling features if provided
    if rolling_features:
        for key, value in rolling_features.items():
            df[key] = value
    else:
        # Set default rolling features
        df['energia_total_kwh_rolling_mean_24h'] = 0
        df['energia_total_kwh_rolling_std_24h'] = 0
        df['energia_total_kwh_rolling_max_24h'] = 0
        df['energia_total_kwh_rolling_mean_168h'] = 0
        df['energia_total_kwh_rolling_std_168h'] = 0
        df['energia_total_kwh_rolling_max_168h'] = 0
    
    return df


def get_feature_columns() -> List[str]:
    """
    Get list of feature columns expected by the trained model.
    
    Returns:
        List of feature column names
    """
    return [
        # Cyclical temporal features
        'hora_sin', 'hora_cos',
        'dia_semana_sin', 'dia_semana_cos',
        'mes_sin', 'mes_cos',
        'dia_ano_sin', 'dia_ano_cos',
        
        # Context features
        'temperatura_exterior_c', 'ocupacion_pct',
        
        # Binary features
        'es_fin_semana', 'es_festivo', 
        'es_semana_parciales', 'es_semana_finales',
        'es_horario_laboral', 'es_horario_pico',
        
        # Interaction features
        'temp_x_ocupacion',
        
        # Sede dummies
        'sede_Tunja', 'sede_Duitama', 'sede_Sogamoso', 'sede_Chiquinquira',
        
        # Periodo dummies
        'periodo_semestre_1', 'periodo_semestre_2',
        'periodo_vacaciones_fin', 'periodo_vacaciones_mitad',
        
        # Lag features
        'energia_total_kwh_lag_1h',
        'energia_total_kwh_lag_24h',
        'energia_total_kwh_lag_168h',
        
        # Rolling features
        'energia_total_kwh_rolling_mean_24h',
        'energia_total_kwh_rolling_std_24h',
        'energia_total_kwh_rolling_max_24h',
        'energia_total_kwh_rolling_mean_168h',
        'energia_total_kwh_rolling_std_168h',
        'energia_total_kwh_rolling_max_168h'
    ]
