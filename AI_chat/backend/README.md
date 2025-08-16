# AI Chat Backend

## Основные файлы:

### 🚀 Запуск приложений:
- `main.py` - Основной AI чат бот API (FastAPI + Gemini)
- `x402_hello_agent.py` - x402 совместимый агент для демо

### 🔧 Утилиты:
- `coinbase_client.py` - Клиент для Coinbase CDP API
- `test_coinbase.py` - Тесты Coinbase API
- `test_x402_agent.py` - Тесты x402 агента

### 🤖 Промпты:
- `prompts/` - Системные промпты для AI

### 📦 Деплой:
- `Dockerfile` - Контейнер для деплоя
- `railway.json` - Конфиг для Railway
- `render.yaml` - Конфиг для Render
- `requirements.txt` - Python зависимости

## Быстрый старт:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск AI чата
python main.py

# Запуск x402 агента  
python x402_hello_agent.py
```

## Переменные окружения:
- `GEMINI_API_KEY` - API ключ Google Gemini
- `CDP_API_KEY_NAME` - Coinbase CDP API Key
- `CDP_PRIVATE_KEY` - Coinbase CDP Private Key