"""
ML Models package for UPTC EcoEnergy.

Contains model implementations for:
- Energy consumption prediction (Prophet, XGBoost, Ensemble)
- Anomaly detection
- Sector-specific models
"""

from .prophet_model import ProphetPredictor
from .ensemble import EnsemblePredictor

__all__ = ['ProphetPredictor', 'EnsemblePredictor']
