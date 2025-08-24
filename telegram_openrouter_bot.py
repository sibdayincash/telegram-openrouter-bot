import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# Импортируем наши новые модули
import ai_processing
import news_scraper

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Ключи API ---
# ВАЖНО: При развертывании проекта на сервере (Render и т.д.)
# эти ключи нужно устанавливать как переменные окружения, а не хранить в коде.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7563880680:AAFpM3h7QXmOVtKdWv5aGYDj-J_C61JXp9o")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден токен для Telegram. Установите переменную окружения TELEGRAM_BOT_TOKEN.")
if not OPENROUTER_API_KEY:
    raise ValueError("Не найден ключ для OpenRouter. Установите переменную окружения OPENROUTER_API_KEY.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение и инструкцию."""
    start_message = """
👋 **Привет! Я бот для обработки новостей.**

Я могу взять статью с сайта на хакасском языке, перевести ее на русский, а затем сделать уникальный рерайт.

**Как использовать:**
Отправьте мне команду в формате:
`/news [URL статьи]`

**Пример:**
`/news https://www.khakaschiry.ru/news/detail.php?ID=14222`
    """
    await update.message.reply_text(start_message, parse_mode=ParseMode.MARKDOWN)


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /news, выполняя весь пайплайн."""
    chat_id = update.effective_chat.id

    # Проверяем, что URL был предоставлен
    if not context.args:
        await context.bot.send_message(chat_id=chat_id, text="Пожалуйста, укажите URL статьи после команды. \nПример: `/news https://...`")
        return

    url = context.args[0]
    logger.info(f"Получена команда /news с URL: {url}")

    await context.bot.send_message(chat_id=chat_id, text="✅ Принято! Начинаю обработку статьи. Это может занять несколько минут...")

    # Шаг 1: Сбор данных со страницы
    try:
        scraped_data = await news_scraper.scrape_article(url)
        if not scraped_data:
            await context.bot.send_message(chat_id=chat_id, text="❌ Не удалось получить данные со страницы. Проверьте ссылку или попробуйте позже.")
            return
    except Exception as e:
        logger.error(f"Ошибка на этапе скрапинга: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Произошла ошибка при сборе данных: {e}")
        return

    await context.bot.send_message(chat_id=chat_id, text="📰 Статья успешно собрана. Начинаю перевод...")

    # Шаг 2: Перевод текста
    try:
        translated_text = await ai_processing.translate_text(scraped_data["body"])
        if "Ошибка API" in translated_text:
             await context.bot.send_message(chat_id=chat_id, text=f"❌ {translated_text}")
             return
    except Exception as e:
        logger.error(f"Ошибка на этапе перевода: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Произошла ошибка при переводе: {e}")
        return

    await context.bot.send_message(chat_id=chat_id, text="🔄 Перевод готов. Начинаю рерайтинг...")

    # Шаг 3: Рерайтинг текста
    try:
        rewritten_text = await ai_processing.rewrite_text(translated_text)
        if "Ошибка API" in rewritten_text:
             await context.bot.send_message(chat_id=chat_id, text=f"❌ {rewritten_text}")
             return
    except Exception as e:
        logger.error(f"Ошибка на этапе рерайтинга: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Произошла ошибка при рерайтинге: {e}")
        return

    # Шаг 4: Отправка результата
    final_caption = f"**{scraped_data['title']}**\n\n{rewritten_text}"

    try:
        if scraped_data.get("image_url"):
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=scraped_data["image_url"],
                caption=final_caption,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=final_caption,
                parse_mode=ParseMode.MARKDOWN
            )
        logger.info("Результат успешно отправлен пользователю.")
    except Exception as e:
        logger.error(f"Ошибка при отправке результата: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Произошла ошибка при отправке сообщения: {e}")


def main():
    """Основной запуск бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Удаляем вебхук, если он был
    # asyncio.run(application.bot.delete_webhook(drop_pending_updates=True))

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("news", news_command))

    logger.info("✅ Бот запущен и готов принимать команды /news.")

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()