"""
WebSocket manager for real-time alerts and notifications.

Provides:
- Connection management
- Room-based broadcasting (by sede)
- Alert distribution
- Connection health monitoring
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of real-time alerts."""
    ANOMALY_DETECTED = "anomaly_detected"
    PREDICTION_READY = "prediction_ready"
    RECOMMENDATION_NEW = "recommendation_new"
    CONSUMPTION_UPDATE = "consumption_update"
    SYSTEM_ALERT = "system_alert"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a real-time alert."""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    sede: Optional[str] = None
    sector: Optional[str] = None
    data: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        d['type'] = self.type.value if isinstance(self.type, AlertType) else self.type
        d['severity'] = self.severity.value if isinstance(self.severity, AlertSeverity) else self.severity
        return d


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.
    
    Features:
    - Room-based connections (by sede)
    - Broadcast to all or specific rooms
    - Connection health monitoring
    - Automatic cleanup of dead connections
    """
    
    def __init__(self):
        # All active connections
        self.active_connections: List[WebSocket] = []
        
        # Connections grouped by sede (room)
        self.sede_connections: Dict[str, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        
        # Alert history (limited)
        self.alert_history: List[Alert] = []
        self.max_history = 100
    
    async def connect(
        self,
        websocket: WebSocket,
        sede: Optional[str] = None,
        client_id: Optional[str] = None
    ):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            sede: Optional sede to subscribe to
            client_id: Optional client identifier
        """
        await websocket.accept()
        
        self.active_connections.append(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'connected_at': datetime.utcnow(),
            'sede': sede,
            'client_id': client_id
        }
        
        # Add to sede room if specified
        if sede:
            if sede not in self.sede_connections:
                self.sede_connections[sede] = set()
            self.sede_connections[sede].add(websocket)
        
        logger.info(f"WebSocket connected: {client_id or 'anonymous'} -> sede: {sede}")
        
        # Send connection confirmation
        await self._send_to_socket(websocket, {
            'type': 'connection_established',
            'message': 'Connected to UPTC EcoEnergy alerts',
            'sede': sede,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket to disconnect
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from sede rooms
        metadata = self.connection_metadata.get(websocket, {})
        sede = metadata.get('sede')
        
        if sede and sede in self.sede_connections:
            self.sede_connections[sede].discard(websocket)
            if not self.sede_connections[sede]:
                del self.sede_connections[sede]
        
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected from sede: {sede}")
    
    async def subscribe_to_sede(self, websocket: WebSocket, sede: str):
        """
        Subscribe a connection to a sede's alerts.
        
        Args:
            websocket: WebSocket connection
            sede: Sede to subscribe to
        """
        if sede not in self.sede_connections:
            self.sede_connections[sede] = set()
        
        self.sede_connections[sede].add(websocket)
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['sede'] = sede
        
        await self._send_to_socket(websocket, {
            'type': 'subscribed',
            'sede': sede,
            'message': f'Subscribed to alerts for {sede}'
        })
    
    async def _send_to_socket(self, websocket: WebSocket, data: Dict):
        """Send data to a single socket with error handling."""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send to socket: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message dictionary to broadcast
        """
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                dead_connections.append(connection)
        
        # Cleanup dead connections
        for conn in dead_connections:
            await self.disconnect(conn)
    
    async def broadcast_to_sede(self, sede: str, message: Dict):
        """
        Broadcast message to all clients subscribed to a sede.
        
        Args:
            sede: Target sede
            message: Message dictionary to broadcast
        """
        if sede not in self.sede_connections:
            return
        
        dead_connections = []
        
        for connection in self.sede_connections[sede]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to sede connection: {e}")
                dead_connections.append(connection)
        
        # Cleanup
        for conn in dead_connections:
            await self.disconnect(conn)
    
    async def send_alert(self, alert: Alert):
        """
        Send an alert to appropriate clients.
        
        Args:
            alert: Alert to send
        """
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        message = {
            'type': 'alert',
            'alert': alert.to_dict()
        }
        
        # Send to specific sede if specified, otherwise broadcast
        if alert.sede:
            await self.broadcast_to_sede(alert.sede, message)
            # Also send to clients not subscribed to specific sede
            for conn in self.active_connections:
                metadata = self.connection_metadata.get(conn, {})
                if metadata.get('sede') is None:
                    await self._send_to_socket(conn, message)
        else:
            await self.broadcast(message)
        
        logger.info(f"Alert sent: {alert.type} - {alert.title}")
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get connection statistics."""
        return {
            'total': len(self.active_connections),
            'by_sede': {
                sede: len(conns) 
                for sede, conns in self.sede_connections.items()
            }
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alert history."""
        return [a.to_dict() for a in self.alert_history[-limit:]]


# Global connection manager instance
manager = ConnectionManager()


# Helper functions for creating alerts
def create_anomaly_alert(
    anomaly: Dict[str, Any],
    sede: str
) -> Alert:
    """Create an alert from an anomaly detection."""
    severity_map = {
        'critical': AlertSeverity.CRITICAL,
        'high': AlertSeverity.ERROR,
        'medium': AlertSeverity.WARNING,
        'low': AlertSeverity.INFO
    }
    
    return Alert(
        id=f"anomaly_{datetime.utcnow().timestamp()}",
        type=AlertType.ANOMALY_DETECTED,
        severity=severity_map.get(anomaly.get('severity', 'low'), AlertSeverity.INFO),
        title=f"Anomalía detectada en {sede}",
        message=anomaly.get('description', 'Se detectó un patrón de consumo anómalo'),
        sede=sede,
        sector=anomaly.get('sector'),
        data={
            'anomaly_type': anomaly.get('anomaly_type'),
            'actual_value': anomaly.get('actual_value'),
            'expected_value': anomaly.get('expected_value'),
            'deviation_pct': anomaly.get('deviation_pct'),
            'recommendation': anomaly.get('recommendation')
        }
    )


def create_prediction_alert(
    sede: str,
    prediction_summary: Dict[str, Any]
) -> Alert:
    """Create an alert for new predictions."""
    return Alert(
        id=f"prediction_{datetime.utcnow().timestamp()}",
        type=AlertType.PREDICTION_READY,
        severity=AlertSeverity.INFO,
        title=f"Predicción actualizada para {sede}",
        message=f"Nuevas predicciones disponibles para las próximas {prediction_summary.get('hours', 24)} horas",
        sede=sede,
        data=prediction_summary
    )


def create_recommendation_alert(
    recommendation: Dict[str, Any],
    sede: str
) -> Alert:
    """Create an alert for a new recommendation."""
    priority_severity = {
        'urgent': AlertSeverity.CRITICAL,
        'high': AlertSeverity.ERROR,
        'medium': AlertSeverity.WARNING,
        'low': AlertSeverity.INFO
    }
    
    return Alert(
        id=f"rec_{datetime.utcnow().timestamp()}",
        type=AlertType.RECOMMENDATION_NEW,
        severity=priority_severity.get(recommendation.get('priority', 'low'), AlertSeverity.INFO),
        title=recommendation.get('title', 'Nueva recomendación'),
        message=f"Ahorro potencial: ${recommendation.get('expected_savings_cop', 0):,.0f} COP/mes",
        sede=sede,
        sector=recommendation.get('sector'),
        data=recommendation
    )
