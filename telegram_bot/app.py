"""Copied bot entrypoint now available at repo root `telegram_bot` folder.
This is functionally identical to `backend/telegram_bot/app.py`.
"""
import os
import logging
from typing import Dict, List
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def sync_call():
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
    await update.message.reply_text(
        "Comandos:\n/start - saludo\n/help - esta ayuda\n" 
        "También puedes enviar preguntas en texto sobre el proyecto."
    )


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
    reply_text = await call_chatgpt(prompt)
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
        logger.error("Environment variable TELEGRAM_BOT_TOKEN is not set.")
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and retry.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("saludar", saludar))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
