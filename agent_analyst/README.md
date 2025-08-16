# Blockchain Analyst Agent (Gemini Flash 2.0)

Professional blockchain analyst agent powered by Google's Gemini Flash 2.0 that provides comprehensive market analysis, trend insights, and investment recommendations using x402 micropayments.

## Features

- **Comprehensive Analysis**: Deep blockchain and cryptocurrency market analysis
- **Multi-Source Data**: Automatically finds and queries relevant data agents
- **Professional Insights**: Expert-level analysis with risk assessments
- **x402 Integration**: Micropayment system for accessing premium analysis
- **Natural Language**: Query using plain English

## Specialties

- Cryptocurrency market analysis
- DeFi protocol evaluation
- NFT market trends  
- Technical analysis
- Risk assessment
- Investment recommendations
- On-chain data interpretation
- Regulatory impact analysis

## API Endpoints

### GET /api/analyze
**Protected by x402 micropayments ($0.05 per analysis)**

Query the analyst using natural language:
```
GET /api/analyze?query=Analyze Bitcoin's recent price movement and predict next week's trend
```

### GET /
Agent information and capabilities

### GET /.well-known/x402
x402 discovery endpoint for Bazaar registration

### GET /health
Health check endpoint

## Environment Variables

Required:
- `GEMINI_API_KEY` - Google Gemini API key for analysis generation
- `CDP_API_KEY_ID` - Coinbase Developer Platform API key ID
- `CDP_API_KEY_SECRET` - Coinbase Developer Platform API secret

Optional:
- `X402_WALLET_ADDRESS` - Wallet address for receiving payments
- `X402_NETWORK` - Network for payments (default: base)
- `X402_PRICE` - Price per analysis (default: 0.05)
- `PORT` - Server port (default: 8080)

## Example Queries

- "Analyze Bitcoin's recent price movement and predict next week's trend"
- "What are the best DeFi yield farming opportunities right now?"
- "Evaluate the risk of investing in Ethereum before the next upgrade"
- "Compare the performance of top 10 cryptocurrencies this month"
- "Should I invest in NFTs right now? What are the risks?"

## Deployment

### Railway
```bash
railway login
railway link
railway up
```

### Docker
```bash
docker build -t blockchain-analyst .
docker run -p 8080:8080 blockchain-analyst
```

## Development

```bash
pip install -e .
python -m blockchain_analyst.x402_server
```

## Author

Dmitrii Momot
