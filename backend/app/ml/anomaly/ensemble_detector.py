"""
Ensemble anomaly detector combining multiple detection methods.

Combines:
- Rules-based detection (statistical thresholds)
- STL decomposition (time series analysis)
- Isolation Forest (existing model)

Provides more robust detection through consensus.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from .rules_engine import RulesBasedDetector, DetectedAnomaly

# STL detector is optional
try:
    from .stl_detector import STLAnomalyDetector
    STL_AVAILABLE = True
except ImportError:
    STLAnomalyDetector = None
    STL_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnsembleAnomalyDetector:
    """
    Ensemble anomaly detector combining multiple methods.
    
    Uses voting/consensus among detectors for more reliable results.
    """
    
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        min_consensus: int = 2,  # Minimum detectors that must agree
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize ensemble detector.
        
        Args:
            model_dir: Directory with saved models
            min_consensus: Minimum number of detectors for anomaly confirmation
            weights: Detector weights for scoring
        """
        self.model_dir = model_dir or Path("ml_models")
        self.min_consensus = min_consensus
        
        # Default weights
        self.weights = weights or {
            'rules': 0.4,
            'stl': 0.3,
            'isolation_forest': 0.3
        }
        
        # Initialize detectors
        self.rules_detector = RulesBasedDetector()
        
        # STL detector is optional
        if STL_AVAILABLE:
            try:
                self.stl_detector = STLAnomalyDetector()
            except Exception as e:
                logger.warning(f"STL detector initialization failed: {e}")
                self.stl_detector = None
        else:
            logger.info("STL detector not available (statsmodels not installed)")
            self.stl_detector = None
        
        # Load Isolation Forest if available
        self.isolation_forest = None
        self._load_isolation_forest()
        
        self.is_fitted = False
    
    def _load_isolation_forest(self):
        """Load pre-trained Isolation Forest model."""
        model_path = self.model_dir / "anomaly_detector.joblib"
        
        if model_path.exists():
            try:
                self.isolation_forest = joblib.load(model_path)
                logger.info(f"Isolation Forest loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load Isolation Forest: {e}")
    
    def fit(self, df: pd.DataFrame) -> 'EnsembleAnomalyDetector':
        """
        Fit the ensemble detector.
        
        Args:
            df: Historical consumption data
            
        Returns:
            self for chaining
        """
        logger.info("Fitting ensemble anomaly detector...")
        
        # Fit rules detector (computes historical stats)
        self.rules_detector.compute_historical_stats(df)
        
        # STL doesn't need explicit fitting, uses data directly
        
        # Isolation Forest should already be trained
        
        self.is_fitted = True
        logger.info("Ensemble detector fitted")
        
        return self
    
    def _run_rules_detection(
        self,
        df: pd.DataFrame,
        severity_threshold: Optional[str] = None
    ) -> List[Dict]:
        """Run rules-based detection."""
        try:
            anomalies = self.rules_detector.detect(df, severity_threshold)
            return self.rules_detector.to_dict_list(anomalies)
        except Exception as e:
            logger.error(f"Rules detection failed: {e}")
            return []
    
    def _run_stl_detection(
        self,
        df: pd.DataFrame,
        severity_threshold: Optional[str] = None
    ) -> List[Dict]:
        """Run STL-based detection."""
        if self.stl_detector is None:
            return []
        
        try:
            return self.stl_detector.detect_anomalies(df, severity_threshold=severity_threshold)
        except Exception as e:
            logger.error(f"STL detection failed: {e}")
            return []
    
    def _run_isolation_forest(
        self,
        df: pd.DataFrame
    ) -> List[Dict]:
        """Run Isolation Forest detection."""
        if self.isolation_forest is None:
            return []
        
        try:
            from ..features import prepare_full_feature_set
            
            # Prepare features
            featured_df = prepare_full_feature_set(df.copy())
            
            # Select numeric features for IF
            numeric_cols = featured_df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove target and ID columns
            exclude_cols = ['energia_total_kwh', 'id', 'reading_id']
            feature_cols = [c for c in numeric_cols if c not in exclude_cols]
            
            X = featured_df[feature_cols].fillna(0)
            
            # Predict (-1 for anomalies, 1 for normal)
            predictions = self.isolation_forest.predict(X)
            scores = self.isolation_forest.decision_function(X)
            
            anomalies = []
            
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly
                    row = df.iloc[i]
                    
                    # Determine severity based on score
                    abs_score = abs(score)
                    if abs_score >= 0.3:
                        severity = 'critical'
                    elif abs_score >= 0.2:
                        severity = 'high'
                    elif abs_score >= 0.1:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    anomalies.append({
                        'timestamp': row['timestamp'],
                        'sede': row['sede'],
                        'sector': 'total',
                        'anomaly_type': 'statistical_outlier',
                        'severity': severity,
                        'actual_value': float(row['energia_total_kwh']),
                        'expected_value': float(df['energia_total_kwh'].mean()),
                        'deviation_pct': float((row['energia_total_kwh'] - df['energia_total_kwh'].mean()) / df['energia_total_kwh'].mean() * 100),
                        'description': f"Outlier estadístico detectado por Isolation Forest (score: {score:.3f})",
                        'recommendation': "Investigar patrón de consumo inusual.",
                        'potential_savings_kwh': float(max(0, row['energia_total_kwh'] - df['energia_total_kwh'].mean())),
                        'isolation_score': float(score),
                        'detection_method': 'isolation_forest'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Isolation Forest detection failed: {e}")
            return []
    
    def _merge_anomalies(
        self,
        all_anomalies: Dict[str, List[Dict]],
        time_tolerance_hours: float = 1.0
    ) -> List[Dict]:
        """
        Merge anomalies from different detectors.
        
        Uses temporal proximity to group related detections.
        
        Args:
            all_anomalies: Dict mapping detector name to anomaly list
            time_tolerance_hours: Hours tolerance for matching anomalies
            
        Returns:
            Merged list of anomalies with consensus information
        """
        # Group by sede and approximate timestamp
        grouped: Dict[str, Dict[str, List[Dict]]] = defaultdict(lambda: defaultdict(list))
        
        for detector_name, anomalies in all_anomalies.items():
            for anomaly in anomalies:
                sede = anomaly['sede']
                ts = anomaly['timestamp']
                
                # Round timestamp to nearest hour for grouping
                if isinstance(ts, str):
                    ts = pd.to_datetime(ts)
                ts_key = ts.strftime('%Y-%m-%d %H:00')
                
                anomaly['detected_by'] = detector_name
                grouped[sede][ts_key].append(anomaly)
        
        # Merge groups
        merged = []
        
        for sede, time_groups in grouped.items():
            for ts_key, anomalies_group in time_groups.items():
                # Count unique detectors
                detectors = set(a['detected_by'] for a in anomalies_group)
                consensus = len(detectors)
                
                if consensus >= self.min_consensus:
                    # Create merged anomaly
                    # Use highest severity
                    severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                    highest_severity = max(
                        anomalies_group,
                        key=lambda x: severity_order.get(x.get('severity', 'low'), 0)
                    )['severity']
                    
                    # Average values
                    avg_actual = np.mean([a['actual_value'] for a in anomalies_group])
                    avg_expected = np.mean([a['expected_value'] for a in anomalies_group])
                    avg_deviation = np.mean([a.get('deviation_pct', 0) for a in anomalies_group])
                    
                    # Combine descriptions
                    all_types = list(set(a.get('anomaly_type', 'unknown') for a in anomalies_group))
                    
                    # Calculate ensemble score
                    ensemble_score = 0
                    for a in anomalies_group:
                        detector = a['detected_by']
                        weight = self.weights.get(detector, 0.33)
                        ensemble_score += weight
                    
                    merged_anomaly = {
                        'timestamp': pd.to_datetime(ts_key),
                        'sede': sede,
                        'sector': 'total',
                        'anomaly_type': all_types[0] if len(all_types) == 1 else 'multi_type',
                        'anomaly_types': all_types,
                        'severity': highest_severity,
                        'actual_value': float(avg_actual),
                        'expected_value': float(avg_expected),
                        'deviation_pct': float(avg_deviation),
                        'description': f"Anomalía detectada por {consensus} métodos: {', '.join(detectors)}",
                        'recommendation': anomalies_group[0].get('recommendation', ''),
                        'potential_savings_kwh': float(max(0, avg_actual - avg_expected)),
                        'consensus': consensus,
                        'detected_by': list(detectors),
                        'ensemble_score': float(ensemble_score),
                        'detection_method': 'ensemble'
                    }
                    
                    merged.append(merged_anomaly)
                
                elif consensus == 1 and self.min_consensus == 1:
                    # Single detection allowed
                    merged.extend(anomalies_group)
        
        # Sort by timestamp and severity
        merged.sort(
            key=lambda x: (
                x['timestamp'],
                -{'low': 0, 'medium': 1, 'high': 2, 'critical': 3}.get(x['severity'], 0)
            )
        )
        
        return merged
    
    def detect(
        self,
        df: pd.DataFrame,
        severity_threshold: Optional[str] = None,
        detectors: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Detect anomalies using ensemble of methods.
        
        Args:
            df: DataFrame with consumption data
            severity_threshold: Minimum severity to report
            detectors: List of detectors to use (default: all)
            
        Returns:
            List of detected anomalies
        """
        if not self.is_fitted:
            self.fit(df)
        
        detectors = detectors or ['rules', 'stl', 'isolation_forest']
        all_anomalies = {}
        
        # Run each detector
        if 'rules' in detectors:
            logger.info("Running rules-based detection...")
            all_anomalies['rules'] = self._run_rules_detection(df, severity_threshold)
            logger.info(f"Rules: {len(all_anomalies['rules'])} anomalies")
        
        if 'stl' in detectors and self.stl_detector:
            logger.info("Running STL detection...")
            all_anomalies['stl'] = self._run_stl_detection(df, severity_threshold)
            logger.info(f"STL: {len(all_anomalies['stl'])} anomalies")
        
        if 'isolation_forest' in detectors and self.isolation_forest:
            logger.info("Running Isolation Forest detection...")
            all_anomalies['isolation_forest'] = self._run_isolation_forest(df)
            logger.info(f"IF: {len(all_anomalies['isolation_forest'])} anomalies")
        
        # Merge results
        merged = self._merge_anomalies(all_anomalies)
        
        logger.info(f"Ensemble detected {len(merged)} anomalies after merging")
        return merged
    
    def detect_realtime(
        self,
        record: Dict[str, Any],
        sede: str,
        historical_df: Optional[pd.DataFrame] = None
    ) -> List[Dict]:
        """
        Detect anomalies for a single record (real-time).
        
        Args:
            record: Single consumption record
            sede: Sede name
            historical_df: Optional recent historical data for context
            
        Returns:
            List of detected anomalies
        """
        # Convert to single-row DataFrame
        df = pd.DataFrame([record])
        df['sede'] = sede
        
        # Rules detection (fast, no historical needed if stats computed)
        anomalies = []
        
        rules_anomalies = self.rules_detector.detect_for_record(record, sede)
        for a in rules_anomalies:
            anomalies.append({
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
                'detection_method': 'rules_realtime'
            })
        
        return anomalies
    
    def get_summary(
        self,
        anomalies: List[Dict]
    ) -> Dict[str, Any]:
        """
        Get summary statistics of detected anomalies.
        
        Args:
            anomalies: List of detected anomalies
            
        Returns:
            Summary statistics dictionary
        """
        if not anomalies:
            return {
                'total': 0,
                'by_severity': {},
                'by_type': {},
                'by_sede': {},
                'total_potential_savings_kwh': 0
            }
        
        df = pd.DataFrame(anomalies)
        
        return {
            'total': len(anomalies),
            'by_severity': df['severity'].value_counts().to_dict(),
            'by_type': df['anomaly_type'].value_counts().to_dict(),
            'by_sede': df['sede'].value_counts().to_dict(),
            'total_potential_savings_kwh': float(df['potential_savings_kwh'].sum()),
            'avg_deviation_pct': float(df['deviation_pct'].mean()),
            'detection_methods': df['detection_method'].value_counts().to_dict() if 'detection_method' in df else {}
        }
