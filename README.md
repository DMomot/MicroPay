# Coinbase Price Agent

MCP server for fetching historical prices from Coinbase with optional x402 micropayments support.

## Установка

```bash
pip install -e .
```

## Настройка

Установите переменные окружения:
```bash
export COINBASE_API_KEY="ваш-api-key-id"
export COINBASE_PRIVATE_KEY="-----BEGIN EC PRIVATE KEY-----
...ваш-приватный-ключ-в-PEM-формате...
-----END EC PRIVATE KEY-----"
```

## Usage

### MCP Server (Free)
```bash
python -m coinbase_price_agent.server
```

### x402 HTTP Server (Paid)
```bash
python -m coinbase_price_agent.x402_server
# or
coinbase-price-agent-x402
```

The x402 server provides HTTP endpoints with micropayment protection:
- `GET /api/prices?query=Bitcoin price for last year` - $0.01 per query
- Automatic discovery via `/.well-known/x402`
- Compatible with x402 Bazaar marketplace

## API Keys Setup

### Coinbase API Keys
1. Register at [Coinbase Developer Platform](https://cloud.coinbase.com/access/api)
2. Create new API key
3. Download key file (contains `id` and `privateKey` in PEM format)
4. Use:
   - **id** → COINBASE_API_KEY
   - **privateKey** → COINBASE_PRIVATE_KEY

### x402 Configuration (Optional)
For micropayment functionality, also set:
```bash
export X402_WALLET_ADDRESS="your-wallet-address"
export X402_NETWORK="base"  # or "base-sepolia" for testnet
export X402_PRICE="0.01"    # Price in USD per query
export CDP_API_KEY_ID="your-cdp-key-id"
export CDP_API_KEY_SECRET="your-cdp-secret"
```

## Доступные инструменты

### query_prices (новый!)

Получает исторические данные по текстовому запросу на естественном языке.

Параметры:
- `query` (обязательный): Текстовый запрос

Примеры запросов:
- "Покажи цены BTC за последнюю неделю"
- "Исторические данные ETH за месяц"
- "Цены COIN50 с 2024-01-01 по 2024-01-31"
- "Почасовые данные SOL за вчера"

### get_historical_prices

Получает исторические данные о ценах для указанного индекса (прямой API запрос).

Параметры:
- `index` (обязательный): Название индекса (например, "COIN50")
- `granularity`: Временной интервал ("ONE_DAY" или "ONE_HOUR")
- `start` (обязательный): Начальная дата в формате ISO 8601
- `end`: Конечная дата в формате ISO 8601

Пример запроса:
```json
{
  "index": "COIN50",
  "granularity": "ONE_DAY", 
  "start": "2024-01-01T00:00:00Z",
  "end": "2024-01-31T00:00:00Z"
}
```
