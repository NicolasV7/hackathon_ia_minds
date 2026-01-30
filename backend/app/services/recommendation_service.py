"""
Recommendation generation service.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.anomaly_repository import AnomalyRepository
from app.schemas.recommendation import RecommendationCreate, RecommendationResponse

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating and managing energy efficiency recommendations.
    """
    
    # Cost parameters (Colombian Pesos)
    ENERGY_COST_COP_PER_KWH = 600  # Approximate commercial rate
    CO2_FACTOR_KG_PER_KWH = 0.2  # Colombian grid factor
    
    # Recommendation templates based on anomaly types
    RECOMMENDATION_TEMPLATES = {
        'off_hours_usage': {
            'title': 'Optimizar consumo fuera de horario',
            'priority': 'high',
            'category': 'scheduling',
            'implementation_difficulty': 'medium',
            'actions': [
                'Verificar estado de equipos activos fuera de horario',
                'Instalar temporizadores en equipos no críticos',
                'Revisar programación de aires acondicionados',
                'Implementar apagado automático'
            ],
            'savings_factor': 0.35
        },
        'weekend_anomaly': {
            'title': 'Reducir consumo en fines de semana',
            'priority': 'medium',
            'category': 'behavioral',
            'implementation_difficulty': 'easy',
            'actions': [
                'Establecer protocolo de apagado viernes en la tarde',
                'Designar responsable de verificación',
                'Crear checklist de cierre semanal',
                'Apagar circuitos no esenciales'
            ],
            'savings_factor': 0.50
        },
        'consumption_spike': {
            'title': 'Gestionar picos de demanda',
            'priority': 'high',
            'category': 'scheduling',
            'implementation_difficulty': 'medium',
            'actions': [
                'Escalonar encendido de equipos de alta potencia',
                'Evitar encendido simultáneo de aires acondicionados',
                'Programar cargas pesadas fuera de horas pico',
                'Considerar sistemas de gestión de demanda'
            ],
            'savings_factor': 0.15
        },
        'statistical_outlier': {
            'title': 'Investigar consumo anómalo',
            'priority': 'medium',
            'category': 'maintenance',
            'implementation_difficulty': 'medium',
            'actions': [
                'Auditar equipos activos durante el periodo anómalo',
                'Verificar condiciones de operación',
                'Revisar mantenimiento de equipos',
                'Validar mediciones con contador principal'
            ],
            'savings_factor': 0.20
        },
        'pattern_deviation': {
            'title': 'Optimizar patrones de consumo',
            'priority': 'low',
            'category': 'behavioral',
            'implementation_difficulty': 'easy',
            'actions': [
                'Analizar cambios en patrones de uso',
                'Capacitar a usuarios en eficiencia energética',
                'Establecer metas de consumo por área',
                'Implementar monitoreo continuo'
            ],
            'savings_factor': 0.10
        },
        'sector_inefficiency': {
            'title': 'Mejorar eficiencia por sector',
            'priority': 'high',
            'category': 'equipment',
            'implementation_difficulty': 'hard',
            'actions': [
                'Auditar equipos del sector',
                'Identificar equipos obsoletos o ineficientes',
                'Evaluar reemplazo de equipos',
                'Optimizar configuración de sistemas'
            ],
            'savings_factor': 0.25
        }
    }
    
    def __init__(self):
        self.recommendation_repo = RecommendationRepository()
        self.anomaly_repo = AnomalyRepository()
    
    async def generate_recommendations_from_anomalies(
        self,
        db: AsyncSession,
        sede: str,
        days: int = 7
    ) -> List[RecommendationResponse]:
        """
        Generate recommendations based on recent anomalies.
        
        Args:
            db: Database session
            sede: Sede name
            days: Number of days to look back for anomalies
            
        Returns:
            List of RecommendationResponse objects
        """
        try:
            # Get unresolved anomalies for the sede
            anomalies = await self.anomaly_repo.get_unresolved(db=db, sede=sede)
            
            if not anomalies:
                logger.info(f"No unresolved anomalies found for sede {sede}")
                return []
            
            recommendations = []
            processed_types = set()  # Avoid duplicate recommendations
            
            for anomaly in anomalies:
                # Skip if we already processed this anomaly type
                anomaly_type = anomaly.anomaly_type
                if anomaly_type in processed_types:
                    continue
                
                processed_types.add(anomaly_type)
                
                # Get template for this anomaly type
                template = self.RECOMMENDATION_TEMPLATES.get(
                    anomaly_type,
                    self.RECOMMENDATION_TEMPLATES['statistical_outlier']
                )
                
                # Calculate potential savings
                potential_savings_kwh = anomaly.potential_savings_kwh * template['savings_factor']
                expected_savings_cop = potential_savings_kwh * self.ENERGY_COST_COP_PER_KWH
                expected_co2_reduction_kg = potential_savings_kwh * self.CO2_FACTOR_KG_PER_KWH
                
                # Generate description
                description = self._generate_description(anomaly, template)
                
                # Create recommendation
                recommendation_data = RecommendationCreate(
                    sede=sede,
                    sector=anomaly.sector,
                    anomaly_id=anomaly.id,
                    title=template['title'],
                    description=description,
                    category=template['category'],
                    priority=template['priority'],
                    expected_savings_kwh=potential_savings_kwh,
                    expected_savings_cop=expected_savings_cop,
                    expected_co2_reduction_kg=expected_co2_reduction_kg,
                    implementation_difficulty=template['implementation_difficulty'],
                    actions=template['actions'],
                    status='pending'
                )
                
                db_recommendation = await self.recommendation_repo.create(db, recommendation_data)
                recommendations.append(RecommendationResponse.model_validate(db_recommendation))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _generate_description(self, anomaly, template: dict) -> str:
        """
        Generate a detailed description for the recommendation.
        
        Args:
            anomaly: Anomaly object
            template: Recommendation template
            
        Returns:
            Description string
        """
        description = f"{anomaly.description}\n\n"
        description += f"Se detectó una desviación de {abs(anomaly.deviation_pct):.1f}% "
        description += f"respecto al consumo esperado en {anomaly.sector}.\n\n"
        description += f"Valor actual: {anomaly.actual_value:.2f} kWh\n"
        description += f"Valor esperado: {anomaly.expected_value:.2f} kWh\n\n"
        description += f"Recomendación: {anomaly.recommendation}"
        
        return description
    
    async def get_recommendations_by_sede(
        self,
        db: AsyncSession,
        sede: str,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RecommendationResponse]:
        """
        Get recommendations for a specific sede.
        
        Args:
            db: Database session
            sede: Sede name
            priority: Optional priority filter
            status: Optional status filter
            skip: Records to skip
            limit: Maximum records to return
            
        Returns:
            List of RecommendationResponse objects
        """
        recommendations = await self.recommendation_repo.get_by_sede(
            db=db,
            sede=sede,
            priority=priority,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [RecommendationResponse.model_validate(r) for r in recommendations]
    
    async def get_pending_recommendations(
        self,
        db: AsyncSession,
        sede: Optional[str] = None
    ) -> List[RecommendationResponse]:
        """
        Get pending recommendations.
        
        Args:
            db: Database session
            sede: Optional sede filter
            
        Returns:
            List of pending RecommendationResponse objects
        """
        recommendations = await self.recommendation_repo.get_pending(
            db=db,
            sede=sede
        )
        
        return [RecommendationResponse.model_validate(r) for r in recommendations]
    
    async def update_recommendation_status(
        self,
        db: AsyncSession,
        recommendation_id: int,
        status: str,
        implementation_notes: Optional[str] = None
    ) -> RecommendationResponse:
        """
        Update the status of a recommendation.
        
        Args:
            db: Database session
            recommendation_id: Recommendation ID
            status: New status (pending, in_progress, implemented, rejected)
            implementation_notes: Optional notes about implementation
            
        Returns:
            Updated RecommendationResponse
        """
        recommendation = await self.recommendation_repo.get(db, recommendation_id)
        
        if not recommendation:
            raise ValueError(f"Recommendation with ID {recommendation_id} not found")
        
        update_data = {'status': status}
        
        if status == 'implemented':
            update_data['implemented_at'] = datetime.utcnow()
        
        if implementation_notes:
            # Add notes to actions list
            current_actions = recommendation.actions or []
            current_actions.append(f"Notas de implementación: {implementation_notes}")
            update_data['actions'] = current_actions
        
        updated_recommendation = await self.recommendation_repo.update(
            db=db,
            db_obj=recommendation,
            obj_in=update_data
        )
        
        return RecommendationResponse.model_validate(updated_recommendation)
