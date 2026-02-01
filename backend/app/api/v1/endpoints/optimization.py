"""
Optimization and sustainability endpoints.
Provides savings projections, opportunities, and sustainability metrics.
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.get("/opportunities")
async def get_optimization_opportunities(
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get optimization opportunities with potential savings.
    
    Returns areas where energy efficiency can be improved.
    """
    try:
        opportunities = [
            {
                "area": "Climatización inteligente",
                "potencial_ahorro": 15200,
                "descripcion": "Optimizar sistemas HVAC con sensores de ocupación en aulas y oficinas",
                "prioridad": "alta",
                "roi_meses": 18,
                "categoria": "HVAC"
            },
            {
                "area": "Sensores de presencia",
                "potencial_ahorro": 8500,
                "descripcion": "Iluminación automática LED en aulas, pasillos y baños",
                "prioridad": "alta",
                "roi_meses": 12,
                "categoria": "Iluminación"
            },
            {
                "area": "Equipos eficientes",
                "potencial_ahorro": 12300,
                "descripcion": "Reemplazo de equipos de laboratorio obsoletos por modelos Energy Star",
                "prioridad": "media",
                "roi_meses": 24,
                "categoria": "Equipamiento"
            },
            {
                "area": "Paneles solares",
                "potencial_ahorro": 22000,
                "descripcion": "Instalación de 500kW en techos de edificios principales",
                "prioridad": "media",
                "roi_meses": 60,
                "categoria": "Renovables"
            },
            {
                "area": "Gestión de horarios",
                "potencial_ahorro": 6800,
                "descripcion": "Apagado automático fuera de horario académico",
                "prioridad": "alta",
                "roi_meses": 6,
                "categoria": "Gestión"
            },
            {
                "area": "Aislamiento térmico",
                "potencial_ahorro": 9500,
                "descripcion": "Mejora de ventanas y aislamiento en edificios antiguos",
                "prioridad": "baja",
                "roi_meses": 36,
                "categoria": "Infraestructura"
            }
        ]
        
        if sede:
            # Adjust values slightly per sede
            multipliers = {
                "tunja": 1.0,
                "duitama": 0.4,
                "sogamoso": 0.35,
                "chiquinquira": 0.15
            }
            mult = multipliers.get(sede.lower(), 1.0)
            for opp in opportunities:
                opp["potencial_ahorro"] = int(opp["potencial_ahorro"] * mult)
        
        return opportunities
        
    except Exception as e:
        logger.error(f"Error getting optimization opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/savings-projection")
async def get_savings_projection(
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get savings projection for waterfall chart.
    
    Returns current consumption and projected savings by category.
    """
    try:
        base_consumption = 100000
        
        if sede:
            consumption_by_sede = {
                "tunja": 45000,
                "duitama": 18200,
                "sogamoso": 15500,
                "chiquinquira": 6800
            }
            base_consumption = consumption_by_sede.get(sede.lower(), 100000)
        
        projection = [
            {"categoria": "Consumo actual", "valor": base_consumption, "tipo": "total"},
            {"categoria": "Climatización", "valor": -int(base_consumption * 0.15), "tipo": "ahorro"},
            {"categoria": "Iluminación", "valor": -int(base_consumption * 0.08), "tipo": "ahorro"},
            {"categoria": "Equipos", "valor": -int(base_consumption * 0.12), "tipo": "ahorro"},
            {"categoria": "Gestión horaria", "valor": -int(base_consumption * 0.05), "tipo": "ahorro"},
            {"categoria": "Consumo proyectado", "valor": int(base_consumption * 0.60), "tipo": "total"}
        ]
        
        return projection
        
    except Exception as e:
        logger.error(f"Error getting savings projection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sustainability")
async def get_sustainability_contribution(
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get sustainability contribution metrics.
    
    Returns environmental impact equivalents.
    """
    try:
        # Base values for all sedes
        base_metrics = {
            "arboles_salvados": 847,
            "agua_ahorrada": 12500,  # m³
            "co2_reducido": 125.3,   # toneladas
            "energia_renovable_equivalente": 45000,  # kWh
            "hogares_equivalentes": 38,
            "km_auto_evitados": 512000
        }
        
        if sede:
            multipliers = {
                "tunja": 1.0,
                "duitama": 0.4,
                "sogamoso": 0.35,
                "chiquinquira": 0.15
            }
            mult = multipliers.get(sede.lower(), 1.0)
            base_metrics = {k: int(v * mult) if isinstance(v, int) else round(v * mult, 1) 
                          for k, v in base_metrics.items()}
        
        return base_metrics
        
    except Exception as e:
        logger.error(f"Error getting sustainability contribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pareto")
async def get_pareto_analysis(
    sede: str = Query(None, description="Filter by sede"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get Pareto analysis of energy waste causes.
    
    Returns causes sorted by impact with cumulative percentage.
    """
    try:
        # Base Pareto data
        base_pareto = [
            {"causa": "Climatización 24/7", "porcentaje": 35, 
             "descripcion": "Sistemas HVAC funcionando fuera de horario"},
            {"causa": "Iluminación sin uso", "porcentaje": 25,
             "descripcion": "Luces encendidas en espacios vacíos"},
            {"causa": "Equipos en standby", "porcentaje": 18,
             "descripcion": "Computadores y equipos en modo espera"},
            {"causa": "Fugas de agua", "porcentaje": 12,
             "descripcion": "Pérdidas en sistema de distribución"},
            {"causa": "Otros", "porcentaje": 10,
             "descripcion": "Otros consumos no optimizados"}
        ]
        
        # Sede-specific variations (adjust percentages based on sede characteristics)
        sede_variations = {
            "tunja": [35, 25, 18, 12, 10],  # Base - balanced
            "duitama": [40, 22, 15, 13, 10],  # Higher HVAC (older buildings)
            "sogamoso": [32, 28, 16, 14, 10],  # Higher lighting (more classrooms)
            "chiquinquira": [30, 20, 20, 15, 15]  # Higher others (smaller, less optimized)
        }
        
        # Get variations for the sede
        variations = sede_variations.get(sede.lower() if sede else "tunja", sede_variations["tunja"])
        
        # Build Pareto with variations
        pareto = []
        acumulado = 0
        for i, item in enumerate(base_pareto):
            porcentaje = variations[i]
            acumulado += porcentaje
            pareto.append({
                "causa": item["causa"],
                "porcentaje": porcentaje,
                "acumulado": acumulado,
                "descripcion": item["descripcion"]
            })
        
        return pareto
        
    except Exception as e:
        logger.error(f"Error getting Pareto analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
