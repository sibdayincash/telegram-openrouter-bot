import os
import httpx
import logging

# Настройка логгирования
logger = logging.getLogger(__name__)

# Получаем ключ из переменных окружения, который должен быть установлен при запуске основного скрипта.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def _call_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Универсальная функция для вызова API OpenRouter.
    """
    if not OPENROUTER_API_KEY:
        # Эта проверка на случай, если модуль используется отдельно.
        # Основной скрипт уже проверяет наличие ключа при старте.
        raise ValueError("Ключ OpenRouter API не найден в переменных окружения.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120.0
            )
            response.raise_for_status()
            result = response.json()

        reply = result["choices"][0]["message"]["content"]
        return reply.strip()

    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenRouter: {e}")
        # Возвращаем пустую строку или ошибку, чтобы вызывающий код мог это обработать
        return f"Ошибка API: {e}"


async def translate_text(text_to_translate: str) -> str:
    """
    Переводит текст с хакасского на русский.
    """
    logger.info("Начинаю перевод текста...")
    system_prompt = "Ты — профессиональный переводчик, который переводит с хакасского языка на русский. Переведи предоставленный текст целиком, сохраняя смысл и структуру. Не добавляй никаких комментариев или вводных фраз, просто дай чистый перевод."
    user_prompt = f"Переведи этот текст с хакасского на русский: \n\n{text_to_translate}"

    translated_text = await _call_openrouter(system_prompt, user_prompt)
    logger.info("Перевод завершен.")
    return translated_text


async def rewrite_text(text_to_rewrite: str) -> str:
    """
    Делает рерайтинг русского текста, чтобы он стал более уникальным.
    """
    logger.info("Начинаю рерайтинг текста...")
    system_prompt = "Ты — профессиональный редактор и копирайтер. Твоя задача — переписать (сделать рерайт) предоставленный новостной текст. Сохрани основной смысл, факты, имена и цифры, но изложи их другими словами, чтобы текст стал уникальным. Говори только переписанным текстом, без вступлений."
    user_prompt = f"Сделай рерайт этого текста: \n\n{text_to_rewrite}"

    rewritten_text = await _call_openrouter(system_prompt, user_prompt)
    logger.info("Рерайтинг завершен.")
    return rewritten_text
