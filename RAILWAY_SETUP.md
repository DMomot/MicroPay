# Railway Deployment Setup

## 🚂 Multiple Deployments from One Repository

### Deployment Options

1. **Demo Server** (Free) - `/demo`
   - Endpoint: `your-demo.railway.app`
   - Features: Basic price fetching without payments
   - Cost: Free tier

2. **x402 Server** (Paid) - `/x402`  
   - Endpoint: `your-x402.railway.app`
   - Features: Full x402 micropayments + Bazaar integration
   - Cost: Production tier

3. **MCP Server** (Development) - `/mcp`
   - Endpoint: `your-mcp.railway.app` 
   - Features: MCP protocol for AI assistants
   - Cost: Development tier

## 📋 Setup Instructions

### Step 1: Create Railway Projects

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create projects
railway create coinbase-demo
railway create coinbase-x402  
railway create coinbase-mcp
```

### Step 2: Deploy Each Service

#### Demo Server
```bash
cd /path/to/project
railway link coinbase-demo
railway up --service demo
```

#### x402 Server  
```bash
railway link coinbase-x402
railway up --service x402
```

#### MCP Server
```bash
railway link coinbase-mcp  
railway up --service mcp
```

### Step 3: Set Environment Variables

#### For Demo Server:
```bash
railway variables set COINBASE_API_KEY="your-key"
railway variables set COINBASE_PRIVATE_KEY="your-private-key"
```

#### For x402 Server:
```bash
railway variables set COINBASE_API_KEY="your-key"
railway variables set COINBASE_PRIVATE_KEY="your-private-key" 
railway variables set X402_WALLET_ADDRESS="your-wallet"
railway variables set X402_NETWORK="base"
railway variables set X402_PRICE="0.01"
railway variables set CDP_API_KEY_ID="your-cdp-id"
railway variables set CDP_API_KEY_SECRET="your-cdp-secret"
```

### Step 4: Custom Domains (Optional)

```bash
# Add custom domains
railway domain add demo.yoursite.com
railway domain add api.yoursite.com  
railway domain add mcp.yoursite.com
```

## 🌐 Expected URLs

- **Demo**: `https://coinbase-demo-production.railway.app`
- **x402**: `https://coinbase-x402-production.railway.app` 
- **MCP**: `https://coinbase-mcp-production.railway.app`

## 🔧 Alternative: Single Project with Multiple Services

```bash
# Create one project with multiple services
railway create coinbase-price-agent

# Add services within the project
railway service create demo
railway service create x402
railway service create mcp
```

Each service will get its own URL:
- `https://demo.coinbase-price-agent.railway.app`
- `https://x402.coinbase-price-agent.railway.app`  
- `https://mcp.coinbase-price-agent.railway.app`

## 💡 Pro Tips

1. **Use different start commands** in Railway dashboard
2. **Set different PORT variables** if needed  
3. **Configure different resource limits** per service
4. **Use Railway's branch deployments** for staging/production
5. **Set up monitoring** for each service separately

## 🚀 Quick Deploy Commands

```bash
# Deploy all services at once
./deploy-all.sh

# Or individually
railway up --detach demo
railway up --detach x402  
railway up --detach mcp
```
