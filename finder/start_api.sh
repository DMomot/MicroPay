#!/bin/bash

echo "🤖 ScoutPay AI Agent Finder"
echo "============================"

# Проверяем зависимости
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен"
    exit 1
fi

# Создаем виртуальное окружение если нужно
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "📦 Активируем виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Запускаем AI Agent Finder API..."
echo "📡 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🎨 Demo: откройте demo.html в браузере"
echo ""
echo "Примеры запросов:"
echo "- найти информацию в интернете"
echo "- узнать погоду"
echo "- цены на акции"
echo "- генерация видео"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""

# Запускаем API сервер
python api_server.py
