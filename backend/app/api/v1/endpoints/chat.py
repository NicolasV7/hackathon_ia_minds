"""
AI Chat endpoint using OpenAI.
Provides intelligent assistant for energy efficiency questions.
"""

import logging
import os
from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# System prompt for the AI assistant
SYSTEM_PROMPT = """Eres EcoBot, el asistente de inteligencia artificial de UPTC EcoEnergy, 
un sistema de monitoreo de eficiencia energética para la Universidad Pedagógica y Tecnológica de Colombia.

Tu rol es ayudar a los usuarios con:
1. Información sobre consumo energético y de agua en las sedes de la UPTC
2. Explicación de predicciones de CO2 y energía
3. Recomendaciones para mejorar la eficiencia energética
4. Interpretación de anomalías detectadas
5. Información sobre las sedes: Tunja (principal), Duitama, Sogamoso y Chiquinquirá

Datos clave de la UPTC:
- Sede Tunja: 18,000 estudiantes, consumo promedio 45,000 kWh/mes
- Sede Duitama: 5,500 estudiantes, consumo promedio 18,200 kWh/mes
- Sede Sogamoso: 6,000 estudiantes, consumo promedio 15,500 kWh/mes
- Sede Chiquinquirá: 2,000 estudiantes, consumo promedio 6,800 kWh/mes

Modelos de ML activos:
- LightGBM para predicción de CO2 (R² = 0.893)
- Ridge Regression para predicción de energía (R² = 0.998)

Responde siempre en español, de forma concisa y profesional.
Si no tienes información específica, sugiere consultar los dashboards o contactar al equipo técnico."""


@router.post("")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI assistant.
    
    Args:
        request: Chat request with user message
        
    Returns:
        AI-generated response
    """
    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai_key:
            # Return a helpful response without OpenAI
            return ChatResponse(
                response=get_fallback_response(request.message)
            )
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": request.message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return ChatResponse(
                response=completion.choices[0].message.content
            )
            
        except ImportError:
            logger.warning("OpenAI library not installed")
            return ChatResponse(
                response=get_fallback_response(request.message)
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ChatResponse(
                response=get_fallback_response(request.message)
            )
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_fallback_response(message: str) -> str:
    """Generate a helpful response without OpenAI."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hola", "buenos", "saludos", "hey"]):
        return "¡Hola! Soy EcoBot, tu asistente de eficiencia energética de la UPTC. ¿En qué puedo ayudarte hoy? Puedo informarte sobre consumo energético, predicciones de CO2, o recomendaciones de ahorro."
    
    if any(word in message_lower for word in ["consumo", "energía", "energia", "kwh"]):
        return """El consumo energético actual de las sedes UPTC es:
        
• Tunja (Principal): ~45,000 kWh/mes
• Duitama: ~18,200 kWh/mes  
• Sogamoso: ~15,500 kWh/mes
• Chiquinquirá: ~6,800 kWh/mes

Los laboratorios y sistemas de climatización representan el mayor consumo. 
Consulta el dashboard de Analytics para ver tendencias detalladas."""
    
    if any(word in message_lower for word in ["co2", "carbono", "emisiones"]):
        return """Las emisiones de CO2 se calculan a partir del consumo energético usando nuestro modelo LightGBM (R² = 0.893).

Emisiones actuales estimadas:
• Tunja: ~68.5 toneladas CO2/mes
• Duitama: ~27.3 toneladas CO2/mes
• Sogamoso: ~23.2 toneladas CO2/mes
• Chiquinquirá: ~10.2 toneladas CO2/mes

El dashboard de Modelos muestra las predicciones en tiempo real."""
    
    if any(word in message_lower for word in ["ahorro", "reducir", "eficiencia", "recomendación"]):
        return """Principales recomendaciones para mejorar la eficiencia energética:

1. **Climatización inteligente**: Instalar sensores de ocupación (ahorro potencial: 15%)
2. **Iluminación LED**: Reemplazar luminarias tradicionales (ahorro: 40% en iluminación)
3. **Horarios optimizados**: Reducir consumo en horas no académicas
4. **Paneles solares**: Considerar instalación en techos disponibles

Visita la página de Balances para ver el análisis detallado de oportunidades de ahorro."""
    
    if any(word in message_lower for word in ["sede", "tunja", "duitama", "sogamoso", "chiquinquira"]):
        return """Información de las sedes UPTC:

**Tunja (Principal)**
- 18,000 estudiantes
- 28 edificios, 125,000 m²
- Mayor consumo en laboratorios

**Duitama**
- 5,500 estudiantes
- 12 edificios, 45,000 m²
- Enfoque en ingeniería

**Sogamoso**
- 6,000 estudiantes
- 10 edificios, 38,000 m²
- Incluye talleres industriales

**Chiquinquirá**
- 2,000 estudiantes
- 5 edificios, 15,000 m²
- Campus más eficiente por estudiante"""
    
    if any(word in message_lower for word in ["modelo", "predicción", "ml", "inteligencia"]):
        return """Nuestro sistema usa dos modelos de Machine Learning:

**1. Modelo CO2 (LightGBM)**
- R² Score: 0.893
- MAE: 0.153
- Predice emisiones de carbono

**2. Modelo Energía (Ridge Regression)**
- R² Score: 0.998
- MAE: 0.014
- Predice consumo total de energía

Los modelos se entrenan con datos históricos de consumo, temperatura, ocupación y calendario académico. Visita la página de Explicabilidad para entender cómo funcionan."""
    
    # Default response
    return """Gracias por tu mensaje. Como EcoBot, puedo ayudarte con:

• **Consumo energético**: Datos de las 4 sedes UPTC
• **Predicciones**: Explicación de modelos de CO2 y energía
• **Recomendaciones**: Sugerencias de ahorro energético
• **Anomalías**: Interpretación de alertas detectadas

¿Sobre qué tema te gustaría saber más? También puedes explorar los dashboards para información detallada en tiempo real."""
