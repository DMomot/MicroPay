# AI Chat Backend - Railway Deploy

Deploy this Python FastAPI backend as a separate Railway project.

## 🚀 Quick Deploy

```bash
# In this directory (AI_chat/backend/)
railway login
railway create ai-chat-backend
railway up
```

## 🔑 Environment Variables

Set in Railway dashboard:

```
GEMINI_API_KEY=your-gemini-api-key-here
CORS_ORIGINS=https://your-frontend-url.up.railway.app
PORT=8000
FORCE_HTTPS=true
```

## 🌐 Expected URL

`https://ai-chat-backend-production.up.railway.app`

## 🧪 Testing

```bash
# Health check
curl https://ai-chat-backend-production.up.railway.app/

# Chat test
curl -X POST https://ai-chat-backend-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 📱 Features

- FastAPI backend
- Gemini AI integration
- CORS configured for frontend
- Health check endpoint
