# 🚀 Руководство по развертыванию x402 Hello Agent

## Быстрые варианты (бесплатно)

### 1. 🔧 Ngrok (мгновенно)
```bash
# В первом терминале
python x402_hello_agent.py

# Во втором терминале  
ngrok http 8001
```
**Результат**: Публичный URL типа `https://abc123.ngrok.io`

### 2. ☁️ Railway.app (5 минут)
1. Зайти на https://railway.app
2. Подключить GitHub репозиторий
3. Railway автоматически обнаружит `railway.json`
4. Деплой пройдет автоматически

### 3. ☁️ Render.com (бесплатно)
1. Зайти на https://render.com
2. "New Web Service"
3. Подключить репозиторий
4. Render использует `render.yaml`

### 4. ☁️ Fly.io
```bash
# Установить flyctl
brew install flyctl

# Войти и создать проект
fly auth login
fly launch

# Деплой
fly deploy
```

### 5. 🐳 Docker + любой хостинг
```bash
# Собрать образ
docker build -t x402-hello-agent .

# Запустить локально
docker run -p 8001:8001 x402-hello-agent

# Загрузить на DockerHub/GitHub Registry
docker tag x402-hello-agent your-username/x402-hello-agent
docker push your-username/x402-hello-agent
```

## VPS варианты (платно, но надежно)

### 6. 🖥️ DigitalOcean/Hetzner/Linode
```bash
# На сервере
git clone your-repo
cd backend
pip install -r requirements.txt
python x402_hello_agent.py

# Для постоянной работы
sudo apt install supervisor
# Настроить supervisor config
```

### 7. 🌐 Cloudflare Workers (Python)
```bash
pip install cloudflare-workers
# Конвертировать FastAPI в Workers формат
```

## Что происходит после деплоя

1. **Агент доступен публично** 
2. **x402 Bazaar автоматически обнаружит** ваш сервис
3. **Появится в листинге** через discovery endpoint
4. **Пользователи смогут платить** и использовать

## Пример для Railway

```bash
# 1. Создать GitHub репозиторий
git init
git add .
git commit -m "x402 Hello Agent"
git remote add origin https://github.com/username/x402-agent
git push -u origin main

# 2. На Railway.app:
# - Connect GitHub
# - Select repository  
# - Deploy автоматически
```

## Переменные окружения

Не забудьте установить:
- `X402_WALLET_ADDRESS` - адрес для получения платежей
- `PORT` - если хостинг требует (Railway/Render сами установят)

## После деплоя

Проверьте эндпоинты:
- `https://your-domain.com/` - информация
- `https://your-domain.com/.well-known/x402` - discovery
- `https://your-domain.com/api/hello` - платный эндпоинт
- `https://your-domain.com/health` - health check

## Мониторинг попадания в Bazaar

После деплоя проверьте:
```bash
curl https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources
# Ищите ваш домен в списке
```

## Рекомендуемый порядок

1. **Начать с Ngrok** - для тестирования
2. **Перейти на Railway/Render** - для продакшена  
3. **Настроить мониторинг** - логи и метрики
4. **Добавить реальную валидацию** платежей
