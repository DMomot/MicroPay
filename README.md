# 💳 MicroPay - Cross-Chain USDC Payment System

**MicroPay** - это современная платежная система для мгновенных cross-chain USDC переводов, построенная на технологии Circle's CCTP (Cross-Chain Transfer Protocol).

## 🌟 Особенности

- **⚡ Мгновенные переводы** - Cross-chain USDC трансферы за секунды
- **🔐 EIP3009 подписи** - Безопасные gasless транзакции для пользователей
- **🌐 Multi-chain** - Поддержка Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche
- **🤖 AI Interface** - Естественный язык для управления платежами
- **🛡️ Enterprise Security** - Rate limiting, валидация подписей, защита от атак

## 🏗️ Архитектура

```
MicroPay/
├── facilitator/         # 🚀 Основной CCTP API сервис
├── CCTP/               # 📜 Solidity смарт-контракты
├── AI_chat/            # 🤖 AI интерфейс (фронтенд + бэкенд)
└── docs/               # 📚 Документация
```

## 🚀 Компоненты

### 1. **CCTP Facilitator API** (`facilitator/`)
- Python FastAPI сервис
- Обрабатывает EIP3009 подписи
- Выполняет cross-chain burns и mints
- Автоматическое извлечение destination из nonce

### 2. **Smart Contracts** (`CCTP/`)
- Solidity контракты для CCTP интеграции
- EIP3009 поддержка для gasless транзакций
- Deployment скрипты для всех сетей

### 3. **AI Chat Interface** (`AI_chat/`)
- React фронтенд с MetaMask интеграцией
- FastAPI бэкенд с Google Gemini
- Естественный язык для платежных команд

## 💰 Поддерживаемые сети

| Сеть | Domain ID | Статус |
|------|-----------|--------|
| Ethereum | 0 | ✅ |
| Avalanche | 1 | ✅ |
| Optimism | 2 | ✅ |
| Arbitrum | 3 | ✅ |
| Base | 6 | ✅ |
| Polygon | 7 | ✅ |

## 🛠️ Быстрый старт

### 1. Запуск Facilitator API
```bash
cd facilitator/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 2. Деплой контрактов
```bash
cd CCTP/
npm install
npx hardhat deploy --network base-sepolia
```

### 3. Запуск AI интерфейса
```bash
# Бэкенд
cd AI_chat/backend/
pip install -r requirements.txt
python main.py

# Фронтенд
cd AI_chat/frontend/
npm install
npm start
```

## 📡 API Endpoints

### POST `/transfer`
Выполняет cross-chain USDC трансфер

```json
{
  "signature": {
    "from": "0x...",
    "to": "0x...",
    "amount": "1000000",
    "validAfter": 0,
    "validBefore": 1234567890,
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

## 🔧 Конфигурация

Создайте `.env` файл:
```env
BASE_SEPOLIA_RPC=https://sepolia.base.org
PRIVATE_KEY=your_facilitator_private_key
PRIVATE_KEY_USER=user_private_key_for_testing
```

## 🚀 Деплой

- **Railway**: Используйте `railway.json` в каждом сервисе
- **Docker**: Dockerfile доступен для каждого компонента
- **Manual**: Следуйте инструкциям в `DEPLOY.md`

## 📚 Документация

- [Быстрый старт](QUICK_START.md)
- [Деплой инструкции](RAILWAY_DEPLOY.md)
- [Facilitator API](facilitator/README.md)
- [Smart Contracts](CCTP/README.md)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

---

**MicroPay** - делаем cross-chain платежи простыми и доступными! 💳✨
