"""
Anomaly detection package for UPTC EcoEnergy.

Provides multiple detection methods:
- Statistical rules (Z-Score, IQR)
- STL decomposition
- Isolation Forest (existing)
- Ensemble detection
"""

from .rules_engine import RulesBasedDetector, ANOMALY_RULES
from .stl_detector import STLAnomalyDetector
from .ensemble_detector import EnsembleAnomalyDetector

__all__ = [
    'RulesBasedDetector',
    'STLAnomalyDetector', 
    'EnsembleAnomalyDetector',
    'ANOMALY_RULES'
]
