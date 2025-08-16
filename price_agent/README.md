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

### Railway Deployment
Deploy to Railway with Docker:
```bash
railway login
railway create
railway up
```

### Local Development
```bash
python -m coinbase_price_agent.x402_server
```

### Endpoints
- `GET /api/prices?query=Bitcoin price for last year` - $0.01 per query
- `GET /.well-known/x402` - x402 discovery endpoint
- `GET /health` - Health check

## API Keys Setup

### Coinbase API Keys
1. Register at [Coinbase Developer Platform](https://cloud.coinbase.com/access/api)
2. Create new API key
3. Download key file (contains `id` and `privateKey` in PEM format)
4. Use:
   - **id** → COINBASE_API_KEY
   - **privateKey** → COINBASE_PRIVATE_KEY

### x402 Configuration
For micropayment functionality, also set:
```bash
export X402_WALLET_ADDRESS="your-wallet-address"
export X402_NETWORK="base"
export X402_PRICE="0.01"
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

## Features

- 💰 **x402 Micropayments** - Crypto payments for API access
- 🌍 **Multi-language** - English and Russian query support  
- 📊 **Real-time Data** - Live Coinbase price data
- 🔍 **Smart Parsing** - Natural language to API parameters
- 🚀 **Bazaar Ready** - Auto-discovery for x402 marketplace
- 🐳 **Docker Ready** - Easy Railway deployment

## Supported Cryptocurrencies

BTC, ETH, SOL, DOGE, ADA, DOT, LINK, UNI, AAVE, COIN50
