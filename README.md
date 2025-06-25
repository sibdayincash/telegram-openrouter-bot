# Telegram OpenRouter Bot

Этот бот отвечает на вопросы пользователей с помощью GPT-3.5 через OpenRouter.

## 🚀 Запуск локально

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Установи переменные окружения:
- `TELEGRAM_BOT_TOKEN`
- `OPENROUTER_API_KEY`

3. Запусти бота:
```bash
python telegram_openrouter_bot.py
```

## ☁️ Развёртывание на Render

1. Создай репозиторий на GitHub
2. Залей туда эти файлы
3. Перейди на [https://render.com](https://render.com), создай Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_openrouter_bot.py`
   - Environment Variables:
     - `TELEGRAM_BOT_TOKEN`
     - `OPENROUTER_API_KEY`

Готово!