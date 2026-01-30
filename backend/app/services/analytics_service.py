"""
Analytics service for dashboard statistics and KPIs.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.repositories.consumption_repository import ConsumptionRepository
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.recommendation_repository import RecommendationRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics, dashboard KPIs, and statistics.
    """
    
    def __init__(self):
        self.consumption_repo = ConsumptionRepository()
        self.anomaly_repo = AnomalyRepository()
        self.prediction_repo = PredictionRepository()
        self.recommendation_repo = RecommendationRepository()
    
    async def get_dashboard_kpis(
        self,
        db: AsyncSession,
        sede: str,
        days: int = 30
    ) -> Dict:
        """
        Get key performance indicators for the dashboard.
        
        Args:
            db: Database session
            sede: Sede name
            days: Number of days to analyze
            
        Returns:
            Dictionary with KPI data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get consumption statistics
            consumption_stats = await self.consumption_repo.get_statistics(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get anomaly summary
            anomaly_summary = await self.anomaly_repo.get_summary_by_sede(
                db=db,
                sede=sede
            )
            
            # Get pending recommendations
            pending_recommendations = await self.recommendation_repo.get_pending(
                db=db,
                sede=sede
            )
            
            # Calculate total potential savings from recommendations
            total_potential_savings_kwh = sum(
                r.expected_savings_kwh for r in pending_recommendations
            )
            total_potential_savings_cop = sum(
                r.expected_savings_cop for r in pending_recommendations
            )
            
            # Get recent predictions for trend analysis
            recent_predictions = await self.prediction_repo.get_latest_batch(
                db=db,
                sede=sede,
                limit=24
            )
            
            avg_predicted_consumption = (
                sum(p.predicted_kwh for p in recent_predictions) / len(recent_predictions)
                if recent_predictions else 0
            )
            
            return {
                'sede': sede,
                'period_days': days,
                'consumption': {
                    'total_kwh': consumption_stats['total_consumption'],
                    'avg_kwh': consumption_stats['avg_consumption'],
                    'max_kwh': consumption_stats['max_consumption'],
                    'min_kwh': consumption_stats['min_consumption'],
                    'record_count': consumption_stats['record_count']
                },
                'anomalies': {
                    'total': sum(anomaly_summary['by_severity'].values()),
                    'by_severity': anomaly_summary['by_severity'],
                    'by_type': anomaly_summary['by_type'],
                    'potential_savings_kwh': anomaly_summary['total_potential_savings_kwh']
                },
                'recommendations': {
                    'total_pending': len(pending_recommendations),
                    'potential_savings_kwh': total_potential_savings_kwh,
                    'potential_savings_cop': total_potential_savings_cop
                },
                'predictions': {
                    'avg_predicted_kwh': avg_predicted_consumption,
                    'forecast_count': len(recent_predictions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard KPIs: {str(e)}")
            raise
    
    async def get_consumption_trends(
        self,
        db: AsyncSession,
        sede: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = 'hourly'
    ) -> Dict:
        """
        Get consumption trends over time.
        
        Args:
            db: Database session
            sede: Sede name
            start_date: Start datetime
            end_date: End datetime
            granularity: 'hourly', 'daily', or 'weekly'
            
        Returns:
            Dictionary with trend data
        """
        try:
            # Get consumption data
            consumption_records = await self.consumption_repo.get_by_sede_and_date_range(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            if not consumption_records:
                return {
                    'sede': sede,
                    'granularity': granularity,
                    'data_points': [],
                    'statistics': {}
                }
            
            # Aggregate by granularity
            if granularity == 'hourly':
                data_points = [
                    {
                        'timestamp': r.timestamp,
                        'consumption_kwh': r.energia_total_kwh,
                        'hora': r.hora
                    }
                    for r in consumption_records
                ]
            else:
                # For daily/weekly, would need more complex aggregation
                # Simplified version for now
                data_points = [
                    {
                        'timestamp': r.timestamp,
                        'consumption_kwh': r.energia_total_kwh
                    }
                    for r in consumption_records
                ]
            
            # Calculate statistics
            consumptions = [r.energia_total_kwh for r in consumption_records]
            
            statistics = {
                'mean': sum(consumptions) / len(consumptions),
                'max': max(consumptions),
                'min': min(consumptions),
                'count': len(consumptions)
            }
            
            return {
                'sede': sede,
                'granularity': granularity,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'data_points': data_points,
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"Error getting consumption trends: {str(e)}")
            raise
    
    async def get_sector_breakdown(
        self,
        db: AsyncSession,
        sede: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get consumption breakdown by sector.
        
        Args:
            db: Database session
            sede: Sede name
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            Dictionary with sector breakdown
        """
        try:
            # Get consumption data
            consumption_records = await self.consumption_repo.get_by_sede_and_date_range(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            if not consumption_records:
                return {
                    'sede': sede,
                    'sectors': {},
                    'total_kwh': 0
                }
            
            # Calculate totals by sector
            sectors = {
                'comedor': 0.0,
                'salones': 0.0,
                'laboratorios': 0.0,
                'auditorios': 0.0,
                'oficinas': 0.0
            }
            
            for record in consumption_records:
                sectors['comedor'] += record.energia_comedor_kwh or 0
                sectors['salones'] += record.energia_salones_kwh or 0
                sectors['laboratorios'] += record.energia_laboratorios_kwh or 0
                sectors['auditorios'] += record.energia_auditorios_kwh or 0
                sectors['oficinas'] += record.energia_oficinas_kwh or 0
            
            total_kwh = sum(sectors.values())
            
            # Calculate percentages
            sector_breakdown = {}
            for sector, kwh in sectors.items():
                sector_breakdown[sector] = {
                    'consumption_kwh': kwh,
                    'percentage': (kwh / total_kwh * 100) if total_kwh > 0 else 0
                }
            
            return {
                'sede': sede,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sectors': sector_breakdown,
                'total_kwh': total_kwh
            }
            
        except Exception as e:
            logger.error(f"Error getting sector breakdown: {str(e)}")
            raise
    
    async def get_hourly_patterns(
        self,
        db: AsyncSession,
        sede: str,
        days: int = 30
    ) -> Dict:
        """
        Get hourly consumption patterns.
        
        Args:
            db: Database session
            sede: Sede name
            days: Number of days to analyze
            
        Returns:
            Dictionary with hourly pattern data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get hourly averages
            hourly_data = await self.consumption_repo.get_hourly_average(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                'sede': sede,
                'period_days': days,
                'hourly_averages': hourly_data
            }
            
        except Exception as e:
            logger.error(f"Error getting hourly patterns: {str(e)}")
            raise
    
    async def get_efficiency_score(
        self,
        db: AsyncSession,
        sede: str,
        days: int = 30
    ) -> Dict:
        """
        Calculate an efficiency score for the sede.
        
        Args:
            db: Database session
            sede: Sede name
            days: Number of days to analyze
            
        Returns:
            Dictionary with efficiency score and components
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get anomaly count
            anomalies = await self.anomaly_repo.get_by_date_range(
                db=db,
                start_date=start_date,
                end_date=end_date,
                sede=sede
            )
            
            # Get consumption statistics
            stats = await self.consumption_repo.get_statistics(
                db=db,
                sede=sede,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate score components (0-100 scale)
            # 1. Anomaly score (fewer anomalies = better)
            total_records = stats['record_count']
            anomaly_rate = len(anomalies) / total_records if total_records > 0 else 0
            anomaly_score = max(0, 100 - (anomaly_rate * 1000))  # Scale appropriately
            
            # 2. Consistency score (lower std deviation = better)
            # Simplified: use a baseline expectation
            consistency_score = 75  # Placeholder
            
            # 3. Off-hours efficiency (check weekend/night consumption)
            off_hours_anomalies = [
                a for a in anomalies 
                if a.anomaly_type in ['off_hours_usage', 'weekend_anomaly']
            ]
            off_hours_rate = len(off_hours_anomalies) / len(anomalies) if anomalies else 0
            off_hours_score = max(0, 100 - (off_hours_rate * 100))
            
            # Overall score (weighted average)
            overall_score = (
                anomaly_score * 0.4 +
                consistency_score * 0.3 +
                off_hours_score * 0.3
            )
            
            return {
                'sede': sede,
                'period_days': days,
                'overall_score': round(overall_score, 1),
                'components': {
                    'anomaly_score': round(anomaly_score, 1),
                    'consistency_score': round(consistency_score, 1),
                    'off_hours_score': round(off_hours_score, 1)
                },
                'metrics': {
                    'total_anomalies': len(anomalies),
                    'anomaly_rate': round(anomaly_rate * 100, 2),
                    'off_hours_anomalies': len(off_hours_anomalies)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {str(e)}")
            raise
