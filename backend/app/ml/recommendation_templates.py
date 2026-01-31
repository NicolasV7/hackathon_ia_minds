"""
Extended recommendation templates for energy efficiency.

Provides sector-specific and context-aware recommendations
for different types of anomalies.
"""

from typing import Dict, List, Any

# Cost parameters for Colombia
ENERGY_COST_COP_PER_KWH = 600  # Commercial rate
CO2_FACTOR_KG_PER_KWH = 0.2    # Colombian grid emission factor
WATER_COST_COP_PER_LITER = 3  # Approximate water cost


# Extended recommendation templates
RECOMMENDATION_TEMPLATES = {
    # =========================================================================
    # OFF-HOURS CONSUMPTION
    # =========================================================================
    'off_hours_usage': {
        'title': 'Optimizar consumo nocturno en {sector}',
        'priority': 'high',
        'category': 'scheduling',
        'implementation_difficulty': 'medium',
        'payback_months': 3,
        
        # Sector-specific actions
        'actions_by_sector': {
            'laboratorios': [
                'Verificar equipos de refrigeración y experimentos en curso',
                'Programar apagado automático de equipos no críticos',
                'Instalar sensores de ocupación para iluminación',
                'Revisar UPS y sistemas de respaldo',
                'Evaluar equipos que pueden pausarse en la noche'
            ],
            'salones': [
                'Verificar que iluminación esté completamente apagada',
                'Revisar aires acondicionados en modo standby',
                'Instalar temporizadores en circuitos de iluminación',
                'Verificar proyectores y equipos audiovisuales',
                'Implementar sensores de presencia'
            ],
            'oficinas': [
                'Configurar PCs para hibernación automática después de 18:00',
                'Instalar regletas inteligentes con apagado programado',
                'Verificar impresoras y equipos en standby',
                'Revisar sistemas de climatización fuera de horario',
                'Designar responsable de verificación nocturna'
            ],
            'auditorios': [
                'Verificar sistemas de iluminación escénica',
                'Revisar equipos de sonido en standby',
                'Programar apagado automático de proyectores',
                'Verificar climatización post-eventos',
                'Implementar protocolo de cierre de eventos'
            ],
            'comedor': [
                'Revisar refrigeradores y cámaras frigoríficas (necesarios 24/7)',
                'Verificar hornos y estufas apagados',
                'Optimizar temperatura de refrigeración nocturna',
                'Apagar iluminación de servicio',
                'Revisar extractores de aire'
            ]
        },
        
        # Context templates
        'context_template': (
            "Se detectó un consumo de {actual_value:.2f} kWh a las {hora}:00 en {sector} "
            "de la sede {sede}. El consumo esperado para este horario es {expected_value:.2f} kWh, "
            "lo que representa una desviación de {deviation_pct:.0f}%."
        ),
        
        'impact_template': (
            "Implementando las acciones recomendadas, se estima un ahorro mensual de:\n"
            "- Energía: {savings_kwh:.0f} kWh\n"
            "- Costo: ${savings_cop:,.0f} COP\n"
            "- Emisiones CO₂: {savings_co2:.1f} kg"
        ),
        
        'savings_factor': 0.35,
        'confidence': 0.85
    },
    
    # =========================================================================
    # WEEKEND ANOMALY
    # =========================================================================
    'weekend_anomaly': {
        'title': 'Reducir consumo de fin de semana en {sector}',
        'priority': 'medium',
        'category': 'behavioral',
        'implementation_difficulty': 'easy',
        'payback_months': 1,
        
        'actions_by_sector': {
            'laboratorios': [
                'Identificar experimentos que requieren funcionamiento continuo',
                'Programar equipos para modo ahorro de energía',
                'Designar horarios específicos de acceso de fin de semana',
                'Implementar sistema de registro de uso en fines de semana'
            ],
            'salones': [
                'Establecer protocolo de cierre viernes tarde',
                'Verificar que no haya clases programadas sin notificación',
                'Apagar aires acondicionados completamente',
                'Desconectar equipos audiovisuales'
            ],
            'oficinas': [
                'Crear checklist de cierre semanal para cada área',
                'Designar responsable de verificación semanal',
                'Implementar apagado automático de circuitos no críticos',
                'Comunicar política de uso de fin de semana'
            ],
            'auditorios': [
                'Verificar agenda de eventos de fin de semana',
                'Protocolo especial para eventos programados',
                'Apagado total cuando no hay eventos'
            ],
            'comedor': [
                'Evaluar horarios de operación de fin de semana',
                'Optimizar refrigeración sin servicio de cocina',
                'Apagar equipos de cocción completamente'
            ]
        },
        
        'context_template': (
            "El consumo en {sede} durante el {dia_nombre} fue de {actual_value:.2f} kWh, "
            "cuando lo esperado es máximo {expected_value:.2f} kWh ({threshold_pct:.0f}% del consumo normal). "
            "Esto indica equipos o sistemas funcionando innecesariamente."
        ),
        
        'savings_factor': 0.50,
        'confidence': 0.90
    },
    
    # =========================================================================
    # CONSUMPTION SPIKE
    # =========================================================================
    'consumption_spike': {
        'title': 'Gestionar pico de demanda en {sede}',
        'priority': 'high',
        'category': 'scheduling',
        'implementation_difficulty': 'medium',
        'payback_months': 6,
        
        'actions_by_sector': {
            'default': [
                'Escalonar encendido de equipos de alta potencia (15 min entre cada uno)',
                'Evitar encendido simultáneo de múltiples aires acondicionados',
                'Programar cargas pesadas fuera de 10:00-14:00',
                'Instalar sistema de gestión de demanda',
                'Evaluar almacenamiento de energía para picos',
                'Negociar tarifas con penalización por picos reducida'
            ],
            'laboratorios': [
                'Identificar equipos de mayor demanda',
                'Programar encendido escalonado de hornos y equipos de potencia',
                'Coordinar uso de equipos entre diferentes laboratorios'
            ]
        },
        
        'context_template': (
            "Se detectó un pico de consumo de {actual_value:.2f} kWh (Z-score: {z_score:.1f}), "
            "lo que representa un incremento de {deviation_pct:.0f}% sobre el consumo promedio. "
            "Los picos de demanda pueden generar penalizaciones en la factura eléctrica."
        ),
        
        'savings_factor': 0.15,
        'confidence': 0.80
    },
    
    # =========================================================================
    # LOW OCCUPANCY HIGH CONSUMPTION
    # =========================================================================
    'low_occupancy_high_consumption': {
        'title': 'Ajustar consumo según ocupación en {sector}',
        'priority': 'high',
        'category': 'automation',
        'implementation_difficulty': 'medium',
        'payback_months': 12,
        
        'actions_by_sector': {
            'default': [
                'Instalar sensores de ocupación para control automático',
                'Implementar zonificación de climatización',
                'Programar sistemas HVAC según horarios de ocupación real',
                'Considerar sistema BMS (Building Management System)',
                'Ajustar setpoints de temperatura según ocupación'
            ],
            'salones': [
                'Vincular encendido de luces y AC con reserva de salón',
                'Implementar sensores de CO2 para ventilación por demanda',
                'Apagado automático 15 minutos después de fin de clase'
            ],
            'comedor': [
                'Ajustar capacidad de cocina según demanda proyectada',
                'Climatización por zonas según ocupación',
                'Iluminación adaptativa por área de servicio'
            ]
        },
        
        'context_template': (
            "En {sede}, el {sector} registra solo {ocupacion_pct:.0f}% de ocupación "
            "pero está consumiendo {actual_value:.2f} kWh, que representa {deviation_pct:.0f}% más "
            "de lo esperado para esta ocupación (esperado: {expected_value:.2f} kWh)."
        ),
        
        'savings_factor': 0.40,
        'confidence': 0.85
    },
    
    # =========================================================================
    # HOLIDAY CONSUMPTION
    # =========================================================================
    'holiday_consumption': {
        'title': 'Optimizar consumo en días festivos',
        'priority': 'medium',
        'category': 'behavioral',
        'implementation_difficulty': 'easy',
        'payback_months': 1,
        
        'actions_by_sector': {
            'default': [
                'Crear calendario de festivos con protocolo de cierre',
                'Designar responsable de verificación pre-festivo',
                'Programar apagado automático para festivos conocidos',
                'Documentar equipos que deben permanecer encendidos',
                'Comunicar protocolo a todo el personal'
            ]
        },
        
        'context_template': (
            "Se registró un consumo de {actual_value:.2f} kWh durante el día festivo, "
            "cuando el máximo esperado es {expected_value:.2f} kWh. "
            "Esto sugiere equipos o sistemas funcionando sin necesidad."
        ),
        
        'savings_factor': 0.50,
        'confidence': 0.90
    },
    
    # =========================================================================
    # ACADEMIC VACATION HIGH
    # =========================================================================
    'academic_vacation_high': {
        'title': 'Reducir consumo durante vacaciones académicas',
        'priority': 'medium',
        'category': 'scheduling',
        'implementation_difficulty': 'easy',
        'payback_months': 1,
        
        'actions_by_sector': {
            'default': [
                'Implementar "modo vacaciones" en sistemas de climatización',
                'Reducir iluminación a mínimos de seguridad',
                'Concentrar actividades en edificios específicos',
                'Aprovechar periodo para mantenimiento de equipos',
                'Apagar equipos no esenciales completamente'
            ],
            'laboratorios': [
                'Identificar laboratorios que pueden cerrarse completamente',
                'Consolidar experimentos en curso en menos espacios',
                'Reducir temperatura de refrigeradores no críticos'
            ],
            'oficinas': [
                'Implementar trabajo remoto durante vacaciones',
                'Concentrar personal en áreas específicas',
                'Reducir climatización en áreas vacías'
            ]
        },
        
        'context_template': (
            "Durante el periodo de vacaciones académicas ({periodo_academico}), "
            "se registró un consumo de {actual_value:.2f} kWh, cuando lo esperado "
            "es máximo {expected_value:.2f} kWh. Las vacaciones son una oportunidad "
            "para reducir significativamente el consumo."
        ),
        
        'savings_factor': 0.45,
        'confidence': 0.88
    },
    
    # =========================================================================
    # STATISTICAL OUTLIER
    # =========================================================================
    'statistical_outlier': {
        'title': 'Investigar consumo anómalo detectado',
        'priority': 'medium',
        'category': 'maintenance',
        'implementation_difficulty': 'medium',
        'payback_months': 3,
        
        'actions_by_sector': {
            'default': [
                'Realizar auditoría de equipos activos durante el periodo',
                'Verificar condiciones de operación (temperatura ambiente, etc.)',
                'Revisar mantenimiento preventivo de equipos principales',
                'Validar mediciones comparando con contador principal',
                'Documentar cualquier evento especial del periodo'
            ]
        },
        
        'context_template': (
            "Se detectó un patrón de consumo estadísticamente anómalo en {sede}. "
            "El consumo de {actual_value:.2f} kWh difiere significativamente del patrón esperado "
            "(score de anomalía: {anomaly_score:.2f}). Se recomienda investigación."
        ),
        
        'savings_factor': 0.20,
        'confidence': 0.70
    },
    
    # =========================================================================
    # SECTOR RATIO ANOMALY
    # =========================================================================
    'sector_ratio_anomaly': {
        'title': 'Balancear consumo por sector en {sede}',
        'priority': 'low',
        'category': 'monitoring',
        'implementation_difficulty': 'medium',
        'payback_months': 6,
        
        'actions_by_sector': {
            'default': [
                'Analizar distribución histórica de consumo por sector',
                'Identificar sector con desviación significativa',
                'Realizar auditoría energética del sector afectado',
                'Comparar con ratios de sedes similares',
                'Establecer benchmarks de consumo por sector'
            ]
        },
        
        'context_template': (
            "El sector {sector} en {sede} está consumiendo {actual_ratio:.0f}% del total, "
            "cuando lo esperado es {expected_ratio:.0f}%. Esta desviación de {deviation_pct:.0f}% "
            "sugiere posible ineficiencia o uso anormal del sector."
        ),
        
        'savings_factor': 0.15,
        'confidence': 0.75
    }
}


def get_recommendation_for_anomaly(
    anomaly: Dict[str, Any],
    sede_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate a complete recommendation for an anomaly.
    
    Args:
        anomaly: Anomaly dictionary
        sede_info: Optional sede information
        
    Returns:
        Complete recommendation dictionary
    """
    anomaly_type = anomaly.get('anomaly_type', 'statistical_outlier')
    template = RECOMMENDATION_TEMPLATES.get(
        anomaly_type,
        RECOMMENDATION_TEMPLATES['statistical_outlier']
    )
    
    sector = anomaly.get('sector', 'total')
    sede = anomaly.get('sede', 'desconocida')
    
    # Get sector-specific actions
    actions = template.get('actions_by_sector', {}).get(
        sector,
        template.get('actions_by_sector', {}).get('default', [])
    )
    
    if not actions:
        actions = template.get('actions_by_sector', {}).get('default', [
            'Investigar causa de la anomalía',
            'Revisar equipos involucrados',
            'Documentar hallazgos'
        ])
    
    # Calculate savings
    potential_savings_kwh = anomaly.get('potential_savings_kwh', 0)
    monthly_savings_kwh = potential_savings_kwh * 30 * template.get('savings_factor', 0.2)
    monthly_savings_cop = monthly_savings_kwh * ENERGY_COST_COP_PER_KWH
    monthly_co2_reduction = monthly_savings_kwh * CO2_FACTOR_KG_PER_KWH
    
    # Format title
    title = template['title'].format(
        sector=sector,
        sede=sede
    )
    
    # Generate context description
    context_vars = {
        'actual_value': anomaly.get('actual_value', 0),
        'expected_value': anomaly.get('expected_value', 0),
        'deviation_pct': abs(anomaly.get('deviation_pct', 0)),
        'sede': sede,
        'sector': sector,
        'hora': anomaly.get('timestamp').hour if hasattr(anomaly.get('timestamp'), 'hour') else 0,
        'dia_nombre': anomaly.get('dia_nombre', 'día'),
        'threshold_pct': 40,
        'ocupacion_pct': anomaly.get('ocupacion_pct', 50),
        'z_score': anomaly.get('z_score', 0),
        'periodo_academico': anomaly.get('periodo_academico', 'periodo'),
        'anomaly_score': anomaly.get('anomaly_score', 0),
        'actual_ratio': anomaly.get('actual_ratio', 0) * 100,
        'expected_ratio': anomaly.get('expected_ratio', 0) * 100,
    }
    
    try:
        context = template.get('context_template', '').format(**context_vars)
    except KeyError:
        context = anomaly.get('description', '')
    
    # Generate impact description
    impact = template.get('impact_template', '').format(
        savings_kwh=monthly_savings_kwh,
        savings_cop=monthly_savings_cop,
        savings_co2=monthly_co2_reduction
    ) if 'impact_template' in template else ''
    
    return {
        'title': title,
        'description': f"{context}\n\n{impact}" if impact else context,
        'category': template['category'],
        'priority': template['priority'],
        'implementation_difficulty': template['implementation_difficulty'],
        'actions': actions,
        'expected_savings_kwh': monthly_savings_kwh,
        'expected_savings_cop': monthly_savings_cop,
        'expected_co2_reduction_kg': monthly_co2_reduction,
        'payback_months': template.get('payback_months', 6),
        'confidence': template.get('confidence', 0.8),
        'anomaly_type': anomaly_type,
        'sede': sede,
        'sector': sector
    }


def get_quick_recommendations(
    anomalies: List[Dict],
    max_recommendations: int = 5
) -> List[Dict]:
    """
    Get prioritized quick recommendations from a list of anomalies.
    
    Args:
        anomalies: List of anomaly dictionaries
        max_recommendations: Maximum recommendations to return
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    seen_types = set()
    
    # Sort by severity and potential savings
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_anomalies = sorted(
        anomalies,
        key=lambda x: (
            severity_order.get(x.get('severity', 'low'), 3),
            -x.get('potential_savings_kwh', 0)
        )
    )
    
    for anomaly in sorted_anomalies:
        anomaly_type = anomaly.get('anomaly_type', 'unknown')
        sede = anomaly.get('sede', '')
        
        # Avoid duplicate types per sede
        key = f"{anomaly_type}_{sede}"
        if key in seen_types:
            continue
        
        seen_types.add(key)
        rec = get_recommendation_for_anomaly(anomaly)
        recommendations.append(rec)
        
        if len(recommendations) >= max_recommendations:
            break
    
    return recommendations
