#!/bin/bash

echo "🔍 ScoutPay Finder - Quick Scan"
echo "================================"

# Проверяем зависимости
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен"
    exit 1
fi

# Устанавливаем зависимости если нужно
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "📦 Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Запускаем сканирование
echo "🚀 Запускаем Bazaar Scout..."
python bazaar_scout.py

echo ""
echo "✅ Сканирование завершено!"
echo "📄 Результаты сохранены в bazaar_agents.json"
