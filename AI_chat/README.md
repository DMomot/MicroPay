# MicroPay AI Chat Interface

AI-интерфейс для MicroPay платежной системы на основе Google Gemini. Позволяет пользователям взаимодействовать с CCTP платежами через естественный язык.

## Структура проекта

```
├── backend/          # FastAPI сервер
│   ├── main.py       # Основной файл API
│   ├── requirements.txt
│   └── README.md
├── frontend/         # React приложение
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
└── README.md
```

## Быстрый запуск

### Backend

1. Перейдите в папку backend:
```bash
cd backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp ../.env.example ../.env
# Отредактируйте .env файл и добавьте свой API ключ Gemini
```

5. Запустите сервер:
```bash
python main.py
```

Backend будет доступен на http://localhost:8000

### Frontend

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите приложение:
```bash
npm start
```

Frontend будет доступен на http://localhost:3000

## Технологии

- **Backend**: FastAPI, Google Generative AI, Python
- **Frontend**: React, TypeScript, CSS3
- **API**: Gemini Pro

## Возможности

✅ Современный адаптивный UI  
✅ Реального времени чат с AI  
✅ TypeScript для типизации  
✅ CORS настроен для разработки  
✅ Индикатор печати  
✅ Обработка ошибок  
✅ Автоскролл сообщений