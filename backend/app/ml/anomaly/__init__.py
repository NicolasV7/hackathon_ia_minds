"""
Anomaly detection package for UPTC EcoEnergy.

Provides multiple detection methods:
- Statistical rules (Z-Score, IQR)
- Isolation Forest (existing)
- Ensemble detection
"""

from .rules_engine import RulesBasedDetector, ANOMALY_RULES

# STL requires statsmodels which may have conflicts
# from .stl_detector import STLAnomalyDetector
from .ensemble_detector import EnsembleAnomalyDetector

__all__ = [
    'RulesBasedDetector',
    # 'STLAnomalyDetector', 
    'EnsembleAnomalyDetector',
    'ANOMALY_RULES'
]
