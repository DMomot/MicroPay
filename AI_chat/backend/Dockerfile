FROM python:3.11-slim

WORKDIR /app

# Копируем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY main.py .
COPY prompts/ ./prompts/

# Экспонируем порт
EXPOSE 8000

# Запускаем сервер
CMD ["python", "main.py"]
