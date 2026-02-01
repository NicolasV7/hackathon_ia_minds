"""
Recommendation endpoints.
"""

import logging
import os
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import (
    RecommendationGenerationRequest,
    RecommendationResponse,
    RecommendationStatusUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])
recommendation_service = RecommendationService()


class AIRecommendationResponse(BaseModel):
    recomendaciones: List[Dict]


@router.post("/generate", response_model=List[RecommendationResponse], status_code=201)
async def generate_recommendations(
    request: RecommendationGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate recommendations based on recent anomalies.
    
    Args:
        request: Generation request with sede and lookback period
        db: Database session
        
    Returns:
        List of generated RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.generate_recommendations_from_anomalies(
            db=db,
            sede=request.sede,
            days=request.days
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sede/{sede}", response_model=List[RecommendationResponse])
async def get_recommendations_by_sede(
    sede: str,
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high, urgent)"),
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, implemented, rejected)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations for a specific sede.
    
    Args:
        sede: Sede name
        priority: Optional priority filter
        status: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.get_recommendations_by_sede(
            db=db,
            sede=sede,
            priority=priority,
            status=status,
            skip=skip,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending", response_model=List[RecommendationResponse])
async def get_pending_recommendations(
    sede: Optional[str] = Query(None, description="Optional sede filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending recommendations.
    
    Args:
        sede: Optional sede filter
        db: Database session
        
    Returns:
        List of pending RecommendationResponse objects
    """
    try:
        recommendations = await recommendation_service.get_pending_recommendations(
            db=db,
            sede=sede
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{recommendation_id}/status", response_model=RecommendationResponse)
async def update_recommendation_status(
    recommendation_id: int,
    status_update: RecommendationStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the status of a recommendation.
    
    Args:
        recommendation_id: Recommendation ID
        status_update: Status update with new status and optional notes
        db: Database session
        
    Returns:
        Updated RecommendationResponse
    """
    try:
        recommendation = await recommendation_service.update_recommendation_status(
            db=db,
            recommendation_id=recommendation_id,
            status=status_update.status,
            implementation_notes=status_update.implementation_notes
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-generate", response_model=AIRecommendationResponse)
async def generate_ai_recommendations(
    sede: str = Query(..., description="Sede name"),
    energia: float = Query(..., description="Current energy consumption"),
    agua: float = Query(..., description="Current water consumption"),
    co2: float = Query(..., description="Current CO2 emissions"),
    anomalias: int = Query(0, description="Number of active anomalies"),
) -> AIRecommendationResponse:
    """
    Generate AI-powered recommendations based on current system data.
    
    Uses OpenAI to analyze consumption patterns and generate personalized actions.
    """
    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai_key:
            # Return fallback recommendations without OpenAI
            return AIRecommendationResponse(
                recomendaciones=get_fallback_recommendations(sede, energia, agua, co2, anomalias)
            )
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            # Prepare context for OpenAI
            context = f"""Analiza los siguientes datos de consumo energético de la UPTC sede {sede}:

DATOS ACTUALES:
- Consumo de energía: {energia:.0f} kWh/mes
- Consumo de agua: {agua:.0f} m³/mes
- Emisiones CO2: {co2:.1f} toneladas/mes
- Anomalías detectadas: {anomalias}

Genera 3 recomendaciones específicas y accionables para mejorar la eficiencia energética.
Cada recomendación debe incluir:
1. Un título claro
2. Una descripción detallada de la acción a tomar
3. La prioridad (alta/media/baja)
4. El ahorro estimado en kWh/mes
5. El sector específico donde aplicar (Comedores, Laboratorios, Aulas, Oficinas, Auditorios)

Responde en formato JSON con esta estructura:
{{
  "recomendaciones": [
    {{
      "titulo": "string",
      "descripcion": "string",
      "prioridad": "alta|media|baja",
      "ahorro_estimado": number,
      "sector": "string"
    }}
  ]
}}"""

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto en eficiencia energética universitaria. Generas recomendaciones prácticas y específicas basadas en datos de consumo. Responde SOLO en formato JSON válido."
                    },
                    {"role": "user", "content": context}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            response_text = completion.choices[0].message.content
            
            # Parse JSON response
            import json
            try:
                recommendations = json.loads(response_text)
                if "recomendaciones" in recommendations:
                    # Format to match frontend expectations
                    formatted_recs = []
                    for i, rec in enumerate(recommendations["recomendaciones"]):
                        formatted_recs.append({
                            "id": f"AI-{i+1}",
                            "sede": sede,
                            "sector": rec.get("sector", "General"),
                            "tipo": "ia",
                            "descripcion": rec.get("descripcion", rec.get("titulo", "")),
                            "ahorro_estimado": rec.get("ahorro_estimado", 50),
                            "prioridad": rec.get("prioridad", "media"),
                            "estado": "pendiente"
                        })
                    return AIRecommendationResponse(recomendaciones=formatted_recs)
            except json.JSONDecodeError:
                logger.warning("OpenAI response is not valid JSON, using fallback")
                
        except ImportError:
            logger.warning("OpenAI library not installed")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
        
        # Fallback to predefined recommendations
        return AIRecommendationResponse(
            recomendaciones=get_fallback_recommendations(sede, energia, agua, co2, anomalias)
        )
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_fallback_recommendations(sede: str, energia: float, agua: float, co2: float, anomalias: int) -> List[Dict]:
    """Generate fallback recommendations based on data patterns."""
    recommendations = []
    
    # Calculate efficiency metrics
    eficiencia = energia / 1000  # Simplified metric
    
    if energia > 40000:
        recommendations.append({
            "id": "AI-1",
            "sede": sede,
            "sector": "Laboratorios",
            "tipo": "eficiencia",
            "descripcion": f"Implementar sistema de gestión energética en laboratorios. Consumo actual ({energia:.0f} kWh) está 15% por encima del benchmark. Instalar sensores de ocupación y automatizar apagado de equipos nocturno.",
            "ahorro_estimado": int(energia * 0.15),
            "prioridad": "alta",
            "estado": "pendiente"
        })
    
    if agua > 8000:
        recommendations.append({
            "id": "AI-2",
            "sede": sede,
            "sector": "Comedores",
            "tipo": "agua",
            "descripcion": f"Optimizar sistema de agua en comedores. Detectado consumo elevado ({agua:.0f} m³). Instalar válvulas automáticas y sensores de flujo para detectar fugas.",
            "ahorro_estimado": int(agua * 0.12),
            "prioridad": "media",
            "estado": "pendiente"
        })
    
    if co2 > 60:
        recommendations.append({
            "id": "AI-3",
            "sede": sede,
            "sector": "HVAC",
            "tipo": "climatizacion",
            "descripcion": f"Actualizar sistema HVAC para reducir emisiones de CO2 ({co2:.1f} ton/mes). Considerar mantenimiento predictivo y ajuste de termostatos inteligentes.",
            "ahorro_estimado": int(co2 * 10),
            "prioridad": "alta",
            "estado": "pendiente"
        })
    
    if anomalias > 3:
        recommendations.append({
            "id": "AI-4",
            "sede": sede,
            "sector": "General",
            "tipo": "monitoreo",
            "descripcion": f"Priorizar resolución de {anomalias} anomalías activas detectadas. Implementar protocolo de respuesta rápida para alertas críticas.",
            "ahorro_estimado": 200,
            "prioridad": "alta",
            "estado": "pendiente"
        })
    
    # Always add at least one general recommendation
    if not recommendations:
        recommendations.append({
            "id": "AI-1",
            "sede": sede,
            "sector": "General",
            "tipo": "optimizacion",
            "descripcion": f"Mantener monitoreo continuo del consumo energético. Los indicadores actuales son estables. Programar auditoría energética trimestral.",
            "ahorro_estimado": 100,
            "prioridad": "baja",
            "estado": "pendiente"
        })
    
    return recommendations
