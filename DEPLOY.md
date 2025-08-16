# Coinbase Price Agent - Railway Deploy

Deploy this price agent with x402 micropayments as a separate Railway project.

## 🚀 Quick Deploy

```bash
# In this directory (price_agent/)
railway login
railway create coinbase-price-agent
railway up
```

## 🔑 Environment Variables

Set in Railway dashboard:

```
COINBASE_API_KEY=your-coinbase-api-key-id
COINBASE_PRIVATE_KEY=your-pem-private-key
X402_WALLET_ADDRESS=your-wallet-address
X402_NETWORK=base
X402_PRICE=0.01
CDP_API_KEY_ID=your-cdp-key-id
CDP_API_KEY_SECRET=your-cdp-secret
PORT=8080
FORCE_HTTPS=true
```

## 🌐 Expected URL

`https://coinbase-price-agent-production.up.railway.app`

## 🧪 Testing

```bash
# Health check
curl https://coinbase-price-agent-production.up.railway.app/health

# Price query (requires x402 payment)
curl "https://coinbase-price-agent-production.up.railway.app/api/prices?query=Bitcoin price for last week"

# x402 discovery
curl https://coinbase-price-agent-production.up.railway.app/.well-known/x402
```

## 📱 Features

- Historical cryptocurrency prices
- x402 micropayments ($0.01 per query)
- Natural language query processing
- Bazaar marketplace integration
- MCP protocol support
