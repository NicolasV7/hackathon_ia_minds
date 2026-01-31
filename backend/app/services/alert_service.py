"""
Alert service for managing and distributing real-time alerts.

Provides:
- Alert creation from anomalies and predictions
- Multi-channel distribution (WebSocket, Telegram)
- Alert aggregation and deduplication
- Alert history and persistence
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.websocket import (
    manager as ws_manager,
    Alert, AlertType, AlertSeverity,
    create_anomaly_alert,
    create_prediction_alert,
    create_recommendation_alert
)

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for managing real-time alerts.
    
    Features:
    - Alert aggregation (avoid alert fatigue)
    - Multi-channel distribution
    - Priority-based routing
    - Cooldown periods
    """
    
    # Cooldown periods (seconds) to avoid alert spam
    COOLDOWN_PERIODS = {
        'anomaly': 300,      # 5 minutes
        'prediction': 3600,  # 1 hour
        'recommendation': 1800,  # 30 minutes
        'system': 60         # 1 minute
    }
    
    # Maximum alerts per hour per sede
    MAX_ALERTS_PER_HOUR = 20
    
    def __init__(self):
        # Track last alert time by type and sede
        self.last_alert_time: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
        # Alert count tracking
        self.hourly_alert_count: Dict[str, int] = defaultdict(int)
        self.last_count_reset: datetime = datetime.utcnow()
        
        # Alert queue for batch processing
        self.alert_queue: List[Alert] = []
        
        # Telegram bot reference (optional)
        self.telegram_enabled = False
    
    def _reset_hourly_count_if_needed(self):
        """Reset hourly alert counts if hour has passed."""
        now = datetime.utcnow()
        if (now - self.last_count_reset).total_seconds() >= 3600:
            self.hourly_alert_count.clear()
            self.last_count_reset = now
    
    def _check_cooldown(
        self,
        alert_type: str,
        sede: str
    ) -> bool:
        """
        Check if cooldown period has passed.
        
        Returns True if alert can be sent.
        """
        key = f"{alert_type}_{sede}"
        last_time = self.last_alert_time.get(alert_type, {}).get(sede)
        
        if last_time is None:
            return True
        
        cooldown = self.COOLDOWN_PERIODS.get(alert_type, 60)
        elapsed = (datetime.utcnow() - last_time).total_seconds()
        
        return elapsed >= cooldown
    
    def _update_cooldown(self, alert_type: str, sede: str):
        """Update last alert time for cooldown tracking."""
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        self.last_alert_time[alert_type][sede] = datetime.utcnow()
    
    def _can_send_alert(self, sede: str, alert_type: str) -> bool:
        """Check if alert can be sent (cooldown + rate limit)."""
        self._reset_hourly_count_if_needed()
        
        # Check hourly limit
        if self.hourly_alert_count[sede] >= self.MAX_ALERTS_PER_HOUR:
            logger.warning(f"Hourly alert limit reached for {sede}")
            return False
        
        # Check cooldown
        if not self._check_cooldown(alert_type, sede):
            logger.debug(f"Alert cooldown active for {alert_type} in {sede}")
            return False
        
        return True
    
    async def send_anomaly_alert(
        self,
        anomaly: Dict[str, Any],
        sede: str,
        force: bool = False
    ) -> bool:
        """
        Send an alert for a detected anomaly.
        
        Args:
            anomaly: Anomaly data dictionary
            sede: Sede where anomaly was detected
            force: Force send even if cooldown active
            
        Returns:
            True if alert was sent
        """
        if not force and not self._can_send_alert(sede, 'anomaly'):
            return False
        
        # Only alert for high severity by default
        severity = anomaly.get('severity', 'low')
        if severity not in ['high', 'critical'] and not force:
            return False
        
        alert = create_anomaly_alert(anomaly, sede)
        
        await self._distribute_alert(alert)
        
        self._update_cooldown('anomaly', sede)
        self.hourly_alert_count[sede] += 1
        
        return True
    
    async def send_prediction_alert(
        self,
        sede: str,
        predictions: List[Dict],
        summary: Optional[Dict] = None
    ) -> bool:
        """
        Send an alert for new predictions.
        
        Args:
            sede: Sede for predictions
            predictions: List of prediction data
            summary: Optional summary statistics
            
        Returns:
            True if alert was sent
        """
        if not self._can_send_alert(sede, 'prediction'):
            return False
        
        if summary is None:
            summary = {
                'hours': len(predictions),
                'avg_kwh': sum(p.get('predicted_kwh', 0) for p in predictions) / len(predictions) if predictions else 0
            }
        
        alert = create_prediction_alert(sede, summary)
        
        await self._distribute_alert(alert)
        
        self._update_cooldown('prediction', sede)
        
        return True
    
    async def send_recommendation_alert(
        self,
        recommendation: Dict[str, Any],
        sede: str
    ) -> bool:
        """
        Send an alert for a new recommendation.
        
        Args:
            recommendation: Recommendation data
            sede: Target sede
            
        Returns:
            True if alert was sent
        """
        if not self._can_send_alert(sede, 'recommendation'):
            return False
        
        # Only alert for high priority recommendations
        priority = recommendation.get('priority', 'low')
        if priority not in ['high', 'urgent']:
            return False
        
        alert = create_recommendation_alert(recommendation, sede)
        
        await self._distribute_alert(alert)
        
        self._update_cooldown('recommendation', sede)
        self.hourly_alert_count[sede] += 1
        
        return True
    
    async def send_system_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        sede: Optional[str] = None
    ) -> bool:
        """
        Send a system-level alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            sede: Optional target sede
            
        Returns:
            True if alert was sent
        """
        alert = Alert(
            id=f"system_{datetime.utcnow().timestamp()}",
            type=AlertType.SYSTEM_ALERT,
            severity=severity,
            title=title,
            message=message,
            sede=sede
        )
        
        await self._distribute_alert(alert)
        
        return True
    
    async def _distribute_alert(self, alert: Alert):
        """
        Distribute alert to all channels.
        
        Args:
            alert: Alert to distribute
        """
        # WebSocket distribution
        try:
            await ws_manager.send_alert(alert)
        except Exception as e:
            logger.error(f"WebSocket alert failed: {e}")
        
        # Telegram distribution (if enabled and critical)
        if self.telegram_enabled and alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR]:
            try:
                await self._send_telegram_alert(alert)
            except Exception as e:
                logger.error(f"Telegram alert failed: {e}")
    
    async def _send_telegram_alert(self, alert: Alert):
        """Send alert via Telegram bot (placeholder)."""
        # This would integrate with the Telegram bot
        # For now, just log
        logger.info(f"Would send Telegram alert: {alert.title}")
    
    async def process_anomaly_batch(
        self,
        anomalies: List[Dict[str, Any]],
        sede: str
    ) -> int:
        """
        Process a batch of anomalies and send aggregated alerts.
        
        Args:
            anomalies: List of detected anomalies
            sede: Sede for anomalies
            
        Returns:
            Number of alerts sent
        """
        if not anomalies:
            return 0
        
        # Group by severity
        critical = [a for a in anomalies if a.get('severity') == 'critical']
        high = [a for a in anomalies if a.get('severity') == 'high']
        
        alerts_sent = 0
        
        # Always alert for critical
        for anomaly in critical:
            if await self.send_anomaly_alert(anomaly, sede, force=True):
                alerts_sent += 1
        
        # Alert for high severity (aggregated if many)
        if len(high) <= 3:
            for anomaly in high:
                if await self.send_anomaly_alert(anomaly, sede):
                    alerts_sent += 1
        elif high:
            # Send aggregated alert
            await self.send_system_alert(
                title=f"{len(high)} anomalías de alta severidad en {sede}",
                message=f"Se detectaron {len(high)} anomalías de alta severidad. "
                        f"Revise el dashboard para más detalles.",
                severity=AlertSeverity.ERROR,
                sede=sede
            )
            alerts_sent += 1
        
        return alerts_sent
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return {
            'hourly_counts': dict(self.hourly_alert_count),
            'total_this_hour': sum(self.hourly_alert_count.values()),
            'connections': ws_manager.get_connection_count(),
            'recent_alerts': ws_manager.get_recent_alerts(5)
        }


# Global service instance
alert_service = AlertService()
