# Blockchain Analyst Agent - Deployment Guide

## Quick Deploy to Railway

1. **Подготовка**
   ```bash
   cd ScoutPay/agent_analyst
   ```

2. **Railway Deploy**
   ```bash
   railway login
   railway link  # или railway init для нового проекта
   railway up
   ```

3. **Настройка переменных окружения в Railway**
   ```bash
   railway variables set GEMINI_API_KEY=your_gemini_key_here
   railway variables set CDP_API_KEY_ID=your_cdp_key_id
   railway variables set CDP_API_KEY_SECRET=your_cdp_secret
   railway variables set X402_WALLET_ADDRESS=0xce465C087305314F8f0eaD5A450898f19eFD0E03
   railway variables set X402_NETWORK=base
   railway variables set X402_PRICE=0.05
   ```

## Тестирование

После деплоя проверьте:

1. **Health Check**
   ```bash
   curl https://your-app.up.railway.app/health
   ```

2. **Agent Info**
   ```bash
   curl https://your-app.up.railway.app/
   ```

3. **x402 Discovery**
   ```bash
   curl https://your-app.up.railway.app/.well-known/x402
   ```

4. **Тестовый анализ** (требует x402 платеж)
   ```bash
   curl "https://your-app.up.railway.app/api/analyze?query=Analyze Bitcoin price trends"
   ```

## Регистрация в Bazaar

После успешного деплоя агент автоматически будет доступен для обнаружения через endpoint `/.well-known/x402`.

## Мониторинг

- Логи: `railway logs`
- Метрики: Railway Dashboard
- Health: `/health` endpoint

## Troubleshooting

- Убедитесь что все переменные окружения установлены
- Проверьте что GEMINI_API_KEY валидный
- Убедитесь что CDP ключи корректные для x402 платежей
