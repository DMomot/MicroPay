# AI Chat Frontend - Railway Deploy

Deploy this React frontend as a separate Railway project.

## 🚀 Quick Deploy

```bash
# In this directory (AI_chat/frontend/)
railway login
railway create ai-chat-frontend
railway up
```

## 🔑 Environment Variables

Set in Railway dashboard:

```
REACT_APP_API_URL=https://your-backend-url.up.railway.app
PORT=3000
FORCE_HTTPS=true
```

## 🌐 Expected URL

`https://ai-chat-frontend-production.up.railway.app`

## 🔗 Connect to Backend

After deploying backend, update `REACT_APP_API_URL` to point to your backend URL.

## 📱 Features

- React TypeScript frontend
- AI chat interface
- Responsive design
- Real-time messaging with Gemini AI
