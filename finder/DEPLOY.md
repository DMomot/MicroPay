# ScoutPay AI Agent Finder - Railway Deploy

Deploy this Python FastAPI backend to Railway for production use.

## 🚀 Quick Deploy

### Option 1: Railway CLI
```bash
# In this directory (ScoutPay/finder/)
railway login
railway create scoutpay-agent-finder
railway up
```

### Option 2: GitHub Integration
1. Push code to GitHub repository
2. Connect Railway to your GitHub repo
3. Railway will auto-deploy on commits

## 🔑 Environment Variables

Set these in Railway dashboard:

```
GEMINI_API_KEY=your-gemini-api-key-here
AGENTS_REFRESH_INTERVAL_MINUTES=60
PORT=8000
```

## 🌐 Expected URLs

- **Production URL**: `https://scoutpay-agent-finder-production.up.railway.app`
- **API Docs**: `https://scoutpay-agent-finder-production.up.railway.app/docs`
- **Health Check**: `https://scoutpay-agent-finder-production.up.railway.app/health`

## 🧪 Testing

```bash
# Health check
curl https://scoutpay-agent-finder-production.up.railway.app/health

# Agent stats
curl https://scoutpay-agent-finder-production.up.railway.app/agents/stats

# Search test
curl -X POST https://scoutpay-agent-finder-production.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{"prompt": "BTC price", "min_rating": 0.5}'
```

## 📱 API Endpoints

- `POST /search` - Search agents by prompt with Gemini AI
- `GET /health` - API health status  
- `GET /agents/stats` - Agent statistics (total vs. with descriptions)

## ⚙️ Features

- ✅ FastAPI backend with auto-reload
- ✅ Gemini 2.0 Flash AI integration  
- ✅ x402 Bazaar agent discovery
- ✅ Smart caching (60min default refresh)
- ✅ AI reasoning output in logs
- ✅ CORS enabled for frontend integration
- ✅ Health check endpoint for monitoring

## 🔧 Configuration

The service automatically:
- Loads agents from x402 Bazaar on startup
- Caches agent list for performance  
- Refreshes cache every AGENTS_REFRESH_INTERVAL_MINUTES
- Uses Gemini for semantic agent scoring
- Outputs AI reasoning for transparency

## 📊 Monitoring

Railway provides:
- Automatic health checks via `/health`
- Real-time logs with AI reasoning
- Resource usage metrics
- Automatic restarts on failure
