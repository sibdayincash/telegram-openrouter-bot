import os
import logging
import httpx
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("7563880680:AAFpM3h7QXmOVtKdWv5aGYDj-J_C61JXp9o")
OPENROUTER_API_KEY = os.getenv("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")

if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Переменные окружения TELEGRAM_BOT_TOKEN и/или OPENROUTER_API_KEY не установлены!")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я бот-помощник по изучению хакасского языка. Задай мне вопрос!")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"Запрос от пользователя: {user_input}")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Ты — доброжелательный преподаватель хакасского языка."},
                {"role": "user", "content": user_input}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

        reply = result["choices"][0]["message"]["content"]
        await context.bot.send_message(chat_id=chat_id, text=reply)

    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenRouter: {e}")
        await context.bot.send_message(chat_id=chat_id, text="❌ Произошла ошибка при обработке запроса.")

# Основной запуск
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    await application.bot.delete_webhook(drop_pending_updates=True)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())