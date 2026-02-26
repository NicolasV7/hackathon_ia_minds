"""Telegram Bot for UPTC EcoEnergy - Energy Analytics Assistant.

Commands:
- /start - Welcome message
- /help - Show available commands
- /menu - Quick options menu
- /consumo [sede] - Get current consumption
- /prediccion [sede] [horas] - Get consumption prediction
- /anomalias [sede] - Get recent anomalies
- /recomendaciones [sede] - Get recommendations
"""
import os
import logging
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

import httpx
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

# Sedes configuration
SEDES = ["Tunja", "Duitama", "Sogamoso", "Chiquinquirá"]


KNOWLEDGE_BASE: Dict[str, str] = {
    "objetivo": (
        "El proyecto es un sistema para monitorizar y optimizar la eficiencia energética "
        "de la UPTC: medir consumo, detectar anomalías, predecir consumo horario y generar "
        "recomendaciones de ahorro e implementación."
    ),
    "ahorro": (
        "Recomendaciones rápidas para ahorrar energía en edificios: \n"
        "1. Programar HVAC según ocupación y horarios.\n"
        "2. Sustituir iluminación por LED y usar sensores de presencia.\n"
        "3. Mantener preventivamente equipos eléctricos.\n"
        "4. Evitar equipos funcionando 24/7; usar programación y apagado automático.\n"
        "5. Mostrar indicadores de consumo para sensibilizar usuarios."
    ),
    "implementacion": (
        "Plan de implementación de medidas de eficiencia: \n"
        "1. Auditoría energética para identificar prioridades.\n"
        "2. Priorizar acciones por ROI y facilidad de ejecución.\n"
        "3. Desplegar sensores/telemetría para monitorización continua.\n"
        "4. Integrar predicciones para planificar cargas y horarios.\n"
        "5. Medir impacto (kWh ahorrado, reducción picos) y ajustar."
    ),
    "datos": (
        "Datos curiosos sobre energía: \n"
        "- La iluminación LED puede consumir hasta 80% menos que la incandescente.\n"
        "- Muchos edificios pierden 20-30% de energía por ineficiencias.\n"
        "- La gestión de demanda reduce costes evitando picos de consumo.\n"
        "- Apagar equipos no usados reduce consumo significativamente.\n"
        "- La eficiencia energética también reduce emisiones de CO2."
    ),
    "como_reducir_factura": (
        "Cómo reducir la factura eléctrica: \n"
        "- Revisar tarifas y desplazar cargas a tramos más baratos.\n"
        "- Mejorar la eficiencia de equipos y control horario.\n"
        "- Implementar controles automáticos para reducir standby.\n"
        "- Monitorizar consumos por área para detectar fugas."
    ),
    "horario_hvac": (
        "Mejores prácticas de horarios para HVAC: \n"
        "- Programar encendidos 30–60 min antes de ocupación.\n"
        "- Bajar setpoints fuera de horario y usar setbacks nocturnos.\n"
        "- Integrar ocupación y condiciones climáticas para optimizar."
    ),
    "tips_estudiantes": (
        "Consejos para estudiantes: \n"
        "- Apagar luces y equipos al salir.\n"
        "- Usar cargadores con temporizador o enchufes inteligentes.\n"
        "- Reportar equipos dañados que consumen más de lo normal.\n"
        "- Participar en campañas de ahorro y retos de consumo."
    ),
    "mensaje_bonito": (
        "✨ Gracias por preocuparte por el planeta. Cada pequeño gesto cuenta: apaga una luz hoy y haz la diferencia. ✨"
    ),
}


def build_system_prompt() -> List[Dict[str, str]]:
    project_context = (
        "Eres un asistente que responde preguntas sobre el proyecto UPTC EcoEnergy. "
        "El objetivo del proyecto es monitorizar y optimizar la eficiencia energética: "
        "medir consumo, detectar anomalías, predecir consumo horario y generar recomendaciones "
        "de ahorro e implementación. Cuando el usuario no provea contexto, responde de forma "
        "clara y concisa y pide más datos si necesita información adicional."
    )

    instructions = (
        "Si la pregunta es estrictamente técnica o solicita rutas/archivos del repo, responde con "
        "referencias concretas a los archivos del repositorio (p. ej. backend/app/ml/inference.py). "
        "Si el API key de OpenAI no está disponible, responde usando una respuesta local corta."
    )

    return [
        {"role": "system", "content": project_context + "\n" + instructions}
    ]


async def call_chatgpt(user_text: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set; using local fallback knowledge base.")
        lower = user_text.lower()
        for k, v in KNOWLEDGE_BASE.items():
            if k in lower:
                return v
        return (
            "Puedo responder sobre el objetivo del proyecto. Escribe 'objetivo' o proporciona más contexto."
        )

    openai.api_key = api_key

    messages = build_system_prompt()
    messages.append({"role": "user", "content": user_text})

    model_name = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    def sync_call():
        try:
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Lo siento, hubo un error contactando al servicio de ChatGPT."

    return await asyncio.to_thread(sync_call)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola — soy el bot del proyecto EcoEnergy. Pregúntame sobre el objetivo, ML o API.\n"
        "Ejemplos: '¿Cuál es el objetivo?', '¿Cómo funcionan las predicciones?'"
    )
    keyboard = [
        [
            InlineKeyboardButton("Ahorro", callback_data="ahorro"),
            InlineKeyboardButton("Implementación", callback_data="implementacion"),
            InlineKeyboardButton("Datos curiosos", callback_data="datos"),
        ],
        [
            InlineKeyboardButton("¿Cómo reducir factura?", callback_data="como_reducir_factura"),
            InlineKeyboardButton("Horario HVAC", callback_data="horario_hvac"),
            InlineKeyboardButton("Tips estudiantes", callback_data="tips_estudiantes"),
        ],
        [
            InlineKeyboardButton("Mensaje bonito", callback_data="mensaje_bonito"),
        ],
    ]
    await update.message.reply_text("Selecciona una pregunta rápida:", reply_markup=InlineKeyboardMarkup(keyboard))


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🤖 *Comandos disponibles:*\n\n"
        "📊 *Consumo y Datos*\n"
        "• /consumo [sede] - Ver consumo actual\n"
        "  Ejemplo: `/consumo Tunja`\n\n"
        "🔮 *Predicciones*\n"
        "• /prediccion [sede] [horas] - Predicción de consumo\n"
        "  Ejemplo: `/prediccion Tunja 24`\n\n"
        "⚠️ *Anomalías*\n"
        "• /anomalias [sede] - Ver anomalías recientes\n"
        "  Ejemplo: `/anomalias Duitama`\n\n"
        "💡 *Recomendaciones*\n"
        "• /recomendaciones [sede] - Ver recomendaciones\n"
        "  Ejemplo: `/recomendaciones Sogamoso`\n\n"
        "📝 *General*\n"
        "• /menu - Menú de opciones rápidas\n"
        "• /start - Iniciar el bot\n\n"
        "También puedes enviar preguntas en texto sobre el proyecto."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def saludar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("hoolisss estrellitas")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Ahorro", callback_data="ahorro"),
            InlineKeyboardButton("Implementación", callback_data="implementacion"),
            InlineKeyboardButton("Datos curiosos", callback_data="datos"),
        ],
        [
            InlineKeyboardButton("¿Cómo reducir factura?", callback_data="como_reducir_factura"),
            InlineKeyboardButton("Horario HVAC", callback_data="horario_hvac"),
            InlineKeyboardButton("Tips estudiantes", callback_data="tips_estudiantes"),
        ],
        [
            InlineKeyboardButton("Mensaje bonito", callback_data="mensaje_bonito"),
        ],
    ]
    await update.message.reply_text("Selecciona una pregunta:", reply_markup=InlineKeyboardMarkup(keyboard))


def get_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Ahorro", callback_data="ahorro"),
            InlineKeyboardButton("Implementación", callback_data="implementacion"),
            InlineKeyboardButton("Datos curiosos", callback_data="datos"),
        ],
        [
            InlineKeyboardButton("¿Cómo reducir factura?", callback_data="como_reducir_factura"),
            InlineKeyboardButton("Horario HVAC", callback_data="horario_hvac"),
            InlineKeyboardButton("Tips estudiantes", callback_data="tips_estudiantes"),
        ],
        [
            InlineKeyboardButton("Mensaje bonito", callback_data="mensaje_bonito"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


PROMPT_MAP = {
    "objetivo": "¿Cuál es el objetivo del proyecto UPTC EcoEnergy?",
    "ml": "Explica brevemente la parte de ML del proyecto y dónde están los modelos.",
    "api": "Explica brevemente la arquitectura de la API y los endpoints principales.",
    "ahorro": "Dame 5 recomendaciones prácticas para ahorrar energía en edificios universitarios, enfocadas en consumo eléctrico y HVAC.",
    "implementacion": "Describe un plan paso a paso para implementar medidas de eficiencia energética en un campus universitario, con prioridades y métricas de éxito.",
    "datos": "Comparte 5 datos curiosos y relevantes sobre energía y eficiencia energética para concienciación.",
    "como_reducir_factura": "¿Qué acciones concretas puede tomar una universidad para reducir su factura eléctrica y desplazar cargas a tramos económicos?",
    "horario_hvac": "¿Cuáles son las mejores prácticas para programar HVAC según ocupación y clima?",
    "tips_estudiantes": "5 consejos simples para que estudiantes ahorren energía en residencias y aulas.",
    "mensaje_bonito": "Devuelve un breve mensaje amable y motivador sobre cuidado energético.",
}


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    if data == "saludar":
        await query.edit_message_text("hoolisss estrellitas")
        return

    # If we have a local canned answer, use it immediately (works without OpenAI key)
    if data in KNOWLEDGE_BASE:
        await query.edit_message_text(KNOWLEDGE_BASE[data])
        return

    prompt = PROMPT_MAP.get(data, data)
    if prompt:
        reply_text = await call_chatgpt(prompt)
    else:
        reply_text = "No entendí tu solicitud. Por favor, selecciona una opción del menú."
    await query.edit_message_text(reply_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("No entendí tu mensaje.")
        return

    await update.message.chat.send_action(action="typing")
    answer = await call_chatgpt(text)
    await update.message.reply_text(answer, reply_markup=get_menu_markup())


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Bot is idle. Set the token and restart to activate.")
        # Stay alive without doing anything (avoids container restart loops)
        import time
        while True:
            time.sleep(3600)

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("saludar", saludar))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add new energy analytics commands
    app.add_handler(CommandHandler("consumo", consumo_cmd))
    app.add_handler(CommandHandler("prediccion", prediccion_cmd))
    app.add_handler(CommandHandler("anomalias", anomalias_cmd))
    app.add_handler(CommandHandler("recomendaciones", recomendaciones_cmd))

    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()


async def consumo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current consumption for a sede."""
    args = context.args
    sede = args[0] if args else None
    
    if not sede:
        # Show sede selection
        keyboard = [[InlineKeyboardButton(s, callback_data=f"consumo_{s}")] for s in SEDES]
        await update.message.reply_text(
            "Selecciona una sede para ver el consumo:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if sede not in SEDES:
        await update.message.reply_text(
            f"Sede '{sede}' no válida. Sedes disponibles: {', '.join(SEDES)}"
        )
        return
    
    await update.message.chat.send_action(action="typing")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/analytics/dashboard",
                params={"sede": sede, "days": 1}
            )
            
            if response.status_code == 200:
                data = response.json()
                message = (
                    f"📊 *Consumo Actual - {sede}*\n\n"
                    f"⚡ Energía Total: {data.get('total_consumption_kwh', 'N/A')} kWh\n"
                    f"💧 Agua: {data.get('total_water_m3', 'N/A')} m³\n"
                    f"🌡️ Temperatura Promedio: {data.get('avg_temperature', 'N/A')}°C\n"
                    f"👥 Ocupación: {data.get('avg_occupancy', 'N/A')}%\n\n"
                    f"📈 Puntuación de Eficiencia: {data.get('efficiency_score', 'N/A')}/100"
                )
                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    "No se pudo obtener el consumo actual. Intenta más tarde."
                )
    except Exception as e:
        logger.error(f"Error fetching consumption: {e}")
        await update.message.reply_text(
            "Error al conectar con el servidor. Verifica que el API esté disponible."
        )


async def prediccion_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get consumption prediction for a sede."""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Uso: /prediccion [sede] [horas]\n"
            "Ejemplo: /prediccion Tunja 24"
        )
        return
    
    sede = args[0]
    horas = int(args[1]) if len(args) > 1 else 24
    
    if sede not in SEDES:
        await update.message.reply_text(
            f"Sede '{sede}' no válida. Sedes disponibles: {', '.join(SEDES)}"
        )
        return
    
    if horas < 1 or horas > 168:
        await update.message.reply_text(
            "El horizonte de predicción debe estar entre 1 y 168 horas."
        )
        return
    
    await update.message.chat.send_action(action="typing")
    
    try:
        async with httpx.AsyncClient() as client:
            # Create prediction
            start_time = datetime.now().isoformat()
            response = await client.post(
                f"{API_BASE_URL}/predictions/batch",
                json={
                    "sede": sede,
                    "start_timestamp": start_time,
                    "horizon_hours": horas
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                
                if predictions:
                    total_predicted = sum(p.get("energia_total_kwh", 0) for p in predictions)
                    avg_confidence = sum(p.get("confidence", 0) for p in predictions) / len(predictions)
                    
                    message = (
                        f"🔮 *Predicción - {sede} ({horas}h)*\n\n"
                        f"⚡ Consumo Total Previsto: {total_predicted:.2f} kWh\n"
                        f"📊 Promedio Horario: {total_predicted/horas:.2f} kWh/h\n"
                        f"🎯 Confianza Promedio: {avg_confidence*100:.1f}%\n\n"
                        f"_Las predicciones se actualizan automáticamente cada hora._"
                    )
                    await update.message.reply_text(message, parse_mode="Markdown")
                else:
                    await update.message.reply_text(
                        "No se generaron predicciones. Intenta más tarde."
                    )
            else:
                await update.message.reply_text(
                    "No se pudo generar la predicción. Intenta más tarde."
                )
    except Exception as e:
        logger.error(f"Error creating prediction: {e}")
        await update.message.reply_text(
            "Error al conectar con el servidor. Verifica que el API esté disponible."
        )


async def anomalias_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get recent anomalies for a sede."""
    args = context.args
    sede = args[0] if args else None
    
    if not sede:
        # Show sede selection
        keyboard = [[InlineKeyboardButton(s, callback_data=f"anomalias_{s}")] for s in SEDES]
        await update.message.reply_text(
            "Selecciona una sede para ver anomalías:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if sede not in SEDES:
        await update.message.reply_text(
            f"Sede '{sede}' no válida. Sedes disponibles: {', '.join(SEDES)}"
        )
        return
    
    await update.message.chat.send_action(action="typing")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/anomalies",
                params={"sede": sede, "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get("items", [])
                
                if anomalies:
                    message = f"⚠️ *Anomalías Recientes - {sede}*\n\n"
                    for i, anomaly in enumerate(anomalies[:5], 1):
                        severity_emoji = {
                            "critical": "🔴",
                            "high": "🟠",
                            "medium": "🟡",
                            "low": "🔵"
                        }.get(anomaly.get("severity"), "⚪")
                        
                        message += (
                            f"{i}. {severity_emoji} *{anomaly.get('anomaly_type', 'Desconocido')}*\n"
                            f"   Sector: {anomaly.get('sector', 'N/A')}\n"
                            f"   Severidad: {anomaly.get('severity', 'N/A')}\n"
                            f"   Valor: {anomaly.get('actual_value', 'N/A')} kWh\n"
                            f"   _{anomaly.get('description', 'Sin descripción')[:100]}..._\n\n"
                        )
                    
                    message += f"_Mostrando {len(anomalies[:5])} de {len(anomalies)} anomalías_"
                    await update.message.reply_text(message, parse_mode="Markdown")
                else:
                    await update.message.reply_text(
                        f"✅ No se encontraron anomalías recientes en {sede}."
                    )
            else:
                await update.message.reply_text(
                    "No se pudieron obtener las anomalías. Intenta más tarde."
                )
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        await update.message.reply_text(
            "Error al conectar con el servidor. Verifica que el API esté disponible."
        )


async def recomendaciones_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get recommendations for a sede."""
    args = context.args
    sede = args[0] if args else None
    
    if not sede:
        # Show sede selection
        keyboard = [[InlineKeyboardButton(s, callback_data=f"recomendaciones_{s}")] for s in SEDES]
        await update.message.reply_text(
            "Selecciona una sede para ver recomendaciones:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if sede not in SEDES:
        await update.message.reply_text(
            f"Sede '{sede}' no válida. Sedes disponibles: {', '.join(SEDES)}"
        )
        return
    
    await update.message.chat.send_action(action="typing")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/recommendations",
                params={"sede": sede, "status": "pending", "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data if isinstance(data, list) else data.get("items", [])
                
                if recommendations:
                    message = f"💡 *Recomendaciones - {sede}*\n\n"
                    for i, rec in enumerate(recommendations[:5], 1):
                        priority_emoji = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(rec.get("priority"), "⚪")
                        
                        savings = rec.get('potential_savings_kwh', 0)
                        savings_text = f"💰 Ahorro potencial: {savings:.2f} kWh\n" if savings else ""
                        
                        message += (
                            f"{i}. {priority_emoji} *{rec.get('title', 'Sin título')}*\n"
                            f"   {savings_text}"
                            f"   _{rec.get('description', 'Sin descripción')[:100]}..._\n\n"
                        )
                    
                    await update.message.reply_text(message, parse_mode="Markdown")
                else:
                    await update.message.reply_text(
                        f"✅ No hay recomendaciones pendientes para {sede}."
                    )
            else:
                await update.message.reply_text(
                    "No se pudieron obtener las recomendaciones. Intenta más tarde."
                )
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        await update.message.reply_text(
            "Error al conectar con el servidor. Verifica que el API esté disponible."
        )



