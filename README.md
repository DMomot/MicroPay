# Coinbase Price Agent

MCP server for fetching historical cryptocurrency prices from Coinbase with optional x402 micropayments support.

## Installation

```bash
pip install -e .
```

## Setup

Set environment variables:
```bash
export COINBASE_API_KEY="your-api-key-id"
export COINBASE_PRIVATE_KEY="-----BEGIN EC PRIVATE KEY-----
...your-private-key-in-PEM-format...
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

## Available Tools

### query_prices

Get historical price data using natural language text queries.

Parameters:
- `query` (required): Text query in natural language

Example queries:
- "Bitcoin price for last year"
- "ETH prices for last month"
- "Show me COIN50 data from 2024-01-01 to 2024-01-31"
- "SOL hourly data for last week"
- "Покажи цены BTC за последнюю неделю" (Russian supported)

### get_historical_prices

Get historical price data for specified cryptocurrency (direct API call).

Parameters:
- `index` (required): Cryptocurrency symbol (e.g., "BTC", "ETH", "SOL")
- `granularity`: Time interval ("ONE_DAY" or "ONE_HOUR")
- `start` (required): Start date in ISO 8601 format
- `end`: End date in ISO 8601 format (optional)

Example request:
```json
{
  "index": "BTC",
  "granularity": "ONE_DAY", 
  "start": "2024-01-01T00:00:00Z",
  "end": "2024-01-31T00:00:00Z"
}
```

## Features

- 🤖 **MCP Integration** - Works with AI assistants (Claude, ChatGPT, etc.)
- 💰 **x402 Micropayments** - Monetize your data with crypto payments
- 🌍 **Multi-language** - Supports English and Russian queries
- 📊 **Real-time Data** - Live price data from Coinbase Pro
- ⚡ **Fast API** - REST endpoints with payment protection
- 🔍 **Smart Parsing** - Natural language to API parameters
- 📈 **Multiple Timeframes** - Hourly and daily data
- 🚀 **Bazaar Ready** - Auto-discovery for x402 marketplace

## Supported Cryptocurrencies

BTC, ETH, SOL, DOGE, ADA, DOT, LINK, UNI, AAVE, COIN50
