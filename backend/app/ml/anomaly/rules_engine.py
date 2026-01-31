"""
Rules-based anomaly detection engine.

Implements dynamic statistical rules for detecting:
- Off-hours consumption
- Weekend anomalies
- Consumption spikes
- Low occupancy with high consumption
- Sector-specific inefficiencies
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================================
# ANOMALY RULE DEFINITIONS
# ============================================================================

ANOMALY_RULES = {
    "off_hours_usage": {
        "name": "Consumo Fuera de Horario",
        "description": "Consumo elevado durante horas no laborales (22:00 - 06:00)",
        "hours": list(range(22, 24)) + list(range(0, 6)),
        "threshold_multiplier": 0.35,  # Max 35% del promedio diurno
        "applies_to": ["salones", "oficinas", "auditorios", "comedor"],
        "excludes": [],  # Labs excluidos porque pueden tener equipos 24/7
        "severity_thresholds": {
            "low": 0.35,
            "medium": 0.50,
            "high": 0.75,
            "critical": 1.0
        }
    },
    
    "weekend_anomaly": {
        "name": "Consumo Elevado en Fin de Semana",
        "description": "Consumo inusualmente alto durante sábado o domingo",
        "days": [5, 6],  # Sábado, Domingo
        "threshold_multiplier": 0.40,  # Max 40% del promedio semanal
        "sector_specific": {
            "comedor": 0.25,      # Comedores casi sin uso
            "salones": 0.30,      # Muy poco uso
            "auditorios": 0.20,   # Casi nulo
            "oficinas": 0.35,     # Algo de trabajo
            "laboratorios": 0.60  # Experimentos largos
        },
        "severity_thresholds": {
            "low": 0.40,
            "medium": 0.60,
            "high": 0.80,
            "critical": 1.0
        }
    },
    
    "consumption_spike": {
        "name": "Pico de Consumo",
        "description": "Incremento súbito anormal en el consumo",
        "z_score_threshold": 3.0,
        "min_deviation_pct": 50,  # Al menos 50% sobre el promedio
        "window_hours": 24,
        "severity_thresholds": {
            "low": 3.0,
            "medium": 4.0,
            "high": 5.0,
            "critical": 6.0
        }
    },
    
    "low_occupancy_high_consumption": {
        "name": "Desbalance Ocupación-Consumo",
        "description": "Alto consumo con baja ocupación reportada",
        "occupancy_threshold": 30,  # Menos del 30% ocupación
        "consumption_multiplier": 0.70,  # Consumiendo >70% del normal
        "severity_thresholds": {
            "low": 0.70,
            "medium": 0.85,
            "high": 1.0,
            "critical": 1.2
        }
    },
    
    "holiday_consumption": {
        "name": "Consumo en Día Festivo",
        "description": "Consumo elevado durante días festivos",
        "threshold_multiplier": 0.30,
        "severity_thresholds": {
            "low": 0.30,
            "medium": 0.45,
            "high": 0.60,
            "critical": 0.80
        }
    },
    
    "academic_vacation_high": {
        "name": "Consumo Alto en Vacaciones",
        "description": "Consumo elevado durante periodo de vacaciones académicas",
        "threshold_multiplier": 0.40,
        "periods": ["vacaciones_fin", "vacaciones_mitad", "vacaciones"],
        "severity_thresholds": {
            "low": 0.40,
            "medium": 0.55,
            "high": 0.70,
            "critical": 0.85
        }
    },
    
    "sector_ratio_anomaly": {
        "name": "Ratio de Sector Anómalo",
        "description": "Un sector consume proporción anormal del total",
        "expected_ratios": {
            "Tunja": {"comedor": 0.12, "salones": 0.25, "laboratorios": 0.30, "auditorios": 0.08, "oficinas": 0.25},
            "Duitama": {"comedor": 0.10, "salones": 0.28, "laboratorios": 0.32, "auditorios": 0.07, "oficinas": 0.23},
            "Sogamoso": {"comedor": 0.10, "salones": 0.26, "laboratorios": 0.35, "auditorios": 0.06, "oficinas": 0.23},
            "Chiquinquira": {"comedor": 0.08, "salones": 0.35, "laboratorios": 0.20, "auditorios": 0.10, "oficinas": 0.27}
        },
        "deviation_threshold": 0.50,  # 50% desviación del ratio esperado
        "severity_thresholds": {
            "low": 0.50,
            "medium": 0.75,
            "high": 1.0,
            "critical": 1.5
        }
    }
}


@dataclass
class DetectedAnomaly:
    """Represents a detected anomaly."""
    timestamp: datetime
    sede: str
    sector: str
    anomaly_type: str
    severity: str
    actual_value: float
    expected_value: float
    deviation_pct: float
    description: str
    recommendation: str
    potential_savings_kwh: float
    z_score: Optional[float] = None
    context: Optional[Dict] = None


class RulesBasedDetector:
    """
    Rules-based anomaly detector using statistical thresholds.
    
    Features:
    - Dynamic thresholds based on historical data
    - Context-aware detection (time, occupancy, academic period)
    - Multi-level severity classification
    - Sector-specific rules
    """
    
    def __init__(self, rules: Optional[Dict] = None):
        """
        Initialize the rules engine.
        
        Args:
            rules: Custom rules dictionary (uses defaults if None)
        """
        self.rules = rules or ANOMALY_RULES
        self.historical_stats: Dict[str, Dict] = {}
    
    def compute_historical_stats(self, df: pd.DataFrame) -> None:
        """
        Compute historical statistics for dynamic thresholds.
        
        Args:
            df: Historical consumption DataFrame
        """
        logger.info("Computing historical statistics...")
        
        for sede in df['sede'].unique():
            sede_df = df[df['sede'] == sede]
            
            self.historical_stats[sede] = {
                # Overall stats
                'mean': sede_df['energia_total_kwh'].mean(),
                'std': sede_df['energia_total_kwh'].std(),
                'median': sede_df['energia_total_kwh'].median(),
                'p95': sede_df['energia_total_kwh'].quantile(0.95),
                'p99': sede_df['energia_total_kwh'].quantile(0.99),
                
                # By hour
                'hourly_mean': sede_df.groupby('hora')['energia_total_kwh'].mean().to_dict(),
                'hourly_std': sede_df.groupby('hora')['energia_total_kwh'].std().to_dict(),
                
                # By day of week
                'daily_mean': sede_df.groupby('dia_semana')['energia_total_kwh'].mean().to_dict(),
                
                # Working hours mean (7-18)
                'working_hours_mean': sede_df[
                    (sede_df['hora'] >= 7) & (sede_df['hora'] <= 18)
                ]['energia_total_kwh'].mean(),
                
                # Non-working hours mean
                'non_working_mean': sede_df[
                    (sede_df['hora'] < 7) | (sede_df['hora'] > 18)
                ]['energia_total_kwh'].mean(),
                
                # Weekend mean
                'weekend_mean': sede_df[
                    sede_df['dia_semana'].isin([5, 6])
                ]['energia_total_kwh'].mean(),
                
                # Weekday mean
                'weekday_mean': sede_df[
                    ~sede_df['dia_semana'].isin([5, 6])
                ]['energia_total_kwh'].mean(),
            }
            
            # Sector-specific stats
            for sector, col in [
                ('comedor', 'energia_comedor_kwh'),
                ('salones', 'energia_salones_kwh'),
                ('laboratorios', 'energia_laboratorios_kwh'),
                ('auditorios', 'energia_auditorios_kwh'),
                ('oficinas', 'energia_oficinas_kwh')
            ]:
                if col in sede_df.columns:
                    self.historical_stats[sede][f'{sector}_mean'] = sede_df[col].mean()
                    self.historical_stats[sede][f'{sector}_std'] = sede_df[col].std()
        
        logger.info(f"Computed stats for {len(self.historical_stats)} sedes")
    
    def _get_severity(
        self, 
        deviation_ratio: float, 
        thresholds: Dict[str, float]
    ) -> str:
        """Determine severity based on deviation ratio."""
        if deviation_ratio >= thresholds.get('critical', 1.0):
            return 'critical'
        elif deviation_ratio >= thresholds.get('high', 0.75):
            return 'high'
        elif deviation_ratio >= thresholds.get('medium', 0.5):
            return 'medium'
        else:
            return 'low'
    
    def _check_off_hours(
        self, 
        row: pd.Series, 
        stats: Dict
    ) -> Optional[DetectedAnomaly]:
        """Check for off-hours consumption anomaly."""
        rule = self.rules['off_hours_usage']
        
        hora = row['hora']
        if hora not in rule['hours']:
            return None
        
        # Get expected value for this hour
        expected = stats.get('non_working_mean', stats['mean'] * 0.3)
        threshold = stats['working_hours_mean'] * rule['threshold_multiplier']
        
        actual = row['energia_total_kwh']
        
        if actual > threshold:
            deviation_pct = ((actual - threshold) / threshold) * 100
            deviation_ratio = actual / stats['working_hours_mean']
            
            return DetectedAnomaly(
                timestamp=row['timestamp'],
                sede=row['sede'],
                sector='total',
                anomaly_type='off_hours_usage',
                severity=self._get_severity(deviation_ratio, rule['severity_thresholds']),
                actual_value=actual,
                expected_value=expected,
                deviation_pct=deviation_pct,
                description=f"Consumo de {actual:.2f} kWh a las {hora}:00, "
                           f"cuando el máximo esperado es {threshold:.2f} kWh",
                recommendation="Verificar equipos activos fuera de horario. "
                              "Considerar instalar temporizadores automáticos.",
                potential_savings_kwh=actual - expected
            )
        
        return None
    
    def _check_weekend(
        self, 
        row: pd.Series, 
        stats: Dict
    ) -> Optional[DetectedAnomaly]:
        """Check for weekend consumption anomaly."""
        rule = self.rules['weekend_anomaly']
        
        if row['dia_semana'] not in rule['days']:
            return None
        
        expected = stats.get('weekend_mean', stats['mean'] * 0.4)
        threshold = stats['weekday_mean'] * rule['threshold_multiplier']
        
        actual = row['energia_total_kwh']
        
        if actual > threshold:
            deviation_pct = ((actual - threshold) / threshold) * 100
            deviation_ratio = actual / stats['weekday_mean']
            
            dia_nombre = 'Sábado' if row['dia_semana'] == 5 else 'Domingo'
            
            return DetectedAnomaly(
                timestamp=row['timestamp'],
                sede=row['sede'],
                sector='total',
                anomaly_type='weekend_anomaly',
                severity=self._get_severity(deviation_ratio, rule['severity_thresholds']),
                actual_value=actual,
                expected_value=expected,
                deviation_pct=deviation_pct,
                description=f"Consumo de {actual:.2f} kWh el {dia_nombre}, "
                           f"cuando el máximo esperado es {threshold:.2f} kWh",
                recommendation="Verificar que equipos no esenciales estén apagados. "
                              "Establecer protocolo de cierre de fin de semana.",
                potential_savings_kwh=actual - expected
            )
        
        return None
    
    def _check_spike(
        self, 
        row: pd.Series, 
        stats: Dict,
        recent_values: Optional[List[float]] = None
    ) -> Optional[DetectedAnomaly]:
        """Check for consumption spike."""
        rule = self.rules['consumption_spike']
        
        mean = stats['mean']
        std = stats['std']
        
        if std == 0:
            return None
        
        actual = row['energia_total_kwh']
        z_score = (actual - mean) / std
        
        if z_score >= rule['z_score_threshold']:
            deviation_pct = ((actual - mean) / mean) * 100
            
            if deviation_pct >= rule['min_deviation_pct']:
                return DetectedAnomaly(
                    timestamp=row['timestamp'],
                    sede=row['sede'],
                    sector='total',
                    anomaly_type='consumption_spike',
                    severity=self._get_severity(z_score, rule['severity_thresholds']),
                    actual_value=actual,
                    expected_value=mean,
                    deviation_pct=deviation_pct,
                    description=f"Pico de consumo de {actual:.2f} kWh "
                               f"(Z-score: {z_score:.1f}, {deviation_pct:.0f}% sobre promedio)",
                    recommendation="Investigar causa del pico. Verificar encendido "
                                  "simultáneo de equipos de alta potencia.",
                    potential_savings_kwh=actual - mean,
                    z_score=z_score
                )
        
        return None
    
    def _check_low_occupancy(
        self, 
        row: pd.Series, 
        stats: Dict
    ) -> Optional[DetectedAnomaly]:
        """Check for low occupancy with high consumption."""
        rule = self.rules['low_occupancy_high_consumption']
        
        if 'ocupacion_pct' not in row or pd.isna(row['ocupacion_pct']):
            return None
        
        occupancy = row['ocupacion_pct']
        if occupancy >= rule['occupancy_threshold']:
            return None
        
        # Expected consumption based on occupancy
        expected = stats['mean'] * (occupancy / 100)
        threshold = stats['mean'] * rule['consumption_multiplier']
        
        actual = row['energia_total_kwh']
        
        if actual > threshold:
            deviation_pct = ((actual - expected) / expected) * 100 if expected > 0 else 100
            deviation_ratio = actual / stats['mean']
            
            return DetectedAnomaly(
                timestamp=row['timestamp'],
                sede=row['sede'],
                sector='total',
                anomaly_type='low_occupancy_high_consumption',
                severity=self._get_severity(deviation_ratio, rule['severity_thresholds']),
                actual_value=actual,
                expected_value=expected,
                deviation_pct=deviation_pct,
                description=f"Consumo de {actual:.2f} kWh con solo {occupancy:.0f}% de ocupación. "
                           f"Esperado: {expected:.2f} kWh",
                recommendation="Revisar sistemas HVAC y ajustar según ocupación real. "
                              "Considerar sensores de presencia.",
                potential_savings_kwh=actual - expected
            )
        
        return None
    
    def _check_holiday(
        self, 
        row: pd.Series, 
        stats: Dict
    ) -> Optional[DetectedAnomaly]:
        """Check for holiday consumption anomaly."""
        rule = self.rules['holiday_consumption']
        
        if not row.get('es_festivo', False):
            return None
        
        expected = stats['mean'] * rule['threshold_multiplier']
        actual = row['energia_total_kwh']
        
        if actual > expected:
            deviation_pct = ((actual - expected) / expected) * 100
            deviation_ratio = actual / stats['mean']
            
            return DetectedAnomaly(
                timestamp=row['timestamp'],
                sede=row['sede'],
                sector='total',
                anomaly_type='holiday_consumption',
                severity=self._get_severity(deviation_ratio, rule['severity_thresholds']),
                actual_value=actual,
                expected_value=expected,
                deviation_pct=deviation_pct,
                description=f"Consumo de {actual:.2f} kWh en día festivo. "
                           f"Máximo esperado: {expected:.2f} kWh",
                recommendation="Verificar equipos activos en festivo. "
                              "Asegurar protocolo de apagado para festivos.",
                potential_savings_kwh=actual - expected
            )
        
        return None
    
    def _check_vacation(
        self, 
        row: pd.Series, 
        stats: Dict
    ) -> Optional[DetectedAnomaly]:
        """Check for vacation period high consumption."""
        rule = self.rules['academic_vacation_high']
        
        periodo = row.get('periodo_academico', '')
        if periodo not in rule['periods']:
            return None
        
        expected = stats['mean'] * rule['threshold_multiplier']
        actual = row['energia_total_kwh']
        
        if actual > expected:
            deviation_pct = ((actual - expected) / expected) * 100
            deviation_ratio = actual / stats['mean']
            
            return DetectedAnomaly(
                timestamp=row['timestamp'],
                sede=row['sede'],
                sector='total',
                anomaly_type='academic_vacation_high',
                severity=self._get_severity(deviation_ratio, rule['severity_thresholds']),
                actual_value=actual,
                expected_value=expected,
                deviation_pct=deviation_pct,
                description=f"Consumo de {actual:.2f} kWh durante vacaciones. "
                           f"Máximo esperado: {expected:.2f} kWh",
                recommendation="Revisar equipos activos durante vacaciones. "
                              "Aprovechar periodo para mantenimiento preventivo.",
                potential_savings_kwh=actual - expected
            )
        
        return None
    
    def detect(
        self,
        df: pd.DataFrame,
        severity_threshold: Optional[str] = None
    ) -> List[DetectedAnomaly]:
        """
        Detect anomalies in consumption data.
        
        Args:
            df: DataFrame with consumption data
            severity_threshold: Minimum severity to report ('low', 'medium', 'high', 'critical')
            
        Returns:
            List of detected anomalies
        """
        # Compute stats if not done
        if not self.historical_stats:
            self.compute_historical_stats(df)
        
        anomalies = []
        severity_order = ['low', 'medium', 'high', 'critical']
        min_severity_idx = severity_order.index(severity_threshold) if severity_threshold else 0
        
        for sede in df['sede'].unique():
            sede_df = df[df['sede'] == sede]
            stats = self.historical_stats.get(sede, {})
            
            if not stats:
                logger.warning(f"No stats for sede {sede}, skipping")
                continue
            
            for _, row in sede_df.iterrows():
                # Run all checks
                checks = [
                    self._check_off_hours(row, stats),
                    self._check_weekend(row, stats),
                    self._check_spike(row, stats),
                    self._check_low_occupancy(row, stats),
                    self._check_holiday(row, stats),
                    self._check_vacation(row, stats),
                ]
                
                for anomaly in checks:
                    if anomaly is not None:
                        # Filter by severity
                        anomaly_severity_idx = severity_order.index(anomaly.severity)
                        if anomaly_severity_idx >= min_severity_idx:
                            anomalies.append(anomaly)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def detect_for_record(
        self,
        record: Dict[str, Any],
        sede: str
    ) -> List[DetectedAnomaly]:
        """
        Detect anomalies for a single record (real-time detection).
        
        Args:
            record: Dictionary with consumption data
            sede: Sede name
            
        Returns:
            List of detected anomalies
        """
        # Convert to DataFrame row
        row = pd.Series(record)
        row['sede'] = sede
        
        stats = self.historical_stats.get(sede, {})
        if not stats:
            logger.warning(f"No stats for sede {sede}")
            return []
        
        anomalies = []
        
        checks = [
            self._check_off_hours(row, stats),
            self._check_weekend(row, stats),
            self._check_spike(row, stats),
            self._check_low_occupancy(row, stats),
            self._check_holiday(row, stats),
        ]
        
        for anomaly in checks:
            if anomaly is not None:
                anomalies.append(anomaly)
        
        return anomalies
    
    def to_dict_list(self, anomalies: List[DetectedAnomaly]) -> List[Dict]:
        """Convert anomalies to list of dictionaries."""
        return [
            {
                'timestamp': a.timestamp,
                'sede': a.sede,
                'sector': a.sector,
                'anomaly_type': a.anomaly_type,
                'severity': a.severity,
                'actual_value': a.actual_value,
                'expected_value': a.expected_value,
                'deviation_pct': a.deviation_pct,
                'description': a.description,
                'recommendation': a.recommendation,
                'potential_savings_kwh': a.potential_savings_kwh,
                'z_score': a.z_score
            }
            for a in anomalies
        ]
