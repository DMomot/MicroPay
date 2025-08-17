# 🚀 Быстрый запуск MicroPay

## Статус окружения ✅

- ✅ **Фронтенд**: Запущен на http://localhost:3000
- ✅ **Бэкенд**: Запущен на http://localhost:8000
- ✅ **MetaMask интеграция**: Настроена и работает

## Как запустить с нуля

### 1. Бэкенд (AI Chat API)

```bash
# Переход в директорию бэкенда
cd AI_chat/backend

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python main.py
```

**Бэкенд будет доступен на**: http://localhost:8000

### 2. Фронтенд (React + MetaMask)

```bash
# Переход в директорию фронтенда
cd AI_chat/frontend

# Установка зависимостей
npm install --legacy-peer-deps

# Запуск
npm start
```

**Фронтенд будет доступен на**: http://localhost:3000

## Функциональность

### AI Chat
- Чат с AI ботом на основе Gemini
- Простой и красивый интерфейс
- Обработка ошибок

### MetaMask интеграция
- Подключение Web3 кошельков
- Поддержка MetaMask, WalletConnect
- Отображение адреса кошелька
- Поддержка ENS имён
- Мультисеть (Ethereum, Polygon, Optimism, Arbitrum)

## Проверка работы

1. Откройте http://localhost:3000
2. Увидите AI чат с кнопками подключения кошелька в хедере
3. Нажмите "MetaMask" для подключения кошелька
4. Попробуйте отправить сообщение AI боту

## Остановка сервисов

```bash
# Остановить фронтенд: Ctrl+C в терминале с npm start
# Остановить бэкенд: Ctrl+C в терминале с python main.py
```

## Файлы проекта

```
ScoutPay/
├── AI_chat/
│   ├── backend/          # FastAPI + Gemini AI
│   │   ├── main.py       # Основной API сервер
│   │   ├── requirements.txt
│   │   └── venv/         # Виртуальное окружение Python
│   │
│   └── frontend/         # React + MetaMask
│       ├── src/
│       │   ├── App.tsx           # Главный компонент
│       │   ├── WalletConnection.tsx  # Подключение кошелька
│       │   ├── wagmi.ts          # Конфиг Web3
│       │   └── index.tsx         # Точка входа
│       └── package.json
│
└── price_agent/          # Другие компоненты проекта
```

## Ошибки и решения

### "ModuleNotFoundError: No module named 'fastapi'"
**Решение**: Активируйте виртуальное окружение:
```bash
cd AI_chat/backend
source venv/bin/activate
```

### "ERESOLVE unable to resolve dependency tree"
**Решение**: Используйте флаг:
```bash
npm install --legacy-peer-deps
```

### Порт уже занят
**Решение**: Найдите и завершите процесс:
```bash
lsof -i :3000  # для фронтенда
lsof -i :8000  # для бэкенда
kill -9 <PID>
```
