# Railway Deployment - 3 Separate Projects

This repository contains 3 independent projects that should be deployed separately on Railway.

## 📦 Projects Structure

```
price_agent/                    # 🏠 Root: Coinbase Price Agent
├── railway.json               # Railway config for price agent
├── DEPLOY.md                  # Deploy instructions
│
├── AI_chat/                   # 🤖 AI Chat Project
│   ├── frontend/              # React TypeScript frontend
│   │   ├── railway.json       # Railway config for frontend
│   │   └── DEPLOY.md          # Deploy instructions
│   │
│   └── backend/               # Python FastAPI backend  
│       ├── railway.json       # Railway config for backend
│       └── DEPLOY.md          # Deploy instructions
│
└── coinbase_price_agent/      # Source code for price agent
```

## 🚀 3 Separate Deployments

### 1. AI Chat Frontend
**Location**: `AI_chat/frontend/`
```bash
cd AI_chat/frontend
railway create ai-chat-frontend
railway up
```
**URL**: `https://ai-chat-frontend-production.up.railway.app`

### 2. AI Chat Backend  
**Location**: `AI_chat/backend/`
```bash
cd AI_chat/backend
railway create ai-chat-backend
railway up
```
**URL**: `https://ai-chat-backend-production.up.railway.app`

### 3. Coinbase Price Agent
**Location**: `price_agent/` (root)
```bash
# In root directory
railway create coinbase-price-agent
railway up
```
**URL**: `https://coinbase-price-agent-production.up.railway.app`

## 🔄 Auto-Deploy Setup

Each folder has its own `railway.json` that will automatically deploy when that specific folder is updated:

- Changes in `AI_chat/frontend/` → redeploys frontend only
- Changes in `AI_chat/backend/` → redeploys backend only  
- Changes in `price_agent/` root → redeploys price agent only

## 🔑 Environment Variables

Each project needs different API keys:

### AI Chat Frontend
- `REACT_APP_API_URL` - Backend URL
- `PORT=3000`

### AI Chat Backend
- `GEMINI_API_KEY` - Google AI key
- `CORS_ORIGINS` - Frontend URL
- `PORT=8000`

### Price Agent
- `COINBASE_API_KEY` - Coinbase key
- `COINBASE_PRIVATE_KEY` - PEM private key
- `X402_WALLET_ADDRESS` - Wallet for payments
- `CDP_API_KEY_ID` & `CDP_API_KEY_SECRET` - CDP keys
- `PORT=8080`

## 🌐 Final URLs

After deployment:
- **AI Chat**: `https://ai-chat-frontend-production.up.railway.app`
- **Chat API**: `https://ai-chat-backend-production.up.railway.app`  
- **Price Agent**: `https://coinbase-price-agent-production.up.railway.app`

Each project runs independently with separate databases, logs, and scaling.