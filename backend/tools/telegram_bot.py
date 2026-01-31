"""Telegram bot to answer questions about the project objective.

Minimal, self-contained script using python-telegram-bot v20+ (async).

Usage:
1. Set environment variable `TELEGRAM_BOT_TOKEN` with your bot token.
2. Run: `python -m backend.tools.telegram_bot` (or `python backend/tools/telegram_bot.py`).

The bot replies using a small built-in knowledge base. Later we can extend
it to call the project backend or an LLM for richer answers.
"""
import os
import asyncio
import logging
from typing import Dict

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KNOWLEDGE_BASE: Dict[str, str] = {
    "objetivo": (
        "El proyecto es un sistema para monitorizar y optimizar la eficiencia energética "
        "de la UPTC: medir consumo, detectar anomalías, predecir consumo horario y generar "
        "recomendaciones de ahorro e implementación."
    ),
    "ml": (
        "La parte de ML carga modelos serializados (joblib) en `backend/ml_models`:\n"
        "- `energy_predictor.joblib`: modelo de predicción de consumo\n"
        "- `anomaly_detector.joblib`: detector de anomalías.\n"
        "El servicio `backend/app/ml/inference.py` expone funciones para predecir y detectar." 
    ),
    "api": (
        "El backend es FastAPI. Endpoints principales en `/api/v1` para analytics, anomalies, "
        "predictions y recommendations. Frontend (Next.js) consume esos endpoints."
    ),
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola — soy el bot del proyecto EcoEnergy. Pregúntame sobre el objetivo, ML o API.\n"
        "Ejemplos: '¿Cuál es el objetivo?', 'ml', 'api'"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Comandos:\n/start - saludo\n/help - esta ayuda\n" 
        "También puedes enviar preguntas en texto sobre el proyecto."
    )


def find_answer(text: str) -> str:
    """Very small matcher against KNOWLEDGE_BASE keys."""
    if not text:
        return "No entendí la pregunta. Escribe 'objetivo', 'ml' o 'api'."

    text_lower = text.lower()
    # direct key match
    for key in KNOWLEDGE_BASE:
        if key in text_lower:
            return KNOWLEDGE_BASE[key]

    # fallback
    return (
        "Puedo responder sobre el objetivo, ML y la API del proyecto. "
        "Escribe 'objetivo', 'ml' o 'api', o dime qué aspecto quieres que explique."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    answer = find_answer(text)
    await update.message.reply_text(answer)


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Environment variable TELEGRAM_BOT_TOKEN is not set.")
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and retry.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
