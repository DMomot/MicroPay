# 🚀 CCTP Facilitator API

Python API сервис для выполнения CCTP transfers через EIP3009 подписи.

## 📋 Функциональность

- **Принимает EIP3009 подписи** от фронтенда
- **Выполняет transferAndBurn** через наш контракт
- **Поддерживает BASE Sepolia и Mainnet**
- **Rate limiting** и безопасность
- **Автоматическое извлечение destination** из nonce

## 🛠 Установка

1. **Создать виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

2. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настроить переменные окружения:**
   ```bash
   # Скопировать шаблон
   cp env.template .env
   
   # Отредактировать .env файл с вашими настройками:
   PRIVATE_KEY=your_private_key_without_0x
   BASE_SEPOLIA_RPC=https://sepolia.base.org
   ```

## 🚀 Запуск

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints

### GET /
Информация о сервисе

### GET /health
Health check

### POST /transfer
Выполнить transferAndBurn с явными destination параметрами

**Request:**
```json
{
  "signature": {
    "from": "0x...",
    "to": "0x...",
    "amount": "1000000",
    "validAfter": 0,
    "validBefore": 1692345600,
    "nonce": "0x...",
    "v": 27,
    "r": "0x...",
    "s": "0x..."
  },
  "destination_domain": 0,
  "destination_address": "0x...",
  "network": "sepolia"
}
```

### POST /transfer-from-nonce
Выполнить transferAndBurnFromNonce (destination из nonce)

**Request:**
```json
{
  "signature": {
    "from": "0x...",
    "to": "0x...",
    "amount": "1000000",
    "validAfter": 0,
    "validBefore": 1692345600,
    "nonce": "0x...",
    "v": 27,
    "r": "0x...",
    "s": "0x..."
  },
  "network": "sepolia"
}
```

### GET /extract-destination/{nonce}
Извлечь destination информацию из nonce

## 🌐 Поддерживаемые сети

### BASE Sepolia (Testnet)
- **Chain ID:** 84532
- **RPC:** https://sepolia.base.org
- **Contract:** `0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c`

### BASE Mainnet
- **Chain ID:** 8453
- **RPC:** https://mainnet.base.org
- **Contract:** (будет задеплоен позже)

## 🔧 Конфигурация

Создайте `.env` файл:
```env
PRIVATE_KEY=your_private_key_without_0x
BASE_SEPOLIA_RPC=https://sepolia.base.org
BASE_MAINNET_RPC=https://mainnet.base.org
CCTP_CONTRACT_MAINNET=your_mainnet_contract_address
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Тестирование

```bash
# Запустить сервер
uvicorn main:app --reload

# Тест health check
curl http://localhost:8000/health

# Тест extract destination
curl http://localhost:8000/extract-destination/0x00000001742d35cc6634c0532925a3b8d5c9c5e3fbe5e1d40000000068a17cc2
```

## 🔒 Безопасность

- **Rate limiting:** 10 запросов в минуту на IP
- **CORS:** Настроен для всех доменов (в продакшене ограничить)
- **Валидация:** Pydantic модели для всех входных данных
- **Логирование:** Все операции логируются

## 📊 Мониторинг

- **Логи:** Используется loguru для структурированного логирования
- **Health check:** `/health` endpoint для мониторинга
- **Metrics:** Можно добавить Prometheus metrics

## 🚀 Деплой

### Docker (рекомендуется)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway/Heroku
1. Добавить `Procfile`: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Установить переменные окружения
3. Задеплоить

## 🔄 Интеграция с фронтендом

```javascript
// Пример вызова API
const response = await fetch('http://localhost:8000/transfer-from-nonce', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    signature: {
      from: userAddress,
      to: contractAddress,
      amount: "1000000", // 1 USDC (6 decimals)
      validAfter: 0,
      validBefore: Math.floor(Date.now() / 1000) + 3600,
      nonce: encodedNonce,
      v: signature.v,
      r: signature.r,
      s: signature.s
    },
    network: "sepolia"
  })
});

const result = await response.json();
console.log('Transaction hash:', result.tx_hash);
```
