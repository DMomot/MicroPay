FROM python:3.11-slim

WORKDIR /app

# Копируем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY x402_hello_agent.py .
COPY .env .

# Экспонируем порт
EXPOSE 8001

# Запускаем агента
CMD ["python", "x402_hello_agent.py"]
